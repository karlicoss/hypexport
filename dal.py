#!/usr/bin/env python3
from itertools import tee, groupby
from typing import NamedTuple, Optional, Sequence, Iterator, List
from pathlib import Path
import json
from datetime import datetime


if __name__ == '__main__':
    # see dal_helper.setup for the explanation
    import dal_helper
    dal_helper.fix_imports(globals())


# TODO not sure what are we gonna do for CI linters; but it's really a minor issue.

from . import dal_helper
from .dal_helper import PathIsh, Res, the, Json


Url = str

# TODO FIXME make it raw and add properties
class Highlight(NamedTuple):
    created: datetime
    title: str
    url: Url
    hid: str
    hyp_link: Url
    highlight: Optional[str] # might be None if for instance we just marked page with tags. not sure if we want to handle it somehow separately
    annotation: Optional[str] # user's comment
    tags: Sequence[str]


# TODO use cached properties..
class Page(NamedTuple):
    """
    Represents annotated page along with the highlights
    """
    highlights: Sequence[Highlight]

    @property
    def url(self) -> str:
        return the(h.url for h in self.highlights)

    @property
    def title(self) -> str:
        return the(h.title for h in self.highlights)

    @property
    def created(self) -> datetime:
        return min(h.created for h in self.highlights)


class DAL:
    def __init__(self, sources: Sequence[PathIsh]) -> None:
        # TODO FIXME take pathish everywhere?
        self.sources = list(map(Path, sources))

    def _iter_raw(self):
        # TODO FIXME merge all of them carefully
        last = max(self.sources)
        j = json.loads(last.read_text())
        if isinstance(j, list):
            # old export format
            annotations = j
        else:
            annotations = j['annotations']
        yield from annotations

    def highlights(self) -> Iterator[Res[Highlight]]:
        for i in self._iter_raw():
            try:
                yield self._parse_highlight(i)
            except Exception as e:
                err = RuntimeError(i)
                err.__cause__ = e
                yield err

    def pages(self) -> Iterator[Res[Page]]:
        vit, eit = tee(self.highlights())
        values = (r for r in vit if not isinstance(r, Exception))
        errors = (r for r in eit if     isinstance(r, Exception))

        key = lambda h: h.url
        for link, git in groupby(sorted(values, key=key), key=key):
            group = list(sorted(git, key=lambda h: h.created))
            yield Page(group)

        yield from errors

    def _parse_highlight(self, i: Json) -> Highlight:
        [tg] = i['target'] # hopefully it's always single element?
        selectors = tg.get('selector', None)
        if selectors is None:
            # TODO warn?...
            selectors = []

        highlights = [s['exact'] for s in selectors if 'exact' in s]

        # TODO warn? never happend though
        assert len(highlights) <= 1

        if len(highlights) == 0:
            highlight = None
        else:
            [highlight] = highlights

        content: Optional[str] = None
        for s in selectors:
            if 'exact' in s:
                content = s['exact']
                break

        page_link = i['uri']
        title = i['document'].get('title')
        if title is None:
            # sometimes happens, e.t. if it's plaintext file
            page_title = page_link
        else:
            page_title = ' '.join(title)
        hid = i['id']
        # TODO check that UTC?
        dts = i['created']
        created = datetime.strptime(dts[:-3] + dts[-2:], '%Y-%m-%dT%H:%M:%S.%f%z')
        txt = i['text']
        annotation = None if len(txt.strip()) == 0 else txt
        context = i['links']['incontext']
        return Highlight(
            created=created,
            url=page_link,
            title=page_title,
            hid=hid,
            hyp_link=context,
            highlight=highlight,
            annotation=annotation,
            tags=tuple(i['tags']),
        )

def demo(dal: DAL) -> None:
    # TODO split errors properly? move it to dal_helper?
    # highlights = list(w for w in dao.highlights() if not isinstance(w, Exception))

    # TODO logger?
    vit, eit = tee(dal.pages())
    values = (r for r in vit if not isinstance(r, Exception))
    errors = (r for r in eit if     isinstance(r, Exception))
    for e in errors:
        print("ERROR! ", e)

    pages = list(values)
    print(f"Parsed {len(pages)} pages")

    from collections import Counter
    from pprint import pprint
    common = Counter({(x.url, x.title): len(x.highlights) for x in pages}).most_common(10)
    print("10 most highlighed pages:")
    for (url, title), count in common:
        print(f'{count:4d} {url} "{title}"')


if __name__ == '__main__':
    dal_helper.main(DAL=DAL, demo=demo)
