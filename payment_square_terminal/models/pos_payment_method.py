import uuid
import requests
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    use_square_terminal = fields.Boolean(string="Use Square Terminal")
    square_access_token = fields.Char(string="Square Access Token")
    square_location_id = fields.Char(string="Square Location ID")
    square_device_code = fields.Char(string="Square Device Code")

    @api.model
    def square_create_checkout(self, payment_method_id, payment_data):
        pm = self.browse(payment_method_id)
        access_token = pm.square_access_token
        location_id = pm.square_location_id
        device_code = pm.square_device_code

        url = "https://connect.squareup.com/v2/terminals/checkouts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        idempotency_key = str(uuid.uuid4())

        payload = {
            "idempotency_key": idempotency_key,
            "checkout": {
                "amount_money": {
                    "amount": int(payment_data['amount'] * 100),
                    "currency": payment_data['currency']
                },
                "device_options": {
                    "device_id": device_code
                },
                "reference_id": payment_data.get('order_ref'),
            }
        }

        _logger.info(f"Sending Square Terminal checkout request to {url} with payload: {payload}")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            _logger.info(f"Square Terminal API response status: {response.status_code}, response body: {response.text}")
            if response.status_code in (200, 201):
                return {"status": "success", "response": response.json()}
            else:
                return {"status": "error", "error": response.text}
        except Exception as e:
            _logger.error(f"Error calling Square Terminal API: {str(e)}")
            return {"status": "error", "error": str(e)}
