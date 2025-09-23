from odoo import models, fields

class PaymentProviderSquare(models.Model):
    _inherit = "payment.provider"

    # Add Square as a provider choice
    provider = fields.Selection([
            ('square', 'Square'),
            ('stripe', 'Stripe'),
            ('paypal', 'PayPal')
        ],
        selection_add=[("square", "Square")],
        ondelete={"square": "set default"},
    )

    # Square-specific configuration
    square_application_id = fields.Char(
        "Square Application ID",
        default="sandbox-sq0idp-Jqc9DX2a0IBzbpkOZjUtsA"
    )
    square_access_token = fields.Char(
        "Square Access Token",
        default="EAAAl2kUOJa8Dmmj7aREZ-Wvixdow4vcZ2vUX7k5BvtZ56nrnws7QOAM7psZK8dO"
    )
    square_location_id = fields.Char(
        "Square Location ID",
        default="LAP0GP4BXQHRE"
    )
    square_sandbox = fields.Boolean(
        "Use Sandbox?",
        default=True
    )
    
    square_device_id = fields.Char(
        "Device Id"
    )

    def _get_default_payment_methods(self):
        """Define default payment methods for Square."""
        self.ensure_one()
        if self.provider == 'square':
            return self.env['payment.method'].search([('code', 'in', ['square_card', 'square_terminal'])])
        return super()._get_default_payment_methods()
    
    def _get_payment_terminal_selection(self):
        selections = super()._get_payment_terminal_selection()
        selections.append(("square", "Square Terminal"))
        return selections
