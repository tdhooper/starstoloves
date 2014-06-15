define(['jquery', 'result.view', 'result.model'], function($, ResultView, ResultModel) {
    "use strict";

    describe("a Result view", function() {

        var view,
            model,
            $el;

        beforeEach(function() {
            $el = $(jasmine.getFixtures().read('results-list.html'));
            model = new ResultModel({
                status: 'PENDING'
            });
            view = new ResultView({
                el: $('.js-result', $el).eq(3).get(0),
                model: model
            });
        });

        describe("when the model updates", function() {

            beforeEach(function() {
                model.set({
                    status: 'SUCCESS',
                    html: '<div class="js-result">somehtml</div>'
                });
            });

            it("replaces the element's html", function() {
                expect(view.$el.html()).toBe('somehtml');
                expect($('.js-result', $el).eq(3).html()).toBe('somehtml');
            });
        });
    });
});