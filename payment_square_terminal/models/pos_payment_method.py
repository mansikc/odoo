from odoo import fields, models

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    use_square_terminal = fields.Boolean(string="Use Square Terminal")
    square_access_token = fields.Char('Square Access Token')
    square_location_id = fields.Char('Square Location ID')
    square_device_code = fields.Char('Square Device Code')

    def _get_payment_terminal_selection(self):
        return super()._get_payment_terminal_selection() + [('square_terminal', 'Square Terminal')]
