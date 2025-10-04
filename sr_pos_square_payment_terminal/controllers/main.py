import hmac
import hashlib
import base64
from odoo import http
from odoo.http import request
import json

SIGNATURE_KEY = "mrPot6mHZfCWldDp1CbePQ"  # get from Square Dashboard
NOTIFICATION_URL = "https://8c901e3c40d3.ngrok-free.app/square/webhook"  # must exactly match the URL registered in Square

class SquareWebhookController(http.Controller):

    @http.route('/square/webhook', type='http', auth='public', csrf=False, methods=['POST'])
    def square_webhook(self, **kwargs):
        # 1. Get raw request body (bytes)
        raw_body = request.httprequest.get_data()  # bytes
        print("++++++raw_body++++++++++", raw_body)
        # 2. Get Square signature header
        signature_header = request.httprequest.headers.get('x-square-hmacsha256-signature', '')

        # 3. Verify signature
        # if not self._is_valid_signature(NOTIFICATION_URL, raw_body, signature_header, SIGNATURE_KEY):
        #     return request.make_response('Invalid signature', headers=[('Content-Type','text/plain')], status=401)

        # 4. Parse JSON manually
        # try:
        payload = json.loads(raw_body.decode('utf-8'))
        terminal_status = payload['data']['object']['checkout']['status']
        print("++++++++terminal_status++++++++++++", terminal_status)
        # except Exception as e:
        #     return request.make_response('Invalid JSON', headers=[('Content-Type','text/plain')], status=400)

        # 5. Log or process the event
        request.env['ir.logging'].sudo().create({
            'name': 'Square Webhook',
            'type': 'server',
            'level': 'info',
            'message': str(payload),
            'path': 'square.webhook',
            'func': 'square_webhook',
            'line': '0',
        })

        # 6. Respond 200 OK
        return request.make_response(json.dumps({"success": True}), headers=[('Content-Type','application/json')])

    def _is_valid_signature(self, notification_url, raw_body, signature_header, signature_key):
        # HMAC-SHA256 verification
        message = notification_url.encode('utf-8') + raw_body
        digest = hmac.new(signature_key.encode('utf-8'), message, hashlib.sha256).digest()
        computed_signature = base64.b64encode(digest).decode()
        return hmac.compare_digest(computed_signature, signature_header)