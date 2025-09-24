odoo.define('pos_square_terminal.payment', function(require) {
    console.log("SquareTerminalPayment: send_payment_request triggered");
    'use strict';
    const PaymentInterface = require('point_of_sale.PaymentInterface');
    const { Gui } = require('point_of_sale.Gui');

    const SquareTerminalPayment = PaymentInterface.extend({
        send_payment_request: async function() {
            this._super.apply(this, arguments);
            const order = this.pos.get_order();
            const line = order.selected_paymentline;

            const payment_data = {
                amount: line.amount,
                currency: this.pos.currency.name,
                order_ref: order.uid,
            };
            console.log(payment_data);
            try {
                const result = await this.rpc({
                    model: 'pos.payment.method',
                    method: 'square_create_checkout',
                    args: [this.payment_method.id, payment_data],
                });
                console.log(result.status);
                if (result.status === "success") {
                    line.set_payment_status('done');
                    Gui.showPopup('InfoPopup', {
                        title: 'Payment successful',
                        body: 'Payment processed on Square Terminal.',
                    });
                } else {
                    line.set_payment_status('retry');
                    Gui.showPopup('ErrorPopup', {
                        title: 'Payment error',
                        body: 'Payment failed: ' + result.error,
                    });
                }
            } catch (err) {
                line.set_payment_status('retry');
                Gui.showPopup('ErrorPopup', {
                    title: 'Payment error',
                    body: 'Error sending payment request: ' + err.message,
                });
            }
        },
    });

    return SquareTerminalPayment;
});
