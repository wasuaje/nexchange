!(function(window ,$) {
    "use strict";

    function loadPaymenMethods(paymentMethodsEndpoint) {
        $.get(paymentMethodsEndpoint, function (data) {
            $(".paymentMethods").html($(data));
        });
        $('.paymentMethods').removeClass('hidden');
    }

    function loadPaymenMethodsAccount(paymentMethodsAccountEndpoint, pm) {
        var data = {'payment_method': pm};

        $.get(paymentMethodsAccountEndpoint, data, function (data) {
            $(".paymentMethodsAccount").html($(data));
        });
        $('.paymentMethodsAccount').removeClass('hidden');
    }

    module.exports =
    {
        loadPaymenMethods: loadPaymenMethods,
        loadPaymenMethodsAccount: loadPaymenMethodsAccount
    };

}(window, window.jQuery)); //jshint ignore:line
