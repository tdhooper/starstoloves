from __future__ import absolute_import
from difflib import SequenceMatcher
from copy import deepcopy
from operator import attrgetter
import pprint

from celery import shared_task

from .strategies import separate_search_strategy, combined_search_strategy



class Result():

    def __init__(self, track, score=None):
        self.track = track
        self._score = score

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value

    def __repr__(self):
        return str(self.__dict__)


def merge(first, second):
    results = []

    for result in first + second:

        matched_indices = [
            i for i, match in enumerate(results)
            if match.track == result.track
        ]

        if matched_indices:
            results[matched_indices[0]] = result
            continue

        results.append(result)
    
    return results


# TODO: consider listener count as well
# sort first by similarity, where +/- 0.2 is the same, then by listener
def score(track_name, artist_name, results):
    for result in results:
        result.score = sum([
            SequenceMatcher(None, track_name, result.track.track_name).ratio(),
            SequenceMatcher(None, artist_name, result.track.artist_name).ratio(),
        ]) * 0.5


def rank(results):
    return sorted(results, key=attrgetter('score'), reverse=True)


@shared_task
def search_lastfm(track_name, artist_name):
    threshold = 0.9
    strategies = [separate_search_strategy, combined_search_strategy]
    results = []
    for strategy in strategies:
        tracks = strategy(track_name, artist_name)
        if tracks:
            new_results = [Result(track) for track in tracks]
            results = merge(results, new_results)
            score(track_name, artist_name, results)
            results = rank(results)
            
            if results[0].score > threshold:
                break
    return [result.track for result in results]
