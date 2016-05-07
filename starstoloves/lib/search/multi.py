from difflib import SequenceMatcher
from copy import deepcopy
from operator import attrgetter
import pprint

from starstoloves.lib.lastfm import lastfm_app
from starstoloves.lib.track.lastfm_track import LastfmTrack
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


def score(track_name, artist_name, results):

    for result in results:

        track_score = SequenceMatcher(
            None,
            track_name.upper(),
            result.track.track_name.upper()
        ).ratio()

        artist_score = SequenceMatcher(
            None,
            artist_name.upper(),
            result.track.artist_name.upper()
        ).ratio()

        result.score = sum([track_score, artist_score]) * 0.5


def rank(results):
    s = results
    s = sorted(s, key=lambda result: result.track.listeners or 0, reverse=True)
    s = sorted(s, key=lambda result: round(result.score * 3), reverse=True)
    return s


def get_correction(track):
    response = lastfm_app.request('track', 'getcorrection', {
        'artist': track.artist_name,
        'track': track.track_name,
    })
    try:
        track_data = response['corrections']['correction']['track']
        return LastfmTrack(
            url=track_data['url'],
            track_name=track_data['name'],
            artist_name=track_data['artist']['name'],
        )
    except TypeError:
        return None


def multi_search(track_name, artist_name):
    threshold = 0.8
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

    tracks = [result.track for result in results]

    if tracks:
        correction = get_correction(tracks[0])
        if correction:
            tracks.insert(0, correction)

    return tracks
