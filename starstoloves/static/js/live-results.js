define([
    'jquery',
    'result.model',
    'result.view',
    'results.collection',
    'toggle-more'
], function(
    $,
    ResultModel,
    ResultView,
    Results,
    ToggleMore
) {
    "use strict";

    var LiveResults = function($el, url) {

        var that = this;
        var results;
        var toggleMore = new ToggleMore($el);

        that.start = function() {
            toggleMore.start();
            results = that.createResults();
            results.url = url;
            that.update();
            results.on('change', toggleMore.update);
        };

        that.createResults = function() {
            var resultModels = [],
                $result,
                model,
                view;

            $('.js-result', $el).each(function(index, result) {
                $result = $(result);
                model = new ResultModel({
                    status: $result.data('status'),
                    id: String($result.data('id'))
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
            var token = $el.data('csrf-token');

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
                var status = {};
                results.forEach(function(model) {
                    status[model.get('id')] = model.get('status')
                });
                results.fetch({
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': token
                    },
                    success: function() {
                        setTimeout(update, 100);
                    },
                    data: {
                        status: status
                    },
                    remove: false
                });
            };

            update();
        };
    };

    return LiveResults;
});