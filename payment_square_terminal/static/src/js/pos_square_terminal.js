odoo.define('pos_square_terminal.payment', function(require) {
    'use strict';
    const PaymentInterface = require('point_of_sale.PaymentInterface');
    const {Gui} = require('point_of_sale.Gui');

    const SquareTerminalPayment = PaymentInterface.extend({
        send_payment_request: async function(cid) {
            this._super.apply(this, arguments);
            const order = this.pos.get_order();
            const line = order.selected_paymentline;
            // Prepare payment data to send to backend
            const data = {
                amount: line.amount,
                currency: this.pos.currency.name,
                payment_method_id: line.payment_method.id,
                access_token: this.payment_method.square_access_token,
                location_id: this.payment_method.square_location_id,
                device_code: this.payment_method.square_device_code,
                order_ref: order.uid,
            };
            // Call backend, in production use secure controller endpoint!
            try {
                let result = await this.rpc({
                    model: 'pos.payment.method',
                    method: 'square_process_payment',
                    args: [[this.payment_method.id], data],
                });
                if (result && result.status === 'SUCCESS') {
                    line.set_payment_status('success');
                } else {
                    line.set_payment_status('retry');
                }
            } catch (err) {
                Gui.showPopup('ErrorPopup', {
                    title: "Square Payment Error",
                    body: err.message,
                });
                line.set_payment_status('retry');
            }
        },
    });

    return SquareTerminalPayment;
});
