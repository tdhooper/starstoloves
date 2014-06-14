define(['Squire', 'jquery', 'backbone'], function(Squire, $, Backbone) {
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

            spyOn(Backbone, 'sync');

            ResultView = jasmine.createSpy('ResultView');
            injector.mock('result.view', ResultView);
            injector.mock('backbone', Backbone);

            injector.require(['live-results'], function(LiveResults) {
                liveResults = new LiveResults($el, 'some-url');
                var createResults = liveResults.createResults;
                spyOn(liveResults, 'createResults').and.callFake(function() {
                    results = createResults();
                    spyOn(results, 'fetch').and.callThrough();
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
                expect(results.toJSON()).toEqual([
                    {status: 'SUCCESS', id: '0'},
                    {status: 'FAILED',  id: '1'},
                    {status: 'SUCCESS', id: '2'},
                    {status: 'PENDING', id: '3'},
                    {status: 'PENDING', id: '4'}
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

            it('sends the current state with the fetch', function() {
                var options = results.fetch.calls.mostRecent().args[0]
                expect(options.data.state).toEqual([
                    {status: 'SUCCESS', id: '0'},
                    {status: 'FAILED',  id: '1'},
                    {status: 'SUCCESS', id: '2'},
                    {status: 'PENDING', id: '3'},
                    {status: 'PENDING', id: '4'}
                ]);
            });

            describe('when the fetch succeeds', function() {

                var triggerSuccess = function(data) {
                    Backbone.sync.calls.mostRecent().args[2].success(data);
                }

                var responseData;

                beforeEach(function() {
                    jasmine.clock().install();
                    responseData = [
                        {status: 'SUCCESS', id: '3'}
                    ];
                    triggerSuccess(responseData);
                });

                afterEach(function() {
                    jasmine.clock().uninstall();
                });

                it('updates the models', function() {
                    expect(results.toJSON()).toEqual([
                        {status: 'SUCCESS', id: '0'},
                        {status: 'FAILED',  id: '1'},
                        {status: 'SUCCESS', id: '2'},
                        {status: 'SUCCESS', id: '3'},
                        {status: 'PENDING', id: '4'}
                    ]);
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
                    triggerSuccess(responseData);
                    jasmine.clock().tick(101);
                    triggerSuccess(responseData);
                    jasmine.clock().tick(101);
                    expect(results.fetch.calls.count()).toBe(4)
                });

                describe('when no more models are pending', function() {

                    beforeEach(function() {
                        triggerSuccess([
                            {status: 'FAILED', id: '4'}
                        ]);
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