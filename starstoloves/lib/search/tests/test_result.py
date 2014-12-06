import pytest

from starstoloves.lib.track.lastfm_track import LastfmTrack
from ..result import LastfmResultParser


pytestmark = pytest.mark.django_db


@pytest.fixture()
def result_parser(request):
    return LastfmResultParser()


class TestResultParser():

    many_results = {
        'trackmatches': {
            'track': [
                {
                    'name': 'trackA',
                    'artist': 'artistA',
                    'url': 'urlA',
                    'listeners': '222',
                },{
                    'name': 'trackB',
                    'artist': 'artistB',
                    'url': 'urlB',
                    'listeners': '888',
                },
            ]
        }
    }

    single_result = {
        'trackmatches': {
            'track': {
                'name': 'trackA',
                'artist': 'artistA',
                'url': 'urlA',
                'listeners': '222',
            }
        }
    }

    no_results = {
        'trackmatches': "\n"
    }


    def test_parse_returns_lastfm_tracks(self, result_parser):
        tracks = result_parser.parse(self.single_result)
        assert isinstance(tracks[0], LastfmTrack)


    def test_parse_extracts_track_details(self, result_parser):
        tracks = result_parser.parse(self.many_results)
        assert [track.track_name for track in tracks] == ['trackA', 'trackB']
        assert [track.artist_name for track in tracks] == ['artistA', 'artistB']
        assert [track.url for track in tracks] == ['urlA', 'urlB']
        assert [track.listeners for track in tracks] == ['222', '888']


    def test_parse_extracts_track_details_when_there_is_only_one(self, result_parser):
        tracks = result_parser.parse(self.single_result)
        assert [track.track_name for track in tracks] == ['trackA']
        assert [track.artist_name for track in tracks] == ['artistA']
        assert [track.url for track in tracks] == ['urlA']
        assert [track.listeners for track in tracks] == ['222']


    def test_parse_returns_none_when_there_are_no_tracks(self, result_parser):
        assert result_parser.parse(self.no_results) is None


    def test_parse_returns_none_when_given_an_error(self, result_parser):
        assert result_parser.parse(TypeError) is None
