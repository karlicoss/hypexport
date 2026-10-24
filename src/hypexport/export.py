import argparse
import json

import hpikit.cli.export as cli
from hpikit.json import Json

from .Hypothesis import hypothesis


class Exporter:
    def __init__(self, *args, **kwargs) -> None:
        kwargs['max_search_results'] = 10000
        self.api = hypothesis.Hypothesis(*args, **kwargs)
        # TODO not sure why max_search_results is set to 2000 in Hypothesis package; documentation says 9800 is the max for offset? Ask judell
        self.user = kwargs['username']

    def export_json(self) -> Json:
        profile = self.api.authenticated_api_query(self.api.api_url + '/profile')
        annotations = list(self.api.search_all({'user': self.user}))
        return {
            'profile': profile,
            'annotations': annotations,
        }


def get_json(**params) -> Json:
    return Exporter(**params).export_json()


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()

    params = cli.get_params(parser, args)

    j = get_json(**params)
    js = json.dumps(j, ensure_ascii=False, indent=2, sort_keys=True)
    cli.dump(js, path=args.path)


def make_parser() -> argparse.ArgumentParser:
    parser = cli.make_parser(
        description='Export/takeout for your personal [Hypothes.is](https://hypothes.is) data: annotations and profile information.',
        params=['username', 'token'],
        extra_usage='''
You can also import `hypexport.export` as a module and call `get_json` function directly to get raw JSON.
''',
    )
    return parser


if __name__ == '__main__':
    main()
