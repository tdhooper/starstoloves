define([
    'jquery',
    'result.model',
    'result.view',
    'results.collection'
], function(
    $,
    ResultModel,
    ResultView,
    Results
) {
    "use strict";

    var LiveResults = function($el, url) {

        var that = this;
        var results;

        that.start = function() {
            results = that.createResults();
            results.url = url;
            that.update();
        };

        that.createResults = function() {
            var resultModels = [],
                $result,
                model,
                view;

            $('.js-result', $el).each(function(index, result) {
                $result = $(result);
                model = new ResultModel({
                    status: $result.data('status')
                });
                view = new ResultView({
                    el: result,
                    model: model
                });
                resultModels.push(model);
            });

            return new Results(resultModels);
        };

        that.update = function() {

            var isComplete = function() {
                var pending = results.detect(function(model) {
                    return model.get('status') == 'PENDING';
                });
                return ! pending;
            };

            var update = function() {
                if (isComplete()) {
                    return;
                }
                results.fetch({
                    success: function() {
                        setTimeout(update, 100);
                    }
                });
            };

            update();
        };
    };

    return LiveResults;
});