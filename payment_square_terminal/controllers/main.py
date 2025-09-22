# -*- coding: utf-8 -*-
import logging
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

            # TODO: here you actually call Square API (checkout/terminal)
            # For now just simulate success
            # Example: request.env['pos.square.api'].sudo()._send_to_square(order_id, amount, currency)

            return {'status': 'success', 'transaction_id': 'TEST12345'}

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