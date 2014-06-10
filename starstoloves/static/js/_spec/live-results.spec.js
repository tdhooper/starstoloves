define(['Squire', 'jquery'], function(Squire, $) {
    "use strict";

    describe("Live Results", function() {

        var results,
            ResultView,
            liveResults,
            resultElements;

        beforeEach(function(done) {
            var $el = $(jasmine.getFixtures().read('results-list.html'));
            resultElements = $('.js-result', $el);
            var injector = new Squire();

            ResultView = jasmine.createSpy('ResultView');
            injector.mock('result.view', ResultView);            
            
            injector.require(['live-results'], function(LiveResults) {
                liveResults = new LiveResults($el, 'some-url');
                var createResults = liveResults.createResults;
                spyOn(liveResults, 'createResults').and.callFake(function() {
                    results = createResults();
                    spyOn(results, 'fetch');
                    return results;
                });
                done();
            });
        });

        describe("when start is called", function() {

            var models;

            beforeEach(function() {
                liveResults.start();
            });

            it("initialises a Results collection with Result models for the existing html", function() {
                expect(liveResults.createResults).toHaveBeenCalled();
                var modelsData = results.models.map(function(model) {
                    return model.toJSON();
                });
                expect(modelsData).toEqual([
                    {status: 'SUCCESS'},
                    {status: 'FAILED'},
                    {status: 'SUCCESS'},
                    {status: 'PENDING'}
                ]);
            });

            it("initialises Result views with existing html and attaches the models", function() {
                expect(ResultView).toHaveBeenCalledWith({el: resultElements[0], model: results.models[0]});
                expect(ResultView).toHaveBeenCalledWith({el: resultElements[1], model: results.models[1]});
                expect(ResultView).toHaveBeenCalledWith({el: resultElements[2], model: results.models[2]});
                expect(ResultView).toHaveBeenCalledWith({el: resultElements[3], model: results.models[3]});
            });

            it('passes the url to the Results collection', function() {
                expect(results.url).toEqual('some-url');
            });

            it('fetches the latest results', function() {
                expect(results.fetch).toHaveBeenCalled();
            });

            describe('when the fetch succeeds', function() {

                beforeEach(function() {
                    jasmine.clock().install();
                    results.fetch.calls.mostRecent().args[0].success();
                });

                afterEach(function() {
                    jasmine.clock().uninstall();
                });

                it('does not immediately do another fetch', function() {
                    expect(results.fetch.calls.count()).toBe(1);
                });

                it('does another fetch after an interval', function() {
                    jasmine.clock().tick(101);
                    expect(results.fetch.calls.count()).toBe(2);
                });

                it('continues to fetch at intervals', function() {
                    jasmine.clock().tick(101);
                    results.fetch.calls.mostRecent().args[0].success();
                    jasmine.clock().tick(101);
                    results.fetch.calls.mostRecent().args[0].success();
                    jasmine.clock().tick(101);
                    expect(results.fetch.calls.count()).toBe(4)
                });

                describe('when no more models are pending', function() {

                    beforeEach(function() {
                        results.models.forEach(function(model) {
                            model.set({
                                status: 'not pending'
                            });
                        });
                    });

                    it('stops fetching', function() {
                        jasmine.clock().tick(101);
                        expect(results.fetch.calls.count()).toBe(1);
                    });
                });
            });
        });
    });
});

/**

SKETCH

ResultsList (Collection)
- polls server for updates
-- sends up it's current status for each item
-- just returns updated items (different status)
-- when all are done, stop polling

ResultModel (Model)
- updates view on update
- stores state and index of each task

ResultView
- adds progress spinner
- onUpdate
-- appends result element
-- removes progress spinner
- onSuccess
-- add tp MoreToggle

MoreToggle
- Init with list container
- add(resultContainer)
-- Hides results when initialised
-- Adds toggle button for each results list
-- allows them to be toggled on/off
-- indicates if there's a loved track inside
-- shows number of extra results

**/