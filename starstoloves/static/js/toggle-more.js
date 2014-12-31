define(['jquery'], function($) {
    "use strict";

    var ToggleMore = function($el) {

        var that = this;

        that.start = function() {
            $el.on('click', '.js-toggle-more-toggle', function(evt) {
                var $group = $(this).prev('.js-toggle-more');
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
            $group.after('<a href="#" class="toggle-more-toggle js-toggle-more-toggle"><span></span></a>');
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
            $group.next('.js-toggle-more-toggle').find('span').text(count + " More");
            $group.data('toggleClosed', true);
        };

        that.show = function($group) {
            var $items = $('.js-toggle-more-item', $group);
            $items.not(':first').removeClass('hide');
            $group.next('.js-toggle-more-toggle').find('span').text("Hide");
            $group.data('toggleClosed', false);
        };

    };
    
    return ToggleMore;
});