define(['backbone', 'jquery'], function(Backbone, $) {
    "use strict";

    var Result = Backbone.View.extend({
        initialize: function() {
            this.model.on('change', this.render, this);
        },
        render: function () {
            var $newEl = $(this.model.get('html'));
            this.$el.replaceWith($newEl);
            this.setElement($newEl);
        }
    });

    return Result;
});