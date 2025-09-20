# -*- coding: utf-8 -*-
import logging
import json
import uuid
import requests

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# class PaymentAcquirerSquare(models.Model):
#     _inherit = 'payment.acquirer'

#     provider = fields.Selection(selection_add=[('square', 'Square')], ondelete={'square': 'set default'})
#     square_application_id = fields.Char(string="Square Application ID")
#     square_access_token = fields.Char(string="Square Access Token")
#     square_location_id = fields.Char(string="Square Location ID")
#     square_sandbox = fields.Boolean(string="Sandbox mode", default=True)

#     def _get_square_base_url(self):
#         self.ensure_one()
#         return 'https://connect.squareupsandbox.com' if self.square_sandbox else 'https://connect.squareup.com'

#     def _square_headers(self):
#         self.ensure_one()
#         if not self.square_access_token:
#             raise UserError(_("Please configure Square Access Token on the acquirer."))
#         return {
#             'Authorization': f'Bearer {self.square_access_token}',
#             'Content-Type': 'application/json',
#             'Accept': 'application/json',
#             # Optionally set Square-Version header if you want a fixed API version:
#             # 'Square-Version': '2024-07-17',
#         }

#     def _square_create_payment(self, source_id, amount, currency='USD', idempotency_key=None, note=None):
#         """Create payment in Square using REST API (/v2/payments).
#         - source_id: a card nonce or 'CARD_ON_FILE' token etc (depends on frontend flow)
#         - amount: float (e.g. 12.50)
#         - currency: 'USD' etc
#         Returns JSON response (dict) or raises on error.
#         """
#         self.ensure_one()
#         if idempotency_key is None:
#             idempotency_key = str(uuid.uuid4())

#         dollars = float(amount)
#         body = {
#             "source_id": source_id,
#             "idempotency_key": idempotency_key,
#             "amount_money": {
#                 "amount": int(round(dollars * 100)),  # cents
#                 "currency": currency
#             }
#         }
#         if self.square_location_id:
#             body["location_id"] = self.square_location_id
#         if note:
#             body["note"] = note

#         url = f"{self._get_square_base_url()}/v2/payments"
#         _logger.debug("Square create_payment request: %s %s", url, body)

#         resp = requests.post(url, headers=self._square_headers(), json=body, timeout=30)
#         try:
#             data = resp.json()
#         except Exception:
#             _logger.exception("Invalid JSON from Square: %s", resp.text)
#             raise UserError(_("Invalid response from Square. Details logged."))

#         if resp.status_code not in (200, 201):
#             _logger.error("Square error: %s %s", resp.status_code, data)
#             # Bubble up useful message if present
#             msg = data.get('errors') or data
#             raise UserError(_("Square API error: %s") % json.dumps(msg))

#         return data

# class PaymentTransactionSquare(models.Model):
#     _inherit = 'payment.transaction'

#     def _square_handle_notification(self, data):
#         """Process data from Square (webhook). This is an example stub.
#         Extend this to map Square payment -> Odoo transaction.
#         """
#         _logger.info("Handling Square webhook data: %s", data)
#         # Example: if data contains payment id and status, try find corresponding transaction
#         # You might map via idempotency_key or by storing square_payment_id on the transaction.
#         return True


from odoo import fields, models

class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    square_terminal = fields.Boolean("Use Square Terminal")
    square_location_id = fields.Char("Square Location ID")
    square_device_id = fields.Char("Square Device ID")
