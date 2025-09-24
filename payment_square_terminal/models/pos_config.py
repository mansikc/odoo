from odoo import models

class PosConfig(models.Model):
    _inherit = "pos.config"

    def _get_payment_terminal_selection(self):
        selections = super()._get_payment_terminal_selection()
        selections.append(("square", "Square Terminal"))
        return selections