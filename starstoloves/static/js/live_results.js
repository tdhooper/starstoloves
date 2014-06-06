"use strict";

define(['results_broadcaster'], function(ResultsBroadcaster) {
    
    var LiveResults = {};

    LiveResults.create = function(spec) {
        ResultsBroadcaster.create(spec);
    };

    return LiveResults;

});