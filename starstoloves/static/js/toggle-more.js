define(['jquery'], function($) {
    "use strict";

    var ToggleMore = function($el) {

        var that = this;

        that.start = function() {
            $el.on('click', '.js-toggle-more-toggle', function(evt) {
                var $group = $(evt.target).parents('.js-toggle-more');
                that.toggle($group);
                evt.preventDefault();
            });
            that.update();
        };

        that.update = function() {
            $('.js-toggle-more', $el).each(function(index, group) {
                var $group = $(group);
                if ( ! $group.data('toggleMoreActive')) {
                    that.add($group);
                }
            });
        }

        that.add = function($group) {
            $group.data('toggleMoreActive', true);
            $('.js-toggle-more-item', $group).eq(0).after('<li><a href="#" class="js-toggle-more-toggle"></a></li>');
            that.hide($group);
        };

        that.toggle = function($group) {
            if ($group.data('toggleClosed')) {
                that.show($group);
            } else {
                that.hide($group);
            }
        };

        that.hide = function($group) {
            var $items = $('.js-toggle-more-item', $group);
            $items.not(':first').addClass('hide');
            var count = $items.length - 1;
            $('.js-toggle-more-toggle', $group).text(count + " More");
            $group.data('toggleClosed', true);
        };

        that.show = function($group) {
            var $items = $('.js-toggle-more-item', $group);
            $items.not(':first').removeClass('hide');
            $('.js-toggle-more-toggle', $group).text("Hide");
            $group.data('toggleClosed', false);
        };

    };
    
    return ToggleMore;
});