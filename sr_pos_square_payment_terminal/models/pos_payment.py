# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
# from square import Square
# from square.environment import SquareEnvironment
import uuid
import requests

class POSPayment(models.Model):
    _inherit = "pos.payment"

    location_id = fields.Char("Location ID")
    device_id = fields.Char("Access Token")
    checkout_id = fields.Char("Checkout ID")
    checkout_status = fields.Char("Checkout Status")
    cancel_reason = fields.Char("Cancel Reason")

    def action_checkout(self, amount, payment_method, currency):
        payment_method_id = self.env['pos.payment.method'].browse(payment_method)
        if not payment_method_id.token:
            raise UserError(_("Square token is missing."))
        if payment_method_id.test_mode == 'live':
            url = "https://connect.squareup.com/v2/terminals/checkouts"
        else:
            url = "https://connect.squareupsandbox.com/v2/terminals/checkouts"
        headers = {
            "Authorization": "Bearer " + str(payment_method_id.token),
            "Content-Type": "application/json",
        }
        if payment_method_id.test_mode == "live" and not payment_method_id.device_ids:
            raise UserError(_("Device ID is missing."))

        device_id = "SIMULATED-TERMINAL-123"
        if payment_method_id.test_mode == "live":
            device_id = payment_method_id.device_ids[0].device
        if payment_method_id.device_ids:
            device_id = payment_method_id.device_ids[0].device

        payload = {
            "idempotency_key": str(uuid.uuid4()),
            "checkout": {
                "amount_money": {
                    "amount": int(round(amount * 100)),
                    "currency": "AUD"
                },
                "device_options": {
                    "device_id": device_id
                }
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            checkout = response.json().get("checkout")
            print ("======checkout", checkout)
            return [checkout['id'], checkout['status'], payment_method_id.location, checkout['device_options']['device_id']]
        else:
            raise UserError(f"Error : {response.text}")

    def action_checkout_status(self, checkout_id, payment_method):
        payment_method_id = self.env['pos.payment.method'].browse(payment_method)
        if not payment_method_id.token:
            raise UserError(_("Square token is missing."))
        if payment_method_id.test_mode == 'live':
            url = "https://connect.squareup.com/v2/terminals/checkouts/" + checkout_id
        else:
            url = "https://connect.squareupsandbox.com/v2/terminals/checkouts/" + checkout_id
        headers = {
            "Authorization": "Bearer " + str(payment_method_id.token),
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_response = response.json().get('checkout')
            print("+++++++++json_response+++++++++++++++++", json_response)
            # return ['COMPLETED']
            # return ['CANCELED', 'Time Out']
            return [json_response['status'], json_response.get("cancel_reason", "")]
        # # else:
        #     raise UserError(f"Error : {response.text}")
