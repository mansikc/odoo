# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class SquareController(http.Controller):

    @http.route(['/payment/square/return'], type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def square_return(self, **post):
        """Return URL for redirect flows (if you implement redirect-based Square checkout).
        For now this is a simple handler that logs and returns a small page.
        """
        _logger.info("Square return called with params: %s", post)
        # TODO: find a transaction using params and mark as done/cancelled
        return request.make_response("Square return received. You can close this window.")

    @http.route(['/payment/square/webhook'], type='json', auth='public', csrf=False, methods=['POST'])
    def square_webhook(self, **kw):
        """Webhook endpoint for Square.
        Square posts JSON. You should validate signatures (X-Square-Signature) for production.
        """
        payload = request.jsonrequest
        headers = request.httprequest.headers
        sig = headers.get('X-Square-Signature') or headers.get('x-square-signature')
        _logger.info("Square webhook received. Signature: %s, payload: %s", sig, payload)

        # Very important: verify the signature in production (Square docs)
        # For this scaffold we simply forward payload to payment.transaction processors if needed.
        try:
            # naive: call a model method to handle notification
            request.env['payment.transaction'].sudo()._square_handle_notification(payload)
        except Exception as e:
            _logger.exception("Error handling Square webhook: %s", e)
            return {'success': False, 'error': str(e)}

        return {'success': True}
