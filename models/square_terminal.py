from odoo import models, api, _
import requests
import uuid
import logging

_logger = logging.getLogger(__name__)


class PosSquarePayment(models.Model):
    _name = 'pos.square.payment'
    _description = 'POS Square Payment Integration'

    @api.model
    def send_square_payment(self, amount, reference):
        access_token = 'EAAAlzYLg05CCXQMU7RcJse-pXVcneNErSWDIdHzQRTzWTWvlwvqm9liBkums14s'
        device_id = '13N20V7N1XYF2'

        url = 'https://connect.squareupsandbox.com/v2/terminals/checkouts'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        body = {
            'idempotency_key': str(uuid.uuid4()),
            'checkout': {
                'amount_money': {
                    'amount': int(amount * 100),  # Square requires cents
                    'currency': 'USD'
                },
                'reference_id': reference,
                'note': 'Odoo POS Order'
            },
            'device_options': {
                'device_id': device_id
            }
        }

        _logger.info('Sending Square payment request: %s', body)

        response = requests.post(url, json=body, headers=headers)

        _logger.info('Square Response: %s', response.text)

        if response.status_code == 200:
            return response.json()
        else:
            return {'error': response.text}
