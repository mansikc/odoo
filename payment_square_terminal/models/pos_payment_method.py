from odoo import fields, models

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    use_square_terminal = fields.Boolean(string="Use Square Terminal")
    square_access_token = fields.Char('EAAAl2kUOJa8Dmmj7aREZ-Wvixdow4vcZ2vUX7k5BvtZ56nrnws7QOAM7psZK8dO')
    square_location_id = fields.Char('LAP0GP4BXQHRE')
    square_device_code = fields.Char('NG6YH1F1HM1Ne')

    def _get_payment_terminal_selection(self):
        return super()._get_payment_terminal_selection() + [('square_terminal', 'Square Terminal')]
