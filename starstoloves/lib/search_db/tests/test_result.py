import pytest

from ..result import LastfmResultParser, LastfmResultParserWithLoves

@pytest.fixture(params=[True, False])
def result_parser(request):
    if request.param:
        return LastfmResultParser()
    else:
        return LastfmResultParserWithLoves([])

class TestResultParser():

    def test_parse_extracts_track_details(self, result_parser):
        result = {
            'trackmatches': {
                'track': [
                    {
                        'name': 'trackA',
                        'artist': 'artistA',
                        'url': 'urlA',
                    },{
                        'name': 'trackB',
                        'artist': 'artistB',
                        'url': 'urlB',
                    },
                ]
            }
        }
        tracks = result_parser.parse(result)
        assert [track['track_name'] for track in tracks] == ['trackA', 'trackB']
        assert [track['artist_name'] for track in tracks] == ['artistA', 'artistB']
        assert [track['url'] for track in tracks] == ['urlA', 'urlB']

    def test_parse_extracts_track_details_when_there_is_only_one(self, result_parser):
        result = {
            'trackmatches': {
                'track': {
                    'name': 'trackA',
                    'artist': 'artistA',
                    'url': 'urlA',
                }
            }
        }
        tracks = result_parser.parse(result)
        assert [track['track_name'] for track in tracks] == ['trackA']
        assert [track['artist_name'] for track in tracks] == ['artistA']
        assert [track['url'] for track in tracks] == ['urlA']

    def test_parse_returns_none_when_there_are_no_tracks(self, result_parser):
        result = {
            'trackmatches': "\n"
        }
        assert result_parser.parse(result) is None

    def test_parse_returns_none_when_given_an_error(self, result_parser):
        assert result_parser.parse(TypeError) is None


@pytest.fixture
def result_parser_with_loves():
    loved_tracks_urls = ['urlA', 'urlC']
    return LastfmResultParserWithLoves(loved_tracks_urls)


class TestResultParserWithLoves():

    def test_parse_marks_tracks_as_loved_when_they_match_a_loved_track(self, result_parser_with_loves):
        result = {
            'trackmatches': {
                'track': [
                    {
                        'name': 'trackA',
                        'artist': 'artistA',
                        'url': 'urlA',
                    },{
                        'name': 'trackB',
                        'artist': 'artistB',
                        'url': 'urlB',
                    },
                ]
            }
        }
        tracks = result_parser_with_loves.parse(result)
        assert [track['loved'] for track in tracks] == [True, False]
