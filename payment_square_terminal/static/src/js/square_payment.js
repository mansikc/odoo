/** @odoo-module **/

import { PaymentInterface } from "@point_of_sale/app/store/payment_interface";
console.log("Custom Square Payment JS actually loaded");

export class SquareTerminalInterface extends PaymentInterface {
  async send_payment_request(cid) {
    console.log("Square send_payment_request called! CID:", cid);

    try {
      const order = this.pos.get_order();
      const paymentline = order.selected_paymentline;

      const payload = {
        order_id: order.uid,
        amount: paymentline.amount,
        currency: this.pos.currency.name,
        customer: order.get_client() ? order.get_client().name : null,
        lines: order.export_as_JSON().lines,
      };

      console.log("Square payload:", payload);

      const response = await this.env.services.rpc({
        route: "/pos/square/payment",
        params: payload,
      });

      if (response.status === "success") {
        paymentline.set_payment_status("done");
      } else {
        paymentline.set_payment_status("rejected");
      }

      return true;
    } catch (err) {
      console.error("Square payment error", err);
      this.pos.get_order().selected_paymentline.set_payment_status("retry");
      return false;
    }
  }

  async send_payment_cancel(order, cid) {
    try {
      await this.env.services.rpc({
        route: "/pos/square/cancel",
        params: { order_id: order.uid },
      });
      order.selected_paymentline.set_payment_status("cancel");
    } catch (err) {
      console.error("Cancel payment failed", err);
    }
  }
}

// Register provider with POS
PaymentInterface.register("Square", SquareTerminalInterface);
