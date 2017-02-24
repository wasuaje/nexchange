!(function(window, $) {
    "use strict";

    function canProceedtoRegister(objectName) {
        var payMeth = $('#payment_method_id').val(),
            userAcc = $('#user_address_id').val(),
            userAccId = $('#new_user_account').val();
        if (!((objectName == 'menu2' || objectName == 'btn-register') &&
            payMeth === '' &&
            userAcc === '' &&
            userAccId === '')) {
            return true;
        }
        return false;
    }

    module.exports = {
        canProceedtoRegister: canProceedtoRegister
    };
}(window, window.jQuery)); //jshint ignore:line