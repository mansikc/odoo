from odoo import models, fields

class SquareConfig(models.Model):
    _name = "square.config"
    _description = "Square Terminal API Configuration"

    name = fields.Char(string="Config Name", required=True)
    access_token = fields.Char(string="Square Access Token", required=True)
    location_id = fields.Char(string="Location ID", required=True)
    device_id = fields.Char(string="Device ID", required=True)