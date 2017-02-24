(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
!(function (window, $) {
      'use strict';

       var  currency = 'rub',
        paymentMethodsEndpoint = '/en/paymentmethods/ajax/',
        paymentMethodsAccountEndpoint = '/en/paymentmethods/account/ajax/',
        cardsEndpoint = '/en/api/v1/cards',
        // Required modules
        orderObject = require('./modules/orders.js'),
        paymentObject = require('./modules/payment.js'),
        captcha = require('./modules/captcha.js'),

        paymentType = '',
        actualPaymentType = '',
        preferenceIdentifier = '',
        preferenceOwner = '';

        $('.trade-type').val('1');

        window.ACTION_BUY = 1;
        window.ACTION_SELL = 0;
        window.action = window.ACTION_BUY; // 1 - BUY 0 - SELL

    $(function () {
            orderObject.setCurrency(false, currency);
            orderObject.reloadCardsPerCurrency(currency, cardsEndpoint);

            var timer = null,
                delay = 500,
                phones = $('.phone');
            //if not used idx: remove jshint
            phones.each(function () {
                if(typeof $(this).intlTelInput === 'function') {
                    // with AMD move to https://codepen.io/jackocnr/pen/RNVwPo
                    $(this).intlTelInput();
                }
            });            

            orderObject.updateOrder($('.amount-coin'), true, currency);
            // if not used event, isNext remove  jshint
            $('#graph-range').on('change', function() {
                orderObject.setCurrency(false, currency);
            });

            $('.exchange-sign').click(function () {
                var menuElem = $('.menu1');

                window.action = menuElem.hasClass('sell') ?
                    window.ACTION_BUY : window.ACTION_SELL;

                orderObject.updateOrder($('.amount-coin'), false, currency, function () {
                        menuElem.toggleClass('sell');
                });
            });

            $('.trigger').click( function(){
                $('.trigger').removeClass('active-action');
                $(this).addClass('active-action');
                if ($(this).hasClass('trigger-buy')) {
                    $('.menu1').removeClass('sell');
                    window.action = window.ACTION_BUY;

                    paymentObject.loadPaymenMethods(paymentMethodsEndpoint);
                    orderObject.updateOrder($('.amount-coin'), false, currency, function () {
                        orderObject.toggleBuyModal();
                    });

                } else {
                    $('.menu1').addClass('sell');
                    window.action = window.ACTION_SELL;

                    orderObject.updateOrder($('.amount-coin'), false, currency, function () {
                        orderObject.toggleSellModal();
                    });
                }

                $('.trade-type').val(window.action);

                orderObject.updateOrder($('.amount-coin'), true, currency);

                var newCashClass = window.action === window.ACTION_BUY ? 'rate-buy' : 'rate-sell';
                  $('.amount-cash, .amount-coin')
                    .removeClass('rate-buy')
                    .removeClass('rate-sell')
                    .addClass(newCashClass);
            });

            $('.amount').on('keyup', function () {
                // Protection against non-integers
                var val = this.value,
                    lastChar = val.slice(-1),
                    prevVal = val.substr(0, val.length-1);
                if(!!prevVal && lastChar === '.' &&
                    prevVal.indexOf('.') === -1) {
                    return;
                    // # TODO: User isNaN
                } else if(!parseInt(lastChar) &&
                          parseInt(lastChar) !== 0) {
                    // TODO: animate error
                    $(this).val(prevVal);
                    return;
                }
                var self = this,
                    loaderElem = $('.exchange-sign'),
                    cb = function animationCallback() {
                        loaderElem.one('animationiteration webkitAnimationIteration', function() {
                            loaderElem.removeClass('loading');
                        });
                        
                        setTimeout(function () {
                            loaderElem.removeClass('loading');
                        }, 2000);// max animation duration
                    };
                
                loaderElem.addClass('loading');
                if (timer) {
                    clearTimeout(timer);
                    timer = null;
                }
                timer = setTimeout(function () {
                    orderObject.updateOrder($(self), false, currency, cb);
                }, delay);
            });

             $('.payment-method').on('change', function () {
                paymentObject.loadPaymenMethodsAccount(paymentMethodsAccountEndpoint);

            });

            $('.currency-select').on('change', function () {
                currency = $(this).val().toLowerCase();
                orderObject.setCurrency($(this), currency);
                //bind all select boxes
                $('.currency-select').not('.currency-to').val($(this).val());
                orderObject.updateOrder($('.amount-coin'), false, currency);
                orderObject.reloadCardsPerCurrency(currency, cardsEndpoint);
            });
            //using this form because the object is inside a modal screen
            $(document).on('change','.payment-method', function () {
                var pm = $('.payment-method option:selected').val();
                $('#payment_method_id').val(pm);
                paymentObject.loadPaymenMethodsAccount(paymentMethodsAccountEndpoint, pm);

            });

        });

    $(function() {
        // TODO: get api root via DI
        $('#payment_method_id').val('');
        $('#user_address_id').val('');
        $('#new_user_account').val('');
        // TODO: if no amount coin selected DEFAULT_AMOUNT to confirm
        var confirm = $('.amount-coin').val() ? $('.amount-coin').val() : DEFAULT_AMOUNT;
        $('.btc-amount-confirm').text(confirm);

        var apiRoot = '/en/api/v1',
            createAccEndpoint = apiRoot + '/phone',
            menuEndpoint = apiRoot + '/menu',
            breadcrumbsEndpoint = apiRoot + '/breadcrumbs',
            validatePhoneEndpoint = '/en/profile/verifyPhone/',
            placerAjaxOrder = '/en/order/ajax/',
            paymentAjax = '/en/payment/ajax/',
            DEFAULT_AMOUNT = 1;

        $('.next-step, .prev-step').on('click', orderObject.changeState);
        $('.phone.val').on('keyup', function () {
            if($(this).val().length) {
                $('.create-acc')
                    .not('.resend')
                    .removeClass('disabled');
            }
        });
        $('.create-acc').on('click', function () {
            if($(this).hasClass('disabled')) {
                return;
            }
            $('.phone.val').addClass('disabled');


            var regPayload = {
                // TODO: check collision with qiwi wallet
                phone: $('.register .phone').val()
            };
            $.ajax({
                type: 'POST',
                url: createAccEndpoint,
                data: regPayload,
                success: function () {
                    $('.register .step2').removeClass('hidden');
                    $('.verify-acc').removeClass('hidden');
                    $('.create-acc').addClass('hidden');
                    $('.create-acc.resend').removeClass('hidden');
                },
                error: function () {
                	var message = gettext('Invalid phone number');
                    toastr.error(message);
                }
            });
        });

        $('.verify-acc').on('click', function () {
            var verifyPayload = {
                token: $('#verification_code').val(),
                phone: $('.register .phone').val()
            };
            $.ajax({
                type: 'POST',
                url: validatePhoneEndpoint,
                data: verifyPayload,
                success: function (data) {
                    if (data.status === 'OK') {
                        orderObject.reloadRoleRelatedElements(menuEndpoint, breadcrumbsEndpoint);
                        orderObject.changeState(null, 'next');
                    } else {
                    	var message = gettext('The code you sent was incorrect. Please, try again.');
                        toastr.error(message);
                    }
                },
                error: function () {
                	var message = gettext('Something went wrong. Please, try again.');
                    toastr.error(message);
                }
            });

        });


        $('.place-order').on('click', function () {
            //TODO verify if $(this).hasClass('sell-go') add
            // the other type of transaction
            // add security checks
            actualPaymentType = $('.payment-preference-actual').text() ;
            preferenceIdentifier = $('.payment-preference-identifier-confirm').text();
            preferenceOwner = $('.payment-preference-owner-confirm').text();
            var verifyPayload = {
                    'trade-type': $('.trade-type').val(),
                    'csrfmiddlewaretoken': $('#csrfmiddlewaretoken').val(),
                    'amount-coin': $('.amount-coin').val() || DEFAULT_AMOUNT,
                    'currency_from': $('.currency-from').val(), //fiat
                    'currency_to': $('.currency-to').val(), //crypto
                    'pp_type': actualPaymentType,
                    'pp_identifier': preferenceIdentifier,
                    'pp_owner': preferenceOwner,
                    '_locale': $('.topright_selectbox').val()
                };
            
            $.ajax({
                type: 'post',
                url: placerAjaxOrder,
                dataType: 'text',
                data: verifyPayload,
                contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
                success: function (data) {
                    //if the transaction is Buy
                      var message;
                    if (window.action == window.ACTION_BUY){
                        message = gettext('Buy order placed successfully');
                    }
                    //if the transaction is Sell
                    else{
                        message = gettext('Sell order placed successfully');

                    }
                    toastr.success(message);
                    $('.successOrder').html($(data));
                    $('#orderSuccessModal').modal({backdrop: 'static'});

                },
                error: function () {
                	var message = gettext('Something went wrong. Please, try again.');
                    toastr.error(message);
                }
            });

        });

      $('.make-payment').on('click', function () {
            var verifyPayload = {
                'order_id': $('.trade-type').val(),
                'csrfmiddlewaretoken': $('#csrfmiddlewaretoken').val(),
                'amount-cash': $('.amount-cash').val(),
                'currency_from': $('.currency-from').val(),
            };

            $.ajax({
                type: 'post',
                url: paymentAjax,
                dataType: 'text',
                data: verifyPayload,
                contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
                success: function (data) {
                    $('.paymentMethodsHead').addClass('hidden');
                    $('.paymentMethods').addClass('hidden');
                    $('.paymentSuccess').removeClass('hidden').html($(data));
                    $('.next-step').click();
                   // loadPaymenMethods(paymentMethodsEndpoint);
                },
                error: function () {
                	var message = gettext('Something went wrong. Please, try again.');
                    toastr.error(message);
                }
            });

        });

        $(document).on('click', '.buy .payment-type-trigger', function () {

            paymentType = $(this).data('label');
            actualPaymentType = $(this).data('type');
            preferenceIdentifier = $(this).data('identifier');
            $('.payment-preference-confirm').text(paymentType);
            $('.payment-preference-actual').text(actualPaymentType);
            $('.payment-preference-identifier-confirm').text(preferenceIdentifier);
            $('#PayMethModal').modal('toggle');
            $('.payment-method').val(paymentType);
            orderObject.changeState(null, 'next');
        });

        $(document).on('click', '.payment-type-trigger-footer', function () {
            $('.supporetd_payment').addClass('hidden');
            paymentType = $(this).data('type');
            preferenceIdentifier = $(this).data('identifier');
            $('.payment-preference-confirm').text(paymentType);
            $('.payment-preference-identifier-confirm').text(preferenceIdentifier);
            // $('#PayMethModal').modal('toggle');
            $('.payment-method').val(paymentType);
            orderObject.changeState(null, 'next');
            $('.footerpay').addClass('hidden');
            $('.buy-go').removeClass('hidden');
            $('.sell-go').addClass('hidden');
            window.action = window.ACTION_BUY;
            $('.next-step')
                .removeClass('btn-info')
                .removeClass('btn-danger')
                .addClass('btn-success');
        });

        $('.sell .payment-type-trigger').on('click', function () {
            paymentType = $(this).data('type').toLocaleLowerCase();
            $('.payment-preference-confirm').text(paymentType);
            $('#UserAccountModal').modal('toggle');
            if (paymentType === 'c2c') {
                $('#CardSellModal').modal('toggle');
            } else if(paymentType === 'qiwi') {
                $('#QiwiSellModal').modal('toggle');
            }
            else if(paymentType === 'paypal') {
                if($('#PaypalSellModal')) {
                    ('#PaypalSellModal').modal('toggle');
                }
            }
            else {
                $('.payment-method').val(paymentType);
            }
        });

        $('.sellMethModal .back').click(function () {
            $(this).closest('.modal').modal('toggle');
            $('#UserAccountModal').modal('toggle');
        });

        $('.payment-widget .val').on('keyup, keydown', function() {
            var val = $(this).closest('.val');
            if (!val.val().length) {
               $(this).removeClass('error').removeClass('valid');
                return;
            }
           if (val.hasClass('jp-card-invalid')) {
                $(this).removeClass('valid').addClass('error');
                // $('.save-card').addClass('disabled');
            } else {
               $(this).removeClass('error').addClass('valid');
               // $('.save-card').removeClass('disabled');
           }

        });

        $('.payment-widget .save-card').on('click', function () {
            $('.supporetd_payment').addClass('hidden');
            // TODO: Add handling for qiwi wallet with .intlTelInput('getNumber')
            if ($(this).hasClass('disabled')) {
                return false;
            }

            var form = $(this).closest('.modal-body');

            preferenceIdentifier = form.find('.val').val();
            preferenceOwner = form.find('.name').val();

            $('.payment-preference-owner').val(preferenceOwner);
            $('.payment-preference-identifier').val(preferenceIdentifier);
            $('.payment-preference-identifier-confirm').text(preferenceIdentifier);

            $(this).closest('.modal').modal('hide');
            
            setTimeout(function () {
                orderObject.changeState(null, 'next');
            }, 600);
        });
    });

    //for test selenium
    function submit_phone(){
        var apiRoot = '/en/api/v1',
            menuEndpoint = apiRoot + '/menu',
            breadcrumbsEndpoint = apiRoot + '/breadcrumbs',
            validatePhoneEndpoint = '/en/profile/verifyPhone/';
            var verifyPayload = {
                token: $('#verification_code').val(),
                phone: $('.register .phone').val()
            };
            $.ajax({
                type: 'POST',
                url: validatePhoneEndpoint,
                data: verifyPayload,
                success: function (data) {
                    if (data.status === 'OK') {
                        orderObject.reloadRoleRelatedElements(menuEndpoint, breadcrumbsEndpoint);
                        orderObject.changeState('next');
                    } else {
                	    var message = gettext('The code you sent was incorrect. Please, try again.');
                        toastr.error(message);
                    }
                },
                error: function () {
                	var message = gettext('Something went wrong. Please, try again.');
                    toastr.error(message);
                }
            });

    }

    window.submit_phone=submit_phone;
} (window, window.jQuery)); //jshint ignore:line

$(document).ready(function() {
    $('.supporetd_payment').removeClass('hidden');

});


   
},{"./modules/captcha.js":2,"./modules/orders.js":4,"./modules/payment.js":5}],2:[function(require,module,exports){
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
},{}],3:[function(require,module,exports){
!(function(window ,$) {
    "use strict";

    var apiRoot = '/en/api/v1',
        chartDataRaw,
        tickerHistoryUrl = apiRoot +'/price/history',
        tickerLatestUrl = apiRoot + '/price/latest';

    function responseToChart(data) {
        var i,
            resRub = [],
            resUsd = [],
            resEur = [];

        for (i = 0; i < data.length; i+=2) {
            var sell = data[i],
            buy = data[i + 1];
            if(!!sell && !!buy) {
                resRub.push([Date.parse(sell.created_on), buy.price_rub_formatted, sell.price_rub_formatted]);
                resUsd.push([Date.parse(sell.created_on), buy.price_usd_formatted, sell.price_usd_formatted]);
                resEur.push([Date.parse(sell.created_on), buy.price_eur_formatted, sell.price_eur_formatted]);
            }
        }
        return {
            rub: resRub,
            usd: resUsd,
            eur: resEur
        };
    }

    function renderChart (currency, hours) {
        var actualUrl = tickerHistoryUrl;
        if (hours) {
            actualUrl = actualUrl + '?hours=' + hours;
        }
         $.get(actualUrl, function(resdata) {
            chartDataRaw = resdata;
            var data = responseToChart(resdata)[currency];
          $('#container-graph').highcharts({

                chart: {
                    type: 'arearange',
                    zoomType: 'x',
                    style: {
                        fontFamily: 'Gotham'
                    },
                    backgroundColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
                        stops: [
                            [0, '#F3F3F3'],
                            [1, '#F3F3F3']
                        ]
                    },
                    events : {
                        load : function () {
                            // set up the updating of the chart each second
                            $('.highcharts-credits').remove();
                            var series = this.series[0];
                            setInterval(function () {
                                $.get(tickerLatestUrl, function (resdata) {
                                    var lastdata = responseToChart(resdata)[currency];
                                    if ( chartDataRaw.length && parseInt(resdata[0].unix_time) >
                                         parseInt(chartDataRaw[chartDataRaw.length - 1].unix_time)
                                    ) {
                                        //Only update if a ticker 'tick' had occured
                                        var _lastadata = lastdata[0];
                                        if (_lastadata[1] > _lastadata[2])
                                        {
                                            var a= _lastadata[1];
                                            _lastadata[1] = _lastadata[2];
                                            _lastadata[2] = a;
                                        }
                                        series.addPoint(_lastadata, true, true);
                                        Array.prototype.push.apply(chartDataRaw, resdata);
                                    }
                                });
                        }, 1000 * 30);
                      }
                    }
                },

                title: {
                    text: 'BTC/' + currency.toUpperCase()
                },

                xAxis: {
                    type: 'datetime',
                    dateTimeLabelFormats: {
                       day: '%e %b',
                        hour: '%H %M'

                    }
                },
                yAxis: {
                    title: {
                        text: null
                    }
                },

                tooltip: {
                    crosshairs: true,
                    shared: true,
                    valueSuffix: ' ' + currency.toLocaleUpperCase()
                },

                legend: {
                    enabled: false
                },

                series: [{
                    name: currency.toLowerCase() === 'rub' ? 'цена' : 'Price',
                    data: data,
                    color: '#8cc63f',
                    // TODO: fix this! make dynamic
                    pointInterval: 3600 * 1000
                }]
            });
        });
    }

    module.exports = {
        responseToChart:responseToChart,
        renderChart: renderChart,
        apiRoot: apiRoot,
        chartDataRaw: chartDataRaw,
        tickerHistoryUrl: tickerHistoryUrl,
        tickerLatestUrl: tickerLatestUrl
    };
}(window, window.jQuery)); //jshint ignore:line

},{}],4:[function(require,module,exports){
!(function(window, $) {
    "use strict";

      // Required modules
     var chartObject = require("./chart.js"),
         registerObject = require("./register.js"),
         googleObject = require('./captcha.js'),
         animationDelay = 3000;


    function updateOrder (elem, isInitial, currency, cb) {
        var val,
            rate,
            amountCoin = $('.amount-coin'),
            amountCashConfirm = 0,
                floor = 100000000;

        isInitial = isInitial || !elem.val().trim();
        val = isInitial ? elem.attr('placeholder') : elem.val();
        val = parseFloat(val);
        if (!val) {
            return;
        }

        $.get(chartObject.tickerLatestUrl, function(data) {
            // TODO: protect against NaN
            updatePrice(getPrice(data[window.ACTION_BUY], currency), $('.rate-buy'));
            updatePrice(getPrice(data[window.ACTION_SELL], currency), $('.rate-sell'));
            rate = data[window.action]['price_' + currency + '_formatted'];
            var btcAmount,
                cashAmount;
            if (elem.hasClass('amount-coin')) {
                btcAmount = val.toFixed(8);
                cashAmount = (rate * btcAmount).toFixed(2);
                amountCashConfirm = cashAmount;
                $(this).val(btcAmount);
                if (isInitial) {
                    $('.amount-cash').attr('placeholder', cashAmount);
                } else {
                    $('.amount-cash').val(cashAmount);
                    $('.amount-coin').val(btcAmount);
                }
            } else {
                btcAmount = Math.floor(val / rate * floor) / floor;
                btcAmount = btcAmount.toFixed(8);
                if (isInitial) {
                    $('.amount-coin').attr('placeholder', btcAmount);
                } else {
                    $('.amount-coin').val(btcAmount);
                }
            }
            $('.btc-amount-confirm').text(amountCoin.val()); // add
            $('.cash-amount-confirm').text(amountCashConfirm); //add

            // cb && cb();
            if(cb) cb();
        });
    }

    //order.js

    function updatePrice (price, elem) {
        var currentPriceText = elem.html().trim(),
            currentPrice,
            isReasonableChange;

        if (currentPriceText !== '') {
            currentPrice = parseFloat(currentPriceText);
        } else {
            elem.html(price);
            return;
        }
        // TODO: refactor this logic
        isReasonableChange = price < currentPrice * 1.05;
        if (currentPrice < price && isReasonableChange) {
            animatePrice(price, elem, true);
        }
        else if (!isReasonableChange) {
            setPrice(elem, price);
        }

        isReasonableChange = price * 1.05 > currentPrice;
        if (currentPrice > price && isReasonableChange) {
            animatePrice(price, elem);
        }
        else if (!isReasonableChange) {
            setPrice(elem, price);
        }
    }

    // order.js
    function animatePrice (price, elem, isRaise) {
        var animationClass = isRaise ? 'up' : 'down';
        elem.addClass(animationClass).delay(animationDelay).queue(function (next) {
                        setPrice(elem, price).delay(animationDelay / 2).queue(function(next) {
                elem.removeClass(animationClass);
                next();
            });
            next();
        });
    }

    //order.js
    function getPrice (data, currency) {
        return data['price_' + currency + '_formatted'];
    }

    function setCurrency (elem, currency) {
        if (elem && elem.hasClass('currency_pair')) {
            $('.currency_to').val(elem.data('crypto'));

        }

        $('.currency').html(currency.toUpperCase());
        chartObject.renderChart(currency, $("#graph-range").val());
    }

    function setPrice(elem, price) {
        elem.each(function () {
            if ($(this).hasClass('amount-cash')) {
                price = price * $('.amount-coin');
                price = Math.round(price * 100) / 100;
            } else {
                $(this).html(price);
            }
        });

        return elem;
    }

    function setButtonDefaultState (tabId) {
        if (tabId === 'menu2') {
            googleObject.doRender();                 
            var modifier = window.ACTION_SELL ? 'btn-danger' : 'btn-success';
            $('.next-step').removeClass('btn-info').addClass(modifier);                        
        } else {
            $('.next-step').removeClass('btn-success').removeClass('btn-danger').addClass('btn-info');
        }
        $('.btn-circle.btn-info')
            .removeClass('btn-info')
            .addClass('btn-default');
    }

    function toggleBuyModal () {
        $("#PayMethModal").modal('toggle');
    }

    function toggleSellModal () {
        try{
            $("#card-form").card({
                container: '.card-wrapper',
                width: 200,
                placeholders: {
                    number: '•••• •••• •••• ••••',
                    name: 'Ivan Ivanov',
                    expiry: '••/••',
                    cvc: '•••'
                }
            });
        }
        catch(e) {}
        $("#UserAccountModal").modal({backdrop: "static"});
    }

    function changeState (e, action) {       
        if (e) {
            e.preventDefault();
        }
        if ( $(this).hasClass('disabled') ) {// jshint ignore:line
            //todo: allow user to buy placeholder value or block 'next'?
            return;
        }

        if (!$('.payment-preference-confirm').html().trim()) {
            if (window.action == window.ACTION_BUY){
                toggleBuyModal();
            } else {
                toggleSellModal();
            }            
            return;
        }

        var valElem = $('.amount-coin'),
            val;
        if (!valElem.val().trim()) {
            //set placeholder as value.
            val = valElem.attr('placeholder').trim();
            valElem.val(val).trigger('change');
            $('.btc-amount-confirm').html(val);
        }

        var paneClass = '.tab-pane',
            tab = $('.tab-pane.active'),
            action = action || $(this).hasClass('next-step') ? 'next' : 'prev',// jshint ignore:line
            nextStateId = tab[action](paneClass).attr('id'),
            nextState = $('[href="#'+ nextStateId +'"]'),
            nextStateTrigger = $('#' + nextStateId),
            menuPrefix = "menu",
            numericId = parseInt(nextStateId.replace(menuPrefix, '')),
            currStateId = menuPrefix + (numericId - 1),
            currState =  $('[href="#'+ currStateId +'"]');
        //skip disabled state, check if at the end
        if(nextState.hasClass('disabled') &&
            numericId < $(".process-step").length &&
            numericId > 1) {
            changeState(null, action);            
        }


        if (nextStateTrigger.hasClass('hidden')) {
            nextStateTrigger.removeClass('hidden');
        }


        if ( !registerObject.canProceedtoRegister(currStateId) ){
            $('.trigger-buy').trigger('click', true);
        } else {
            setButtonDefaultState(nextStateId);

            currState
                .addClass('completed');

            nextState
                .tab('show');
            window.scrollTo(0, 0);
        }
        

        $(window).trigger('resize');
    }

    function reloadRoleRelatedElements (menuEndpoint) {
        $.get(menuEndpoint, function (menu) {
            $(".menuContainer").html($(menu));
        });

        $(".process-step .btn")
            .removeClass('btn-info')
            .removeClass('disabled')
            .removeClass('disableClick')
            .addClass('btn-default');

        $(".step2 .btn")
            .addClass('btn-info')
            .addClass('disableClick');
    }

    function reloadCardsPerCurrency(currency, cardsModalEndpoint) {
        var _locale= $('.topright_selectbox').val();
        $.post(cardsModalEndpoint, {currency: currency, _locale: _locale }, function (data) {
            $('.paymentSelectionContainer').html($(data));
        });
    }

    module.exports = {
        updateOrder: updateOrder,
        updatePrice: updatePrice,
        animatePrice: animatePrice,
        getPrice: getPrice,
        setCurrency: setCurrency,
        setPrice: setPrice,
        setButtonDefaultState: setButtonDefaultState,
        changeState: changeState,
        reloadRoleRelatedElements: reloadRoleRelatedElements,
        reloadCardsPerCurrency: reloadCardsPerCurrency,
        toggleBuyModal: toggleBuyModal,
        toggleSellModal: toggleSellModal
    };
}(window, window.jQuery)); //jshint ignore:line

},{"./captcha.js":2,"./chart.js":3,"./register.js":6}],5:[function(require,module,exports){
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

},{}],6:[function(require,module,exports){
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
},{}]},{},[1]);
