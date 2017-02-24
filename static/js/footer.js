!(function (window, $) {
    $(window).bind("load", function () {

        function positionFooter() {
            var footerHeight = $('.footer').outerHeight(),
            bottomFooterHeight = $('.footer_bottom').height(),
            containerHeight = $('.container').height(),
            spacerHeight = $(window).height() - containerHeight -
                footerHeight - bottomFooterHeight;

            if (spacerHeight) {
                $('.spacer').css('height', spacerHeight);
            }
        }

        $(document).ready(positionFooter);

    });
}(window, window.$)); //jshint ignore:line