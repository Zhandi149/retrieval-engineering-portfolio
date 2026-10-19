"""Transcript search and timestamp projection over synthetic video metadata."""
import json
from pathlib import Path
from .search import Document, SearchIndex


def timestamp(seconds):
    if not isinstance(seconds, int) or isinstance(seconds, bool) or seconds < 0:
        raise ValueError("timestamp must be a nonnegative integer")
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"


def segment_number(seconds, duration=300):
    timestamp(seconds)
    if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
        raise ValueError("segment duration must be a positive integer")
    return seconds // duration + 1


class VideoCatalog:
    def __init__(self):
        self.rows = json.loads(Path(__file__).with_name("sample_catalog.json").read_text())
        self.by_id = {row["id"]: row for row in self.rows}
        self.index = SearchIndex([Document(row["id"], row["text"], row["title"]) for row in self.rows])

    def search(self, query, limit=6):
        results = []
        for hit in self.index.search(query, limit):
            row = self.by_id[hit["id"]]
            results.append(dict(hit, video_id=row["video_id"], start=row["start"],
                                timestamp=timestamp(row["start"]),
                                segment=segment_number(row["start"]), synthetic=True))
        return results
