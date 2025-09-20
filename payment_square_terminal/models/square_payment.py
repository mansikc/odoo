from odoo import models, fields

class PaymentProviderSquare(models.Model):
    _inherit = "payment.provider"

    # Add Square as a provider choice
    provider = fields.Selection(
        selection_add=[("square", "Square Terminal")],
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