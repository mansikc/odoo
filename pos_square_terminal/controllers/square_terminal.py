import json
import uuid
import requests

from odoo import http
from odoo.http import request

class SquareTerminalController(http.Controller):

    @http.route('/pos/square/payment', type='json', auth='user')
    def pos_square_payment(self, **kwargs):
        order_id = kwargs.get('order_id')
        amount = kwargs.get('amount')
        currency = kwargs.get('currency', 'USD')

        config = request.env['square.config'].sudo().search([], limit=1)
        if not config:
            return {"error": "Square configuration missing"}

        url = "https://connect.squareup.com/v2/terminals/checkouts"

        headers = {
            "Square-Version": "2023-09-20",
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "idempotency_key": str(uuid.uuid4()),
            "checkout": {
                "amount_money": {
                    "amount": int(amount),
                    "currency": currency
                },
                "device_options": {
                    "device_id": config.device_id
                },
                "reference_id": str(order_id)
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return {"success": response.json()}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}