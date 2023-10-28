#!/usr/bin/env python3
import json

from .exporthelpers.export_helper import setup_parser, Parser

from .Hypothesis import hypothesis


class Exporter:
    def __init__(self, *args, **kwargs) -> None:
        kwargs['max_search_results'] = 10000
        self.api = hypothesis.Hypothesis(*args, **kwargs)
        # TODO not sure why max_search_results is set to 2000 in Hypothesis package; documentation says 9800 is the max for offset? Ask judell
        self.user = kwargs['username']

    def export_json(self):
        profile = self.api.authenticated_api_query(self.api.api_url + '/profile')
        annotations = list(self.api.search_all({'user': self.user}))
        return {
            'profile': profile,
            'annotations': annotations,
        }


def get_json(**params):
    return Exporter(**params).export_json()


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()

    params = args.params
    dumper = args.dumper

    j = get_json(**params)
    js = json.dumps(j, ensure_ascii=False, indent=2, sort_keys=True)
    dumper(js)


def make_parser():
    parser = Parser('Export/takeout for your personal [[https://hypothes.is][Hypothes.is]] data: annotations and profile information.')
    setup_parser(
        parser=parser,
        params=['username', 'token'],
        extra_usage='''
You can also import ~hypexport.export~ as a module and call ~get_json~ function directly to get raw JSON.
''',
    )
    return parser


if __name__ == '__main__':
    main()
