odoo.define('square_terminal_pos.square_payment', function(require) {
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const rpc = require('web.rpc');

    const SquarePayment = (PaymentScreen) => class extends PaymentScreen {
        async validateOrder(isForceValidate) {
            const order = this.env.pos.get_order();
            const payment_method = order.selected_paymentline.payment_method.name;

            if (payment_method === 'Square Terminal') {
                const amount = order.get_total_with_tax();
                const reference = order.name;

                try {
                    const result = await rpc.query({
                        model: 'pos.square.payment',
                        method: 'send_square_payment',
                        args: [amount, reference],
                    });

                    console.log('Square Result:', result);

                    if (result.checkout && result.checkout.status === 'PENDING') {
                        this.showPopup('ConfirmPopup', {
                            title: 'Square Payment Initiated',
                            body: 'Please complete payment on the Square terminal.',
                        });
                    } else if (result.error) {
                        this.showPopup('ErrorPopup', {
                            title: 'Square Payment Error',
                            body: result.error,
                        });
                        return;
                    }
                } catch (error) {
                    this.showPopup('ErrorPopup', {
                        title: 'Connection Error',
                        body: error.message,
                    });
                    return;
                }
            }

            return super.validateOrder(isForceValidate);
        }
    };

    Registries.Component.extend(PaymentScreen, SquarePayment);
    return SquarePayment;
});
