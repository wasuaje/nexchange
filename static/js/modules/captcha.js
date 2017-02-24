!(function(window ,$) {
  "use strict";
    var isVerified = false;

  var verifyRecatpchaCallback = function(response) {

          //console.log( 'g-recaptcha-response: ' + response );
      if($('.phone.val').val().length > 10) {
            $('.create-acc')
                .not('.resend')
                .removeClass('disabled');
      }

      isVerified = true;
  };
  
  var getIsVerefied = function () {
      return isVerified;
  };

var doRender = function() {
      grecaptcha.render( 'grecaptcha', {
        'sitekey' : '6LfPaAoUAAAAAOmpl6ZwPIk2Zs-30TErK48dPhcS',  // required
        'theme' : 'light',  // optional
        'callback': verifyRecatpchaCallback  // optional
      });
};

module.exports = {
    verifyRecatpchaCallback:verifyRecatpchaCallback,
    doRender: doRender,
    isVerified: getIsVerefied
};

}(window, window.jQuery)); //jshint ignore:line