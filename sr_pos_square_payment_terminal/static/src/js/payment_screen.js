/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { ConfirmationDialog, AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useAutofocus, useService } from "@web/core/utils/hooks";

console.log("+++++++++PaymentScreen++++++++")
patch(PaymentScreen.prototype, {

    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
    },
    //@Override
    async addNewPaymentLine(paymentMethod) {
        if (
            paymentMethod.type === "pay_later" &&
            (!this.currentOrder.to_invoice ||
                this.pos.models["ir.module.module"].find((m) => m.name === "pos_settle_due")
                    ?.state !== "installed")
        ) {
            this.notification.add(
                _t(
                    "To ensure due balance follow-up, generate an invoice or download the accounting application. "
                ),
                { autocloseDelay: 7000 }
            );
        }
        if (this.pos.paymentTerminalInProgress && paymentMethod.use_payment_terminal) {
            this.dialog.add(AlertDialog, {
                title: _t("Error"),
                body: _t("There is already an electronic payment in progress."),
            });
            return;
        }

        if (this.paymentLines.length === 0) {
            this.makeAnimation();
        }
        // original function: click_paymentmethods
        const result = this.currentOrder.addPaymentline(paymentMethod);
        if (result) {
            this.numberBuffer.set(result.amount.toString());
            if (
                paymentMethod.use_payment_terminal &&
                !this.isRefundOrder &&
                paymentMethod.payment_terminal.fastPayments
            ) {
                const newPaymentLine = this.paymentLines.at(-1);
                this.sendPaymentRequest(newPaymentLine);
            }
            const search_pay_method = await this.orm.searchRead(
                "pos.payment.method",
                [["id", "=", paymentMethod.id]],
                ["is_square_payment"],
                { limit: 1 }
            )
            console.log("+++++++++paymentMethod++++++++", paymentMethod, search_pay_method)
            const lastPaymentLine = this.paymentLines.at(-1);
            if (search_pay_method && search_pay_method[0].is_square_payment && lastPaymentLine.amount > 0) {
                console.log("+++++++++lastPaymentLine++++++=", lastPaymentLine, this)
                const checkout_data = await this.orm.call(
                        "pos.payment",
                        "action_checkout",
                        [0, lastPaymentLine.amount, lastPaymentLine.payment_method_id.id, this.pos.config.currency_id.name]
                    );
                lastPaymentLine['checkout_id'] = checkout_data[0];
                lastPaymentLine['checkout_status'] = checkout_data[1];
                lastPaymentLine['location_id'] = checkout_data[2];
                lastPaymentLine['device_id'] = checkout_data[3];
                this.dialog.add(ConfirmationDialog, {
                    title: "Square",
                    body: "Are you want to complete the payment on connected terminal?",
                    confirmLabel: _t("Check Status"),
                    cancelLabel: _t("Cancel Transaction"),
                    confirm: async () => {
                        const checkout_status = await this.orm.call(
                            "pos.payment",
                            "action_checkout_status",
                            [0, checkout_data[0], lastPaymentLine.payment_method_id.id]
                        );
                        lastPaymentLine['checkout_status'] = checkout_status[0];
                        lastPaymentLine['cancel_reason'] = checkout_status[1];
                        if (checkout_status[0] == 'COMPLETED') {
                            this.validateOrder();
                        } else if (checkout_status[0] == 'PENDING') {
                            return false;
                        } else if (checkout_status[0] == 'CANCELED') {
                            await this.deletePaymentLine(lastPaymentLine.uuid)
                            this.notification.add(
                                lastPaymentLine['cancel_reason'],
                                {
                                    type: "danger",
                                }
                            );
                        }
                    },
                    cancel: async () => {
                        await this.deletePaymentLine(lastPaymentLine.uuid)
                    },
                    dismiss: async () => {
                        await this.deletePaymentLine(lastPaymentLine.uuid)
                    },
                });
            }
            return true;
        } else {
            this.dialog.add(AlertDialog, {
                title: _t("Error"),
                body: _t("There is already an electronic payment in progress."),
            });
            return false;
        }
    }

});
