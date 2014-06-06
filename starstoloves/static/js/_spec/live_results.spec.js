"use strict";

define(['Squire', 'jquery'], function(Squire, $) {

    describe('Live Results', function() {

        var LiveResults,
            ResultsBroadcaster;

        beforeEach(function(done) {

            ResultsBroadcaster = jasmine.createSpyObj('ResultsBroadcaster', ['create']);
            
            var injector = new Squire();
            injector.mock('results_broadcaster', ResultsBroadcaster);

            injector.require(['live_results'], function(MockedLiveResults) {
                LiveResults = MockedLiveResults
                done();
            });
        });

        describe('when create is called', function() {

            var container;

            beforeEach(function() {
                container = $('<div></div>');
                LiveResults.create({
                    container: container
                });
            });

            it('creates a ResultsBroadcaster', function() {
                expect(ResultsBroadcaster.create).toHaveBeenCalledWith({
                    container: container
                });
            });
        });
    });
});

/**

SKETCH

ResultsBroadcaster
* onNewResults(callback)
- callback with results as they arrive
- stores state and index of each task
- adds progress spinner
- polls server for updates
-- sends up it's current status for each item
-- just returns updated items (different status)
-- when all are done, stop polling

ResultsUpdater
* update(results)
- match them to element by index
- appends result element

MoreToggle
* add(resultContainer)
- Hides results when initialised
- Adds toggle button for each results list
- allows them to be toggled on/off
- indicates if there's a loved track inside
- shows number of extra results

**/