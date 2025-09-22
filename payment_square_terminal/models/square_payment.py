from odoo import models, fields


class PaymentProviderSquare(models.Model):
    _inherit = "payment.provider"

    provider = fields.Selection(
        selection_add=[("square", "Square")],
        ondelete={"square": "set default"},
    )

    # Square-specific configuration
    square_application_id = fields.Char("Square Application ID")
    square_access_token = fields.Char("Square Access Token")
    square_location_id = fields.Char("Square Location ID")   # Business location
    square_device_id = fields.Char("Square Device ID")       # POS Terminal device
    square_sandbox = fields.Boolean("Use Sandbox?", default=True)

    def _get_default_payment_methods(self):
        """Define default payment methods for Square."""
        self.ensure_one()
        if self.provider == "square":
            return self.env["payment.method"].search([
                ("code", "in", ["card", "terminal"])
            ])
        return super()._get_default_payment_methods()
