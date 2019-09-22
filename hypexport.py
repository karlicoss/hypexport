#!/usr/bin/env python3
import json
from pathlib import Path

from kython.misc import import_file

class Exporter:
    def __init__(self, *args, **kwargs) -> None:
        # TODO use submodule??
        hypothesis = import_file(Path(__file__).absolute().parent / 'Hypothesis' / 'hypothesis.py', 'hypothesis')
        self.api = hypothesis.Hypothesis(*args, **kwargs, max_search_results=10000)
        # TODO not sure why max_search_results is set to 2000 in Hypothesis package; documentation says 9800 is the max for offset? Ask judell
        self.user = kwargs['username']

    def export_json(self):
        profile = self.api.authenticated_api_query(self.api.api_url + '/profile')
        annotations = list(self.api.search_all({'user': self.user}))
        return {
            'profile'    : profile,
            'annotations': annotations,
        }


def get_json(**params):
    return Exporter(**params).export_json()


def main():
    from export_helper import setup_parser
    import argparse
    # TODO pass docs to setup_parser?
    # https://hypothes.is/account/developer
    parser = argparse.ArgumentParser('Export/takeout for your personal Hypothesis data')
    setup_parser(parser=parser, params=['username', 'token'])
    args = parser.parse_args()

    params = args.params
    dumper = args.dumper

    j = get_json(**params)
    js = json.dumps(j, ensure_ascii=False, indent=2, sort_keys=True)
    dumper(js)


if __name__ == '__main__':
    main()
