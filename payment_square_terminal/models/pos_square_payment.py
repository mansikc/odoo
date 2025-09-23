# models/pos_square_payment.py

from odoo import models, fields, api
import square

# Make sure you have the square SDK installed: pip install square

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _get_payment_terminal_selection(self):
        # Extend the selection to add the Square Terminal option
        res = super(PosPaymentMethod, self)._get_payment_terminal_selection()
        res.append(('square_terminal', 'Square Terminal'))
        return res

    use_payment_terminal = fields.Selection(selection='_get_payment_terminal_selection', ondelete='cascade')

    # Link the payment method to a specific Square device
    square_device_id = fields.Many2one('pos_square_terminal.device', string="Square Terminal Device")


class PosSquarePayment(models.Model):
    _name = 'pos.square.payment'
    _description = 'Square Terminal Payment Logic'

    # This is a dummy model to handle the RPC calls from the front-end
    # The actual logic will be placed here

    def create_square_checkout(self, amount, device_id):
        # Your Square API credentials
        # This should ideally come from pos.config
        square_access_token = self.env['pos.config'].sudo().search([], limit=1).square_access_token
        square_location_id = self.env['pos.config'].sudo().search([], limit=1).square_location_id
        
        if not square_access_token or not square_location_id or not device_id:
            return {'status': 'failed', 'message': 'Square credentials or device not configured.'}

        try:
            client = square.Client(
                access_token=square_access_token,
                environment='sandbox' # Use 'production' for live payments
            )
            
            # Use the Terminal API to create a checkout request
            result = client.terminal.create_terminal_checkout(
                body={
                    "idempotency_key": self.env['ir.sequence'].next_by_code('square.checkout.idempotency'),
                    "checkout": {
                        "amount_money": {
                            "amount": int(amount * 100),
                            "currency": 'USD' # Or your company's currency
                        },
                        "device_options": {
                            "device_id": device_id,
                            "tip_mode": "TIPS_ENABLED"
                        }
                    }
                }
            )

            if result.is_success():
                return {
                    'status': 'pending', 
                    'checkout_id': result.body['checkout']['id']
                }
            else:
                return {
                    'status': 'failed',
                    'message': f"API Error: {result.errors}"
                }

        except Exception as e:
            return {'status': 'failed', 'message': str(e)}

    def check_payment_status(self, checkout_id):
        # This method can be called from the front-end to poll for the payment status
        # Recommended to use webhooks instead for real-time updates
        
        # ... your code to call the Square API to get checkout status
        # This should return 'COMPLETED', 'PENDING', 'CANCELED', or 'FAILED'
        pass
