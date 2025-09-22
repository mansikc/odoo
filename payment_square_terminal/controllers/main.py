# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class SquareController(http.Controller):

    @http.route('/pos/square/payment', type='json', auth='public', methods=['POST'])
    def square_payment(self, **kwargs):
        """Send payment request from POS to Square Terminal API."""
        try:
            provider = request.env['payment.provider'].sudo().search([('provider', '=', 'square')], limit=1)
            if not provider:
                return {"status": "error", "message": "Square provider not configured"}

            order_id = kwargs.get('order_id')
            amount = kwargs.get('amount')
            currency = kwargs.get('currency')

            # Build payload for Square Terminal API
            payload = {
                "idempotency_key": order_id,
                "checkout": {
                    "amount_money": {
                        "amount": int(float(amount) * 100),  # cents
                        "currency": currency,
                    },
                    "device_options": {
                        "device_id": provider.square_device_id,
                    },
                },
            }

            headers = {
                "Square-Version": "2025-01-22",
                "Authorization": f"Bearer {provider.square_access_token}",
                "Content-Type": "application/json",
            }

            url = "https://connect.squareupsandbox.com/v2/terminals/checkouts" if provider.square_sandbox \
                else "https://connect.squareup.com/v2/terminals/checkouts"

            response = request.post(url, json=payload, headers=headers)
            result = response.json()

            if response.status_code == 200 and "checkout" in result:
                _logger.info("Square payment success: %s", result)
                return {"status": "success", "transaction": result}
            else:
                _logger.error("Square payment error: %s", result)
                return {"status": "error", "message": result.get("errors", "Unknown error")}

        except Exception as e:
            _logger.exception("Unexpected error in Square payment")
            return {"status": "error", "message": str(e)}

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