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

class POSPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    is_square_payment = fields.Boolean("Square Payment")
    test_mode = fields.Selection([
        ("stage", "staging"),
        ("live", "Live")
    ])
    location = fields.Char("Location ID")
    token = fields.Char("Access Token")
    device_ids = fields.One2many("square.payment.device", "pos_payment_method_id")
    generated_device_code = fields.Char()

    @api.model
    def _load_pos_data_fields(self, config):
        return super()._load_pos_data_fields(config) + ['is_square_payment']

    def action_generate_location(self):
        if not self.token:
            raise UserError(_("Square token is missing."))

        if self.test_mode == 'live':
            url = "https://connect.squareup.com/v2/locations"
        else:
            url = "https://connect.squareupsandbox.com/v2/locations"
        headers = {
            "Authorization": "Bearer " + str(self.token),
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)
        print ("==location==response.json()=====",response.json())
        if response.status_code == 200:
            locations = response.json().get("locations", [])
            if locations:
                self.location = locations[0]['id']
            else:
                raise UserError(_("No locations found in Square account."))
        else:
            raise UserError(f"Error fetching locations: {response.text}")

    def generate_device(self):
        if not self.token:
            raise UserError(_("Square token is missing."))

        if not self.location:
            raise UserError(_("Location ID is missing. Please generate a location first."))

        if self.test_mode == 'live':
            url = "https://connect.squareup.com/v2/devices/codes"
        else:
            url = "https://connect.squareupsandbox.com/v2/devices/codes"

        payload = {
            "idempotency_key": str(uuid.uuid4()),
            "device_code": {
                "name": "Odoo POS Terminal",
                "product_type": "TERMINAL_API",
                "location_id": self.location
            }
        }

        headers = {
            "Authorization": "Bearer " + str(self.token),
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=payload, headers=headers)
        print ("========response.json()",response.json())
        if response.status_code == 200:
            device_data = response.json().get("device_code", {})
            # Prepare vals
            self.generated_device_code = device_data['code']
        else:
            raise UserError(f"Error creating device: {response.text}")

    def get_device(self):
        if not self.token:
            raise UserError(_("Square token is missing."))

        if not self.location:
            raise UserError(_("Location ID is missing. Please generate a location first."))

        if self.test_mode == 'live':
            url = "https://connect.squareup.com/v2/devices/codes"
        else:
            url = "https://connect.squareupsandbox.com/v2/devices/codes"

        headers = {
            "Authorization": "Bearer " + str(self.token),
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            device_data = response.json().get('device_codes', {})
            self.device_ids = [(5, 0)]
            for device in device_data:
                vals = {
                    "device": device.get("device_id"),
                    "name": device.get("name") or "Unnamed Device",
                    "code": device.get("code") or "",
                    "location": device.get("location_id"),
                    "status": device.get("status"),
                    "pos_payment_method_id": self.id, }
                # Create the device record in Odoo
                self.env["square.payment.device"].create(vals)
        else:
            raise UserError(f"Error Fetching device: {response.text}")

class SquarePaymentDevice(models.Model):
    _name = "square.payment.device"
    _description = "Square Payment Device"

    pos_payment_method_id = fields.Many2one("pos.payment.method", "Payment Method")
    device = fields.Char("ID")
    name = fields.Char("Name")
    code = fields.Char("Model")
    location = fields.Char("Location")
    status = fields.Char("Status")