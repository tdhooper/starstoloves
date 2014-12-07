import os
import json
from unittest.mock import call, MagicMock

import pytest

from starstoloves.lib.track.lastfm_track import LastfmTrack
from ..result import LastfmResultParser
from ..multi import (
    multi_search,
    Result,
    merge,
    score,
    rank,
)
from .fixtures import lastfm_app


threshold = 0.8


@pytest.fixture
def tracks():
    return [
        LastfmTrack(
            url='track_1_url',
            track_name='track_1_track',
            artist_name='track_1_artist',
        ),
        LastfmTrack(
            url='track_2_url',
            track_name='track_2_track',
            artist_name='track_2_artist',
        ),
        LastfmTrack(
            url='track_3_url',
            track_name='track_3_track',
            artist_name='track_3_artist',
        ),
        LastfmTrack(
            url='track_4_url',
            track_name='track_4_track',
            artist_name='track_4_artist',
        )
    ]


@pytest.fixture
def tracks_from_separate(tracks):
    return tracks[:2]


@pytest.fixture
def tracks_from_combined(tracks):
    return tracks[2:]


@pytest.fixture
def SequenceMatcher(create_patch):
    return create_patch('starstoloves.lib.search.multi.SequenceMatcher')


@pytest.fixture
def separate_search_patch(create_patch):
    patched = create_patch('starstoloves.lib.search.multi.separate_search_strategy')
    patched.return_value = None
    return patched


@pytest.fixture
def combined_search_patch(create_patch):
    patched = create_patch('starstoloves.lib.search.multi.combined_search_strategy')
    patched.return_value = None
    return patched


@pytest.fixture
def separate_search_has_tracks(separate_search_patch, tracks_from_separate):
    separate_search_patch.return_value = tracks_from_separate


@pytest.fixture
def combined_search_has_tracks(combined_search_patch, tracks_from_combined):
    combined_search_patch.return_value = tracks_from_combined


@pytest.fixture
def score_patch(create_patch):
    patched = create_patch('starstoloves.lib.search.multi.score')
    patched.side_effect = score
    return patched


@pytest.fixture
def rank_patch(create_patch):
    patched = create_patch('starstoloves.lib.search.multi.rank')
    patched.side_effect = rank
    return patched


@pytest.fixture
def merge_patch(create_patch):
    patched = create_patch('starstoloves.lib.search.multi.merge')
    patched.side_effect = merge
    return patched


@pytest.fixture
def set_scores(SequenceMatcher):
    def set_scores_method(score_map):
        def new_matcher(isjunk, a, b):
            matcher = MagicMock()
            matcher.ratio.return_value = score_map[b]
            return matcher
        SequenceMatcher.side_effect = new_matcher
    return set_scores_method


@pytest.fixture
def set_scores_from_class(request, set_scores):
    set_scores(request.instance.scores)


@pytest.fixture
def get_result_fixtures():
    def get_file(filename):
        path = os.path.join(
            os.path.dirname(__file__),
            'result_fixtures',
            filename
        )
        with open (path, 'r') as results_file:
            return json.loads(results_file.read())['results']
    return get_file


class TestResult():

    def test_it_exposes_parameters(self):
        track = LastfmTrack('track_1_url', 'track_1_track', 'track_1_artist')
        result = Result(track, 3)
        assert result.track == track
        assert result.score == 3

    def test_score_can_be_set(self):
        track = LastfmTrack('track_1_url', 'track_1_track', 'track_1_artist')
        result = Result(track)
        result.score = 5
        assert result.score == 5


class TestMerge():

    def test_merges(self):
        first = [
            Result(LastfmTrack('track_1_url', 'track_1_track', 'track_1_artist')),
            Result(LastfmTrack('track_2_url', 'track_2_track', 'track_2_artist')),
        ]
        second = [
            Result(LastfmTrack('track_3_url', 'track_3_track', 'track_3_artist')),
            Result(LastfmTrack('track_4_url', 'track_4_track', 'track_4_artist')),
        ]
        merged = merge(first, second)
        assert len(merged) is 4
        assert merged[0] is first[0]
        assert merged[1] is first[1]
        assert merged[2] is second[0]
        assert merged[3] is second[1]


    def test_removes_duplicates_preferring_second(self):
        first = [
            Result(LastfmTrack('track_1_url', 'track_1_track', 'track_1_artist')),
            Result(LastfmTrack('track_2_url', 'track_2_track', 'track_2_artist')),
        ]
        second = [
            Result(LastfmTrack('track_2_url', 'track_2_track', 'track_2_artist')),
            Result(LastfmTrack('track_3_url', 'track_3_track', 'track_3_artist')),
        ]
        merged = merge(first, second)
        assert len(merged) is 3
        assert merged[0] is first[0]
        assert merged[1] is second[0]
        assert merged[2] is second[1]


    def test_merges_with_empty_list(self):
        first = []
        second = [
            Result(LastfmTrack('track_1_url', 'track_1_track', 'track_1_artist')),
            Result(LastfmTrack('track_2_url', 'track_2_track', 'track_2_artist')),
        ]
        merged = merge(first, second)
        assert len(merged) is 2
        assert merged[0] is second[0]
        assert merged[1] is second[1]


class TestScore():

    def test_calculates_similarity_to_original_query(self, SequenceMatcher):
        result = Result(LastfmTrack('track_1_url', 'track_1_track', 'track_1_artist'))
        score('query_track', 'query_artist', [result])
        assert call(None, 'query_track', 'track_1_track') in SequenceMatcher.call_args_list
        assert call(None, 'query_artist', 'track_1_artist') in SequenceMatcher.call_args_list


    def test_adds_averaged_scores_to_results(self, set_scores):
        set_scores({
            'track_1_track': 5,
            'track_1_artist': 10,
        })

        result = Result(LastfmTrack('track_1_url', 'track_1_track', 'track_1_artist'))
        score('query_track', 'query_artist', [result])

        assert result.score == 7.5


class TestRank():

    def test_sorts_by_descending_score(self):
        results = [
            Result(LastfmTrack(''), .0),
            Result(LastfmTrack(''), .9),
            Result(LastfmTrack(''), .5),
        ]
        assert rank(results) == [
            results[1],
            results[2],
            results[0]
        ]


    def test_higher_listener_counts_float_to_top(self):
        results = [
            Result(LastfmTrack(url='', listeners=3), .0),
            Result(LastfmTrack(url='', listeners=2), .0),
            Result(LastfmTrack(url='', listeners=0), .5),
            Result(LastfmTrack(url='', listeners=1), .5),
        ]
        assert rank(results) == [
            results[3],
            results[2],
            results[0],
            results[1]
        ]


    def test_subtle_score_differences_do_not_trump_listener_counts(self):
        results = [
            Result(LastfmTrack(url='', listeners=1), .01),
            Result(LastfmTrack(url='', listeners=0), .02),
            Result(LastfmTrack(url='', listeners=1), .91),
            Result(LastfmTrack(url='', listeners=0), .92),
        ]
        assert rank(results) == [
            results[2],
            results[3],
            results[0],
            results[1]
        ]


    def test_subtle_listener_count_differences_do_not_trump_score(self):
        results = [
            Result(LastfmTrack(url='', listeners=10), .9),
            Result(LastfmTrack(url='', listeners=11), .0),
            Result(LastfmTrack(url='', listeners=98), .9),
            Result(LastfmTrack(url='', listeners=99), .0),
        ]
        assert rank(results) == [
            results[2],
            results[0],
            results[3],
            results[1]
        ]


@pytest.mark.usefixtures('lastfm_app', 'separate_search_has_tracks')
class TestSearchLastfm():

    threshold = 0.5

    def test_tries_a_separate_search(self, separate_search_patch):
        multi_search('query_track', 'query_artist')
        assert separate_search_patch.call_args == call('query_track', 'query_artist')


    def test_scores_results(self, tracks_from_separate, score_patch):
        multi_search('query_track', 'query_artist')

        query_track = score_patch.call_args[0][0]
        query_artist = score_patch.call_args[0][1]
        results = score_patch.call_args[0][2]

        assert query_track == 'query_track'
        assert query_artist == 'query_artist'
        assert isinstance(results[0], Result)
        assert isinstance(results[1], Result)
        assert results[0].track == tracks_from_separate[0]
        assert results[1].track == tracks_from_separate[1]


    def test_ranks_results(self, tracks_from_separate, rank_patch):
        multi_search('query_track', 'query_artist')

        results = rank_patch.call_args[0][0]

        assert isinstance(results[0], Result)
        assert isinstance(results[1], Result)
        assert results[0].track == tracks_from_separate[0]
        assert results[1].track == tracks_from_separate[1]


@pytest.mark.usefixtures('lastfm_app')
class TestSearchLastfmWhenNoSeparateOrCombinedSearchResults():

    def test_tries_a_combined_search(self, combined_search_patch):
        multi_search('query_track', 'query_artist')
        assert combined_search_patch.call_args == call('query_track', 'query_artist')


    def returns_none(self):
        tracks = multi_search('query_track', 'query_artist')
        assert tracks is None


@pytest.mark.usefixtures('set_scores_from_class', 'lastfm_app', 'separate_search_has_tracks')
class TestSearchLastfmWhenSeparateSearchResultsAboveThreshold():

    scores = {
        'track_1_track': threshold,
        'track_1_artist': threshold,
        'track_2_track': threshold + 0.1,
        'track_2_artist': threshold + 0.1,
    }

    def test_does_not_try_a_combined_search(self, combined_search_patch):
        multi_search('query_track', 'query_artist')
        assert combined_search_patch.call_count is 0


    def test_returns_ranked_result_tracks(self, tracks_from_separate):
        result_tracks = multi_search('query_track', 'query_artist')
        assert result_tracks == [tracks_from_separate[1], tracks_from_separate[0]]


@pytest.mark.usefixtures(
    'set_scores_from_class',
    'lastfm_app',
    'separate_search_has_tracks',
    'combined_search_has_tracks'
)
class TestSearchLastfmWhenSeparateSearchResultsBelowThreshold():

    scores = {
        'track_1_track': threshold - 0.5,
        'track_1_artist': threshold - 0.5,
        'track_2_track': threshold,
        'track_2_artist': threshold,
        'track_3_track': threshold - 0.1,
        'track_3_artist': threshold - 0.1,
        'track_4_track': threshold - 0.9,
        'track_4_artist': threshold - 0.9,
    }

    def test_tries_a_combined_search(self, combined_search_patch):
        multi_search('query_track', 'query_artist')
        assert combined_search_patch.call_args == call('query_track', 'query_artist')


    def test_merges_results(self, tracks_from_separate, tracks_from_combined, merge_patch):
        multi_search('query_track', 'query_artist')

        results_a = merge_patch.call_args[0][0]
        assert isinstance(results_a[0], Result)
        assert isinstance(results_a[1], Result)
        assert results_a[0].track == tracks_from_separate[1]
        assert results_a[1].track == tracks_from_separate[0]

        results_b = merge_patch.call_args[0][1]
        assert isinstance(results_b[0], Result)
        assert isinstance(results_b[1], Result)
        assert results_b[0].track == tracks_from_combined[0]
        assert results_b[1].track == tracks_from_combined[1]


    def test_scores_results(self, tracks_from_separate, tracks_from_combined, score_patch):
        multi_search('query_track', 'query_artist')

        query_track = score_patch.call_args[0][0]
        query_artist = score_patch.call_args[0][1]
        results = score_patch.call_args[0][2]

        assert query_track == 'query_track'
        assert query_artist == 'query_artist'
        assert isinstance(results[0], Result)
        assert isinstance(results[1], Result)
        assert results[0].track == tracks_from_separate[1]
        assert results[1].track == tracks_from_separate[0]
        assert results[2].track == tracks_from_combined[0]
        assert results[3].track == tracks_from_combined[1]


    def test_ranks_results(self, tracks_from_separate, tracks_from_combined, rank_patch):
        multi_search('query_track', 'query_artist')

        results = rank_patch.call_args[0][0]

        assert isinstance(results[0], Result)
        assert isinstance(results[1], Result)
        assert isinstance(results[2], Result)
        assert isinstance(results[3], Result)
        assert results[0].track == tracks_from_separate[1]
        assert results[1].track == tracks_from_separate[0]
        assert results[2].track == tracks_from_combined[0]
        assert results[3].track == tracks_from_combined[1]


    def test_returns_ranked_result_tracks(self, tracks_from_separate, tracks_from_combined):
        result_tracks = multi_search('query_track', 'query_artist')
        assert result_tracks == [
            tracks_from_separate[1],
            tracks_from_combined[0],
            tracks_from_separate[0],
            tracks_from_combined[1],
        ]


@pytest.mark.usefixtures('lastfm_app')
class TestAgainstRealResults():

    def test_no_good_separate_results_asys(
        self,
        separate_search_patch,
        combined_search_patch,
        get_result_fixtures
    ):
        parser = LastfmResultParser()
        separate_search_patch.return_value = parser.parse(get_result_fixtures('result_separate_asys.json'))
        combined_search_patch.return_value = parser.parse(get_result_fixtures('result_combined_asys.json'))
        results = multi_search('No More Fucking Rock´n´ Roll', 'A.S.Y.S.')
        assert results[0].track_name == "No More Fucking Rock 'n' Roll"
        assert results[0].artist_name == "A*S*Y*S"
        assert results[0].listeners == 1912


    def test_good_separate_results_danger(
        self,
        separate_search_patch,
        get_result_fixtures
    ):
        parser = LastfmResultParser()
        separate_search_patch.return_value = parser.parse(get_result_fixtures('result_separate_danger.json'))
        results = multi_search('11h30 - datA remix', 'Danger')
        assert results[0].track_name == "11h30 (DatA Remix)"
        assert results[0].artist_name == "Danger"
        assert results[0].listeners == 114502


    def test_badly_ordered_separate_results_the_subs(
        self,
        separate_search_patch,
        get_result_fixtures
    ):
        parser = LastfmResultParser()
        separate_search_patch.return_value = parser.parse(get_result_fixtures('result_separate_the_subs.json'))
        results = multi_search('My Body', 'The Subs')
        assert results[0].track_name == "My Body"
        assert results[0].artist_name == "The Subs"
        assert results[0].listeners == 521
