import requests
from odoo import api, models

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    @api.model
    def square_process_payment(self, data):
        access_token = data.get('access_token')
        device_code = data.get('device_code')
        location_id = data.get('location_id')
        amount = data.get('amount')
        currency = data.get('currency')
        order_ref = data.get('order_ref')

        # Compose headers and payload for Square API
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        payload = {
            "idempotency_key": order_ref,
            "amount_money": {
                "amount": int(amount * 100),  # Square expects cents
                "currency": currency,
            },
            "device_id": device_code,
            "location_id": location_id,
        }
        try:
            resp = requests.post(
                "https://connect.squareup.com/v2/terminals/checkouts",
                headers=headers,
                json=payload,
                timeout=15,
            )
            if resp.status_code == 200 and resp.json().get('checkout'):
                return {'status': 'SUCCESS', 'resp': resp.json()}
            else:
                return {'status': 'FAILED', 'error': resp.text}
        except Exception as e:
            return {'status': 'FAILED', 'error': str(e)}
