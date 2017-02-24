describe("Profile function", function() {
    
    jasmine.getFixtures().fixturesPath = 'base/static/js/tests/fixtures/';

    describe("verifyPhone", function() {
        beforeEach(function () {
            loadFixtures('ProfileFixture.html');

            spyOn($, "ajax").and.callFake(function() {
                var dfd = jQuery.Deferred();
                dfd.resolve('{"error":"error"}');
                return dfd.promise();
            });
        });

        it("should make an AJAX request to the URL specified on the data attribute of the button", function() {
            spyOnEvent('#verify_phone_now', 'click');

            $("#verify_phone_now").on("click", verifyPhone);
            $('#verify_phone_now').trigger('click');

            expect('click').toHaveBeenTriggeredOn('#verify_phone_now');
            expect($.ajax.calls.mostRecent().args[0].url).toEqual('/profile/verifyPhone/');            
        });

        it("should show 'loading...' while processing", function() {
            verifyPhone();
            expect($('#alert_verifying_phone')[0]).toBeVisible();
            expect($('#alert_phone_not_verified')[0]).not.toBeVisible();
        });

        it("should execute the callback function on success", function () {
            // can't figure how to test this...  
        });
    });

});