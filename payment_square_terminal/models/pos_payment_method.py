import uuid
import requests
from odoo import models, api

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

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

        idempotency_key = str(uuid.uuid4())  # Unique key to avoid duplicate charges

        payload = {
            "idempotency_key": idempotency_key,
            "checkout": {
                "amount_money": {
                    "amount": int(payment_data['amount'] * 100),  # in cents
                    "currency": payment_data['currency']
                },
                "device_options": {
                    "device_id": device_code
                },
                "reference_id": payment_data.get('order_ref'),
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code in (200, 201):
            return {"status": "success", "response": response.json()}
        else:
            return {"status": "error", "error": response.text}
