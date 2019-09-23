from typing import NamedTuple, Optional, Sequence, Iterator
from pathlib import Path
import json
from datetime import datetime

Url = str

class Annotation(NamedTuple):
    dt: datetime
    title: str
    content: Optional[str] # might be none if for instance we just marked page with tags. not sure if we want to handle it somehow separately
    link: Url
    eid: str
    text: Optional[str]
    context: Url
    tags: Sequence[str]
    hyp_link: Url



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

    def iter_annotations(self) -> Iterator[Annotation]:
        for i in self._iter_raw():
            dts = i['created']
            title = ' '.join(i['document']['title'])
            selectors = i['target'][0].get('selector', None)
            if selectors is None:
                # TODO warn?...
                selectors = []
            content: Optional[str] = None
            for s in selectors:
                if 'exact' in s:
                    content = s['exact']
                    break
            eid = i['id']
            link = i['uri']
            # TODO FIXME UTC?
            dt = datetime.strptime(dts[:-3] + dts[-2:], '%Y-%m-%dT%H:%M:%S.%f%z')
            txt = i['text']
            text = None if len(txt.strip()) == 0 else txt
            context = i['links']['incontext']
            yield Annotation(
                dt=dt,
                title=title,
                content=content,
                link=link,
                eid=eid,
                text=text,
                context=context, # TODO FIXME is context used anywhere?
                tags=tuple(i['tags']),
                hyp_link=context,
            )

