from odoo import models, fields

class PosConfig(models.Model):
    _inherit = "pos.config"

iface_payment_terminal = fields.Selection(
        selection_add=[('square', 'Square Terminal')],
        string="Payment Terminal"
    )