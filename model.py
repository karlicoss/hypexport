from typing import NamedTuple, Optional, Sequence, Iterator, Dict, Any, Union
from pathlib import Path
import json
from datetime import datetime

Url = str

class Highlight(NamedTuple):
    dt: datetime
    page_title: str
    page_link: Url
    id: str
    hyp_link: Url
    highlight: Optional[str] # might be None if for instance we just marked page with tags. not sure if we want to handle it somehow separately
    annotation: Optional[str] # user's comment
    tags: Sequence[str]



class Model:
    def __init__(self, sources: Sequence[Path]) -> None:
        # TODO FIXME use new style exports
        # TODO FIXME take pathish everywhere?
        self.sources = list(map(Path, sources))

    def _iter_raw(self):
        # TODO FIXME merge all of them carefully
        last = max(self.sources)
        j = json.loads(last.read_text())
        if isinstance(j, list):
            # TODO ugh. old style export
            annotations = j
        else:
            annotations = j['annotations']
        yield from annotations

    def iter_highlights(self) -> Iterator[Union[Highlight, Exception]]:
        for i in self._iter_raw():
            try:
                yield self._parse_highlight(i)
            except Exception as e:
                err = RuntimeError(i)
                err.__cause__ = e
                yield err

    def _parse_highlight(self, i: Dict[str, Any]) -> Highlight:
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
        # TODO FIXME UTC?
        dts = i['created']
        dt = datetime.strptime(dts[:-3] + dts[-2:], '%Y-%m-%dT%H:%M:%S.%f%z')
        txt = i['text']
        annotation = None if len(txt.strip()) == 0 else txt
        context = i['links']['incontext']
        return Highlight(
            dt=dt,
            page_title=page_title,
            page_link=page_link,
            id=hid,
            hyp_link=context,
            highlight=highlight,
            annotation=annotation,
            tags=tuple(i['tags']),
        )

