#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from kython.misc import import_file

hypothesis = import_file(Path(__file__).parent / 'Hypothesis' / 'hypothesis.py', 'hypothesis')

# https://hypothes.is/account/developer
from hypothesis_secrets import HYPOTHESIS_USER, HYPOTHESIS_TOKEN

def main():
    h = hypothesis.Hypothesis(username=HYPOTHESIS_USER, token=HYPOTHESIS_TOKEN)
    
    data = []
    for a in h.search_all({'user': HYPOTHESIS_USER}):
        data.append(a)
    
    json.dump(data, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)

if __name__ == '__main__':
    main()
