/** @odoo-module **/

odoo.define("pos_square_terminal.square_payment", function (require) {
  "use strict";

  const rpc = require("web.rpc");

  function sendSquarePayment(order_id, amount, currency) {
    return rpc.query({
      route: "/pos/square/payment",
      params: {
        order_id: order_id,
        amount: amount,
        currency: currency,
      },
    });
  }

  return {
    sendSquarePayment,
  };
});
