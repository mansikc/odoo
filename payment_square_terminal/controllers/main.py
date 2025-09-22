# -*- coding: utf-8 -*-
import logging
import requests
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class SquareController(http.Controller):

    @http.route('/pos/square/payment', type='json', auth='public', csrf=False)
    def pos_square_payment(self, **kwargs):
        """
        Called from POS frontend when user selects Square payment.
        This should trigger a Square Checkout or Terminal API call.
        """
        try:
            order_id = kwargs.get('order_id')
            amount = kwargs.get('amount')
            currency = kwargs.get('currency')
            customer = kwargs.get('customer')
            lines = kwargs.get('lines')

            _logger.info("POS Square payment request: order=%s, amount=%s %s, customer=%s",
                         order_id, amount, currency, customer)

            access_token = "EAAAl2kUOJa8Dmmj7aREZ-Wvixdow4vcZ2vUX7k5BvtZ56nrnws7QOAM7psZK8dO"
            location_id = "LAP0GP4BXQHRE"
            device_id = "NG6YH1F1HM1N"

            # Square API endpoint for terminal checkout
            api_url = "https://connect.squareup.com/v2/terminals/checkouts"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            checkout_body = {
                "idempotency_key": "odoo-" + str(order_id),   # Unique for every transaction
                "checkout": {
                    "amount_money": {
                        "amount": int(amount),
                        "currency": currency
                    },
                    "reference_id": str(order_id),
                    "device_options": {
                        "device_id": device_id
                    }
                }
            }

            resp = requests.post(api_url, headers=headers, json=checkout_body, timeout=15)
            resp.raise_for_status()
            resp_data = resp.json()

            checkout_id = resp_data['checkout']['id']
            status = resp_data['checkout']['status']
            qr_code = resp_data['checkout'].get('qr_code', None)
            # You can now pass qr_code to frontend if needed, or handle based on status

            return {
                'status': status,
                'transaction_id': checkout_id,
                'qr_code': qr_code,
                'raw': resp_data
            }
        except Exception as e:
            _logger.exception("Error while creating Square payment")
            return {'status': 'error', 'message': str(e)}

    @http.route('/pos/square/cancel', type='json', auth='public', csrf=False)
    def pos_square_cancel(self, **kwargs):
        """
        Cancel a pending payment.
        """
        order_id = kwargs.get('order_id')
        _logger.info("Square payment cancel called for order %s", order_id)
        # TODO: call Square cancel API if needed
        return {'status': 'cancelled'}

    @http.route(['/payment/square/return'], type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def square_return(self, **post):
        """Return URL for redirect-based checkout (optional)."""
        _logger.info("Square return called with params: %s", post)
        return request.make_response("Square return received. You can close this window.")

    @http.route(['/payment/square/webhook'], type='json', auth='public', csrf=False, methods=['POST'])
    def square_webhook(self, **kw):
        """Webhook endpoint for Square notifications."""
        payload = request.jsonrequest
        headers = request.httprequest.headers
        sig = headers.get('X-Square-Signature') or headers.get('x-square-signature')
        _logger.info("Square webhook received. Signature: %s, payload: %s", sig, payload)

        try:
            request.env['payment.transaction'].sudo()._square_handle_notification(payload)
        except Exception as e:
            _logger.exception("Error handling Square webhook: %s", e)
            return {'success': False, 'error': str(e)}

        return {'success': True}
