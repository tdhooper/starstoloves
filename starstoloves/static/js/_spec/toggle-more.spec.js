define(['jquery', 'toggle-more'], function($, ToggleMore) {
    "use strict";

    var testGroup = function(context) {

        it("hides all but the first item in the group", function() {
            expect($('.js-toggle-more-item:not(:first)', context.$active).is('.hide')).toBe(true);
            expect($('.js-toggle-more-item:first', context.$active).is('.hide')).toBe(false);
        });

        it("adds toggle links after the group", function() {
            expect(context.$active.next('a.js-toggle-more-toggle').length).toBe(1);
        });

        it("labels the toggle link as more", function() {
            expect(context.$active.next('.js-toggle-more-toggle').is(':contains(More)')).toBe(true); 
        });

        it("includes the number of hidden items in the toggle link", function() {
            expect(context.$active.next('.js-toggle-more-toggle').is(':contains(' + context.activeHidden + ')')).toBe(true);
        });

        describe("when the toggle link is clicked", function() {

            var evt;

            beforeEach(function() {
                evt = $.Event('click');
                context.$active.next('.js-toggle-more-toggle').trigger(evt);
            });

            it("prevents default", function() {
                expect(evt.isDefaultPrevented()).toBe(true);
            });

            it("shows all of the group's items", function() {
                expect($('.js-toggle-more-item.hide', context.$active).length).toBe(0);
            });

            it("labels the toggle link as hide", function() {
                expect(context.$active.next('.js-toggle-more-toggle').is(':contains(Hide)')).toBe(true); 
            });

            it("doesn't change other groups", function() {
                expect($('.js-toggle-more-item.hide', context.$inactive).length).toBe(context.inactiveHidden);
            });

            describe("when the toggle link is again", function() {

                beforeEach(function() {
                    context.$active.next('.js-toggle-more-toggle').trigger('click');
                });

                it("hides all but the first item in the group", function() {
                    expect($('.js-toggle-more-item:not(:first)', context.$active).is('.hide')).toBe(true);
                    expect($('.js-toggle-more-item:first', context.$active).is('.hide')).toBe(false);
                });

                it("labels the toggle link as more", function() {
                    expect(context.$active.next('.js-toggle-more-toggle').is(':contains(More)')).toBe(true); 
                });
            });
        });
    };

    describe("Toggle More", function() {

        var toggleMore,
            $el;

        beforeEach(function() {
            $el = $(jasmine.getFixtures().read('results-list.html'));
            toggleMore = new ToggleMore($el);
        });

        describe("when start is called", function() {
            
            var $groups;

            beforeEach(function() {
                toggleMore.start();
                $groups = $('.js-toggle-more', $el);
            });

            describe("test first group", function() {

                var context = {};

                beforeEach(function() {
                    context.$active = $groups.eq(0);
                    context.$inactive = $groups.eq(1);
                    context.activeHidden = 2;
                    context.inactiveHidden = 6;
                });

                testGroup(context);
            });

            describe("test second group", function() {

                var context = {};

                beforeEach(function() {
                    context.$active = $groups.eq(1);
                    context.$inactive = $groups.eq(0);
                    context.activeHidden = 6;
                    context.inactiveHidden = 2;
                });

                testGroup(context);
            });

            describe('when a group is added and update is called', function() {

                var $newGroup;

                beforeEach(function() {
                    $newGroup = $('\
                        <ul class="js-toggle-more">\
                            <li class="js-toggle-more-item">A</li>\
                            <li class="js-toggle-more-item">B</li>\
                            <li class="js-toggle-more-item">C</li>\
                            <li class="js-toggle-more-item">D</li>\
                        </ul>\
                    ');
                    $('.js-result', $el).eq(2).empty().append($newGroup);
                    toggleMore.update();
                });

                describe("test new group", function() {

                    var context = {};

                    beforeEach(function() {
                        context.$active = $newGroup;
                        context.$inactive = $groups;
                        context.activeHidden = 3;
                        context.inactiveHidden = 8;
                    });

                    testGroup(context);
                });

                it("doesn't re-initialise the other groups", function() {
                    expect($groups.eq(0).next('.js-toggle-more-toggle').length).toBe(1);
                    expect($groups.eq(1).next('.js-toggle-more-toggle').length).toBe(1);
                });
            });
        });
    });
});