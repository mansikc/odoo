/** @odoo-module **/

odoo.define('payment_square_terminal.pos_square_terminal', function (require) {
    "use strict";

    const PaymentInterface = require('point_of_sale.PaymentInterface');
    const models = require('point_of_sale.models');

    const SquareTerminalInterface = PaymentInterface.extend({

        /**
         * Send payment request to Square
         */
        async send_payment_request(cid) {
            try {
                // Get current order
                const order = this.pos.get_order();
                const paymentline = order.selected_paymentline;

                // Get payment amount
                const amount = paymentline.amount;

                // Build payload
                const payload = {
                    order_id: order.uid,            // POS internal order id
                    amount: amount,                 // Amount to pay
                    currency: this.pos.currency.name, // Currency code, e.g. "USD"
                    customer: order.get_client() ? order.get_client().name : null,
                    lines: order.export_as_JSON().lines, // Order lines (products)
                };

                // Call backend controller that integrates with Square
                const response = await this._rpc({
                    model: 'pos.square.api',
                    method: 'send_payment_request',
                    args: [payload],
                });

                // Handle response (success/failure)
                if (response.status === 'success') {
                    paymentline.set_payment_status('done');
                } else {
                    paymentline.set_payment_status('rejected');
                }

                return true;
            } catch (err) {
                console.error("Square payment error", err);
                order.selected_paymentline.set_payment_status('retry');
                return false;
            }
        },

        /**
         * Cancel payment if needed
         */
        async send_payment_cancel(order, cid) {
            try {
                await this._rpc({
                    model: 'pos.square.api',
                    method: 'cancel_payment',
                    args: [order.uid],
                });
                order.selected_paymentline.set_payment_status('cancel');
            } catch (err) {
                console.error("Cancel payment failed", err);
            }
        }
    });

    // Register Square as a new payment method
    models.register_payment_method('square', SquareTerminalInterface);

    return SquareTerminalInterface;
});