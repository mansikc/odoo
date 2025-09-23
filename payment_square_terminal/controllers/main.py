# controllers/main.py
import logging
import json
import uuid
import base64
import hmac
import hashlib
import requests

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

SQUARE_API_BASE = "https://connect.squareup.com"  # use sandbox? see note below
SQUARE_API_VERSION = "2025-08-20"  # set an explicit Square-Version header

def _get_square_token():
    return request.env['ir.config_parameter'].sudo().get_param('pos_square.access_token')

def _get_webhook_signature_key():
    return request.env['ir.config_parameter'].sudo().get_param('pos_square.webhook_signature_key')

class PosSquareController(http.Controller):

    @http.route('/pos_square/create_device_code', type='json', auth='user', methods=['POST'])
    def create_device_code(self, **kwargs):
        """
        Create a Device Code (used to pair a Square Terminal). Caller should display `code` to the seller
        and have them enter it on the Square Terminal "Use a device code".
        Request payload: { "location_id": "<location_id>", "name": "Counter 1" }
        """
        token = _get_square_token()
        if not token:
            return {"error": "Square token not configured"}

        location_id = kwargs.get('location_id')
        name = kwargs.get('name', 'Odoo POS')

        url = f"{SQUARE_API_BASE}/v2/devices/codes"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Square-Version": SQUARE_API_VERSION,
        }
        body = {
            "idempotency_key": str(uuid.uuid4()),
            "device_code": {
                "name": name,
                "product_type": "TERMINAL_API",
                "location_id": location_id
            }
        }
        resp = requests.post(url, headers=headers, json=body, timeout=15)
        if resp.status_code >= 400:
            _logger.error("Square create_device_code error: %s", resp.text)
            return {"error": resp.text}
        return resp.json()

    @http.route('/pos_square/create_checkout', type='json', auth='user', methods=['POST'])
    def create_checkout(self, **kwargs):
        """
        Create a Square Terminal Checkout.
        Request payload must include:
          - amount (float or int) (in major units, e.g. 100.50)
          - currency (e.g. "USD" or "INR")
          - device_id (serial/device id of the paired terminal)  OR (device_code) if you want to attempt pairing workflow
          - reference (your pos order name)
        """
        token = _get_square_token()
        if not token:
            return {"error": "Square token not configured"}

        amount = kwargs.get('amount')
        currency = kwargs.get('currency', 'USD')
        device_id = kwargs.get('device_id')
        reference = kwargs.get('reference', 'odoo-pos')
        note = kwargs.get('note', '')

        # convert amount to cents
        try:
            amt_minor = int(round(float(amount) * 100))
        except Exception:
            return {"error": "invalid amount"}

        url = f"{SQUARE_API_BASE}/v2/terminals/checkouts"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Square-Version": SQUARE_API_VERSION,
        }

        body = {
            "idempotency_key": str(uuid.uuid4()),
            "checkout": {
                "amount_money": {
                    "amount": amt_minor,
                    "currency": currency
                },
                "reference_id": reference,
                "note": note,
                # either device_id (serial) OR device options:
                "device_id": device_id,
                # optionally autocomplete: true/false
                "autocomplete": True
            }
        }

        resp = requests.post(url, headers=headers, json=body, timeout=15)
        if resp.status_code >= 400:
            _logger.error("Square create_checkout error: %s", resp.text)
            return {"error": resp.text, "status_code": resp.status_code}
        data = resp.json()
        # Save mapping: you should store checkout id on the pos.order record (example below)
        # request.env['pos.order'].sudo().browse(pos_order_id).write({'square_checkout_id': data['checkout']['id']})
        return data

    @http.route('/pos_square/webhook', type='http', auth='public', csrf=False, methods=['POST'])
    def square_webhook(self, **kwargs):
        """
        Webhook endpoint to receive Square events.
        Validate signature and then process events:
          - device.code.paired  -> get device_id for later checkout requests
          - terminal.checkout.updated -> check status and update order/payment
          - payment.updated/payment.created -> confirm amounts
        See Square docs on how to verify signature.
        """
        raw = request.httprequest.get_data()  # raw bytes
        signature_header = request.httprequest.headers.get('x-square-hmacsha256-signature') or request.httprequest.headers.get('x-square-signature')
        sig_key = _get_webhook_signature_key()
        if not sig_key:
            _logger.error("Square webhook signature key not configured")
            return request.make_response("signature key not configured", status=500)

        # Validate signature (Square verification algorithm: uses signature key, notification_url, and raw body)
        # You can use square.utilities.webhooks_helper.is_valid_webhook_event_signature if using their SDK.
        notification_url = request.httprequest.url  # full URL
        # square expects you to feed raw body and the notification_url and signature key to recreate HMAC.
        try:
            # sig_key provided in Square dashboard is base64-encoded; decode first
            decoded_sig_key = base64.b64decode(sig_key)
        except Exception:
            _logger.exception("Invalid webhook signature key format (not base64?).")
            decoded_sig_key = sig_key.encode('utf-8')

        # Compute HMAC-SHA256 over (notification_url + raw_body) and base64 encode result
        mac = hmac.new(decoded_sig_key, (notification_url.encode('utf-8') + raw), hashlib.sha256)
        expected = base64.b64encode(mac.digest()).decode()

        if not signature_header or expected != signature_header:
            _logger.warning("Invalid Square webhook signature. expected=%s header=%s", expected[:8], signature_header[:8] if signature_header else None)
            return request.make_response("Forbidden", status=403)

        try:
            payload = json.loads(raw.decode('utf-8'))
        except Exception:
            _logger.exception("Failed to parse Square webhook JSON")
            return request.make_response("Bad payload", status=400)

        # Process common events
        event_type = payload.get('type') or payload.get('event_type')  # event shape can vary by API version
        _logger.info("Square webhook received: %s", event_type)

        # Example handling:
        if event_type == "device.code.paired":
            device = payload.get('data', {}).get('object', {})
            # device contains device.id & device.device_id; save to your pos device config
            # e.g. search by reference you used in create_device_code and store device_id.
            _logger.info("Device paired: %s", device)
        elif event_type == "terminal.checkout.updated":
            checkout = payload.get('data', {}).get('object', {}).get('checkout', {})
            checkout_id = checkout.get('id')
            status = checkout.get('status')
            # Use checkout.reference_id to find your pos.order and mark payment
            reference = checkout.get('reference_id')
            _logger.info("Checkout %s status=%s ref=%s", checkout_id, status, reference)
            # Example: when COMPLETED -> create pos.payment and validate order
            if status == "COMPLETED":
                # locate pos order by your saved reference (customize to your implementation!)
                orders = request.env['pos.order'].sudo().search([('name','=', reference)], limit=1)
                if orders:
                    # create a pos.payment record if needed, or call existing Odoo flows to validate
                    # (this part depends on your implementation)
                    _logger.info("Found Odoo pos.order %s for checkout %s", orders.name, checkout_id)
        # Always return 200 OK quickly
        return request.make_response("OK", status=200)
