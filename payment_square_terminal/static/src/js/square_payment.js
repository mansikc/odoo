/** @odoo-module **/

odoo.define('payment_square_terminal.pos_square_terminal', function (require) {
    "use strict";

    const PaymentInterface = require('point_of_sale.PaymentInterface');
    const models = require('point_of_sale.models');

    const SquareTerminalInterface = PaymentInterface.extend({

        /**
         * Send payment request to Odoo backend (which then calls Square API)
         */
        async send_payment_request(cid) {
            try {
                const order = this.pos.get_order();
                const paymentline = order.selected_paymentline;

                // Amount in POS currency
                const amount = paymentline.amount;

                // Build payload for backend
                const payload = {
                    order_id: order.uid,  // POS internal order id
                    amount: amount,
                    currency: this.pos.currency.name,
                    customer: order.get_client() ? order.get_client().name : null,
                    lines: order.export_as_JSON().lines,
                };

                // Call backend controller (new route)
                const response = await this._rpc({
                    route: '/pos/square/payment',
                    params: payload,
                });

                if (response.status === 'success') {
                    paymentline.set_payment_status('done');
                } else {
                    paymentline.set_payment_status('rejected');
                }

                return true;
            } catch (err) {
                console.error("Square payment error", err);
                this.pos.get_order().selected_paymentline.set_payment_status('retry');
                return false;
            }
        },

        /**
         * Cancel a payment
         */
        async send_payment_cancel(order, cid) {
            try {
                await this._rpc({
                    route: '/pos/square/cancel',
                    params: { order_id: order.uid },
                });
                order.selected_paymentline.set_payment_status('cancel');
            } catch (err) {
                console.error("Cancel payment failed", err);
            }
        }
    });

    models.register_payment_method('square', SquareTerminalInterface);

    return SquareTerminalInterface;
});