#!/usr/bin/env python3
from itertools import tee, groupby
from typing import NamedTuple, Optional, Sequence, Iterator
from pathlib import Path
from datetime import datetime


from .exporthelpers import dal_helper
from .exporthelpers.dal_helper import (
    PathIsh,
    Res,
    the,
    Json,
    pathify,
    datetime_aware,
    json_items,
)
from .exporthelpers import logging_helper


logger = logging_helper.logger(__name__)


Url = str


# TODO unstead, use raw json + add @property?
class Highlight(NamedTuple):
    created: datetime_aware
    title: str
    url: Url
    hid: str
    hyp_link: Url
    # highlight might be None if for instance we just marked page with tags without annotating
    # not sure if we want to handle it somehow separately
    highlight: Optional[str]
    annotation: Optional[str]  # user's comment
    tags: Sequence[str]


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
        self.sources = list(map(pathify, sources))

    def _iter_raw(self):
        paths = self.sources
        total = len(paths)
        width = len(str(total))
        for idx, path in enumerate(paths):
            logger.info(f'processing [{idx:>{width}}/{total:>{width}}] {path}')
            with path.open(mode='rb') as fo:
                first = fo.read(1)
                old_format = first == b'['
            key = None if old_format else 'annotations'
            # annotations are in reverse chronological order, so make sense to reverse
            annotations = sorted(iter(json_items(path, key)), key=lambda j: j.get('created', ''))
            yield from annotations

    def highlights(self) -> Iterator[Res[Highlight]]:
        emitted = set()
        for i in self._iter_raw():
            hid = i['id']
            if hid in emitted:
                continue
            emitted.add(hid)
            try:
                yield self._parse_highlight(i)
            except Exception as e:
                err = RuntimeError(i)
                err.__cause__ = e
                yield err

    def pages(self) -> Iterator[Res[Page]]:
        vit, eit = tee(self.highlights())
        # fmt: off
        values = (r for r in vit if not isinstance(r, Exception))
        errors = (r for r in eit if     isinstance(r, Exception))
        # fmt: on

        by_url = lambda h: h.url
        by_created = lambda h: h.created
        def it() -> Iterator[Page]:
            for link, git in groupby(sorted(values, key=by_url), key=by_url):
                group = list(sorted(git, key=by_created))
                yield Page(group)

        yield from sorted(it(), key=by_created)
        yield from errors

    def _parse_highlight(self, i: Json) -> Highlight:
        [tg] = i['target']  # hopefully it's always single element?
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


# todo would be nice to use some fake data instead? this only gonna work under an ediable install
def _testfile() -> Path:
    testdata = Path(__file__).absolute().parent.parent.parent / 'testdata'
    [jfile] = testdata.rglob('data/annotations.json')
    return jfile


def test() -> None:
    dal = DAL([_testfile()])
    # at least check it doesn't crash
    for p in dal.pages():
        assert not isinstance(p, Exception)
        p.title
        p.url
        p.created
        len(list(p.highlights))


def demo(dal: DAL) -> None:
    # TODO split errors properly? move it to dal_helper?
    # highlights = list(w for w in dao.highlights() if not isinstance(w, Exception))

    # TODO logger?
    vit, eit = tee(dal.pages())
    # fmt: off
    values = (r for r in vit if not isinstance(r, Exception))
    errors = (r for r in eit if     isinstance(r, Exception))
    # fmt: on
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
