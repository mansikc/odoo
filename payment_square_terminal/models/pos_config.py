from odoo import models, fields

class PosConfig(models.Model):
    _inherit = "pos.config"

iface_payment_terminal_square = fields.Boolean(
        string="Enable Square Terminal",
        default=False
    )