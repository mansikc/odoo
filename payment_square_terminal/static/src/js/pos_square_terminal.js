// static/src/js/pos_square_terminal.js

odoo.define('pos_square_terminal.payment', function (require) {
    "use strict";

    const PaymentTerminal = require('pos_payment_terminal.payment_terminal');
    const { _t } = require('web.core');

    const PosSquareTerminal = PaymentTerminal.extend({
        terminal_name: 'square_terminal',

        send_payment_request: function () {
            const paymentline = this.pos.get_order().selected_paymentline;
            if (!paymentline || paymentline.payment_method.use_payment_terminal !== this.terminal_name) {
                return;
            }

            const amount = paymentline.amount;
            const device_id = paymentline.payment_method.square_device_id[0]; // Get the ID from the Many2one field

            // Call the Python backend to create the Square checkout
            this.rpc({
                model: 'pos.square.payment',
                method: 'create_square_checkout',
                args: [amount, device_id],
            }).then(result => {
                if (result.status === 'pending') {
                    // Update the payment line status and start polling/waiting for webhook
                    paymentline.set_payment_status('waiting');
                } else {
                    paymentline.set_payment_status('force_done'); // Or an error status
                    this.show_popup('Error', _t(result.message));
                }
            }).catch(error => {
                paymentline.set_payment_status('force_done');
                this.show_popup('Error', _t('Failed to connect to the Square Terminal.'));
            });
        },
        
        // This function will be called by your webhook handler
        set_payment_status_from_webhook: function(checkout_id, status) {
            const order = this.pos.get_order();
            const paymentline = order.selected_paymentline;
            if (paymentline && paymentline.square_checkout_id === checkout_id) {
                if (status === 'COMPLETED') {
                    paymentline.set_payment_status('done');
                } else {
                    paymentline.set_payment_status('force_done'); // Mark as failed or canceled
                }
            }
        },
    });

    return PosSquareTerminal;
});
