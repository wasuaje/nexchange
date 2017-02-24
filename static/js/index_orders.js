!(function (window, $) {
    "use strict";

    $(document).ready(function() {

        function withdraw_address_error(msg) {
            $(".withdraw_address_err:visible").html(msg);
        }


        $('[data-toggle="popover"]').on('inserted.bs.popover', function () {

            var span = $(this);
            var popover = $(this).data("bs.popover");
            var forms = popover.tip().find("form");

            var form_update = forms.first();
            var form_create = forms.last();

            var select_addresses = form_update.find("select:first");
            var input_address = form_create.find("input[type=text]:first");
            var btnSetAddress = form_update.find("button[type=submit]:first");


            var close_popover = function() {
                span.trigger("click");
            };

            var toggle_forms = function() {
                $(".set_withdraw_address").toggle();
                $(".create_withdraw_address").toggle();
            };

            // Links that closes the popover
            $(".closepopover").click(close_popover);

            // Buttons to toggle between select/add address
            $(".toggle_widthdraw_address_form").click(toggle_forms);

            // Copy options from the template object
            // (it may have changed duo to new addresses beend added)
            var options = $("#popover-template select:first > option").clone();
            select_addresses.empty().append(options);

            // if there is one address set for this order, select it
            select_addresses.children("option").each(function(index, option){
                if ( $.trim($(option).text()) === $.trim(span.html()) ) {
                    select_addresses.prop('selectedIndex', index);
                }
            });

            /**
             * The form which handles 'select one of the existing addresses'
             */
            form_update.submit(function(event) {
                event.preventDefault();
                withdraw_address_error(''); // clean up

                var selected = select_addresses.find("option:selected").first();
                if (selected.val() === "") {
                    withdraw_address_error("You must select an address first.");
                    return false;
                }

                btnSetAddress.button('loading');

                $.post( span.data('url-update'), {'value': selected.val()}, function( data ) {
                    if (data.status === 'OK') {
                        span.html(selected.text());
                        span.trigger("click");
                    } else {
                        withdraw_address_error(UNKNOW_ERROR);
                    }

                    btnSetAddress.button('reset');
                }).fail(function(jqXHR){
                    if (jqXHR.status == 403) {
                        withdraw_address_error(jqXHR.responseText);
                    } else if(data.status === 'ERR') {
                        withdraw_address_error(data.msg);
                    } else {
                        withdraw_address_error(UNKNOW_ERROR);
                    }
                    btnSetAddress.button('reset');
                });
            });

            /**
             * The form which handles 'add a new address'
             */
            form_create.submit(function(event) {
                event.preventDefault();
                withdraw_address_error(''); // clean up

                if (input_address.val() === "") {
                    withdraw_address_error("You must insert an address first.");
                    return false;
                }

                var btn = form_create.find("button[type=submit]:first");
                btn.button('loading');

                $.post( span.data('url-create'), {'value': input_address.val()}, function( data ) {
                    if (data.status === 'OK') {

                        // Add this address as an option to the select
                        select_addresses
                            .append($("<option></option>")
                            .attr("value", data.pk)
                            .text(input_address.val()));
                        select_addresses.val(data.pk);  // select it

                        // updates the template element
                        $("#popover-template select:first")
                            .append($("<option></option>")
                            .attr("value", data.pk)
                            .text(input_address.val()));

                        // clean up the input
                        input_address.val('');

                        // get back to select form and submit it
                        form_create.find(".toggle_withdraw_address_form:first").trigger("click");
                        btnSetAddress.trigger("click");

                    } else if(data.status === 'ERR') {
                        withdraw_address_error(data.msg);
                    } else {
                        withdraw_address_error(UNKNOW_ERROR);
                    }

                    btn.button('reset');
                }).fail(function(jqXHR){
                    if (jqXHR.status == 403) {
                        withdraw_address_error(jqXHR.responseText);
                    } else {
                        withdraw_address_error(UNKNOW_ERROR);
                    }
                    btn.button('reset');
                });
            });


            // Defines which form will show up when popover opens
            if ( options.length > 1 ) {
                popover.tip().find(".set_withdraw_address:first").toggle();
                popover.tip().find(".cancel_btn").click(toggle_forms);
            } else {
                popover.tip().find(".create_withdraw_address:first").toggle();
                popover.tip().find(".cancel_btn").click(close_popover);
            }
        });

        /**
         * Handles the payment confirmation
         */
        $('.checkbox-inline input').change(function() {
            var pk = $(this).data('pk');
            var spin = $("#spin_confirming_" + pk );
            var container = $(this).closest('.checkbox-inline');
            var toggle = this;
            var withdraw_address = $(".withdraw_address[data-pk=" + pk + "]"); // withdraw_address for this orders

            var treatError = function(msg) {
                // Sets the toggle back and notifies the user about the error
                if ( $(toggle).prop('checked') ){
                    $(toggle).data('bs.toggle').off(true);
                } else {
                    $(toggle).data('bs.toggle').on(true);
                }

                $(spin).hide();
                $(container).show();
                toastr.error(msg);
            };

            $.post( $(this).data('url'), {'paid': $(this).prop('checked')}, function( data ) {

                if (data.status === 'OK') {
                    if (data.frozen) {
                        // so user wont change any payment confirmation
                        $(toggle).bootstrapToggle('disable');

                        // so user cannot edit withdraw_address
                        $("#td-frozen-withdraw-" + pk + " .frozen").html($(withdraw_address).html());
                        $("#td-withdraw-" + pk).hide();
                        $("#td-frozen-withdraw-" + pk).show();
                    }

                    $(spin).hide();
                    $(container).show();

                } else {
                    treatError(UNKNOW_ERROR);
                }

            }).fail(function(jqXHR){
                if (jqXHR.status == 403) {
                    treatError(jqXHR.responseText);
                } else {
                    treatError(UNKNOW_ERROR);
                }
            });

        });

    });
}(window, window.jQuery)); //jshint ignore:line