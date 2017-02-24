!(function (window, $) {
    "use strict";

    var requestNewSMSToken = function() {
        var url = $("#resend_sms_button").data('url');

        $("#resend_sms_button").html(
            '<i class="fa fa-spinner fa-spin"></i>&nbsp;Sending you the token again...'
        );

        $.post( url , function( data ) {
            $("#resend_sms_button").html(
                '<i class="fa fa-repeat" aria-hidden="true"></i>&nbsp;Send-me the token again'
            );
            var message = gettext("SMS token sent. Fill in the verification form field and click on 'Verify phone now'.");
            toastr.info(message);
        }).fail(function(){

            $("#resend_sms_button").html(
                '<i class="fa fa-repeat" aria-hidden="true"></i>&nbsp;Send-me the verification token again'
            );
            var message = gettext("Something went wrong. Please, try again.");
            toastr.error(message);
        });
    };


    $("#resend_sms_button").on("click", requestNewSMSToken);

    var verifyPhone = function() {
        var url = $("#verify_phone_now").data('url');
        var token = $("#verification_code").val();

        $("#alert_phone_not_verified").hide();
        $("#alert_verifying_phone").show();

         $.post( url , {'token': token}, function( data ) {
            if (data.status === 'OK') {
                location.reload(); //TODO: Ajax update screen..
            } else if (data.status === 'NOT_MATCH') {
                $("#alert_verifying_phone").hide();
                $("#alert_phone_not_verified").show();
                var message = gettext('The code you sent was incorrect. Please, try again.');
                toastr.error(message);
            }


        }).fail(function(){
            $("#alert_verifying_phone").hide();
            $("#alert_phone_not_verified").show();
            var message = gettext('Something went wrong. Please, try again.');
            toastr.error(message);
        });

    };

    $("#verify_phone_now").on("click", verifyPhone);

    window.verifyPhone = verifyPhone; //hack to allow tests to run
}(window, window.jQuery)); //jshint ignore:line
