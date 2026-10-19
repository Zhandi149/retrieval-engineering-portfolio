"""Small in-memory BM25 index with explicit scoring and deterministic ties."""
from collections import Counter
from dataclasses import dataclass
import math
import re


def tokenize(text):
    return re.findall(r"\w+", text.casefold())


@dataclass(frozen=True)
class Document:
    id: str
    text: str
    title: str = ""


class SearchIndex:
    def __init__(self, documents, k1=1.5, b=0.75):
        self.documents = list(documents)
        if len({d.id for d in self.documents}) != len(self.documents):
            raise ValueError("document IDs must be unique")
        if k1 <= 0 or not 0 <= b <= 1:
            raise ValueError("invalid BM25 parameters")
        self.k1, self.b = k1, b
        self.terms = [Counter(tokenize(d.title + " " + d.text)) for d in self.documents]
        self.lengths = [sum(t.values()) for t in self.terms]
        self.average_length = sum(self.lengths) / max(1, len(self.lengths))
        self.frequency = Counter(term for terms in self.terms for term in terms)

    def search(self, query, limit=10):
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 0:
            raise ValueError("limit must be a nonnegative integer")
        query_terms = set(tokenize(query))
        hits = []
        for document, counts, length in zip(self.documents, self.terms, self.lengths):
            score = 0.0
            for term in sorted(query_terms & counts.keys()):
                frequency = self.frequency[term]
                idf = math.log(1 + (len(self.documents) - frequency + 0.5) / (frequency + 0.5))
                norm = self.k1 * (1 - self.b + self.b * length / self.average_length)
                score += idf * counts[term] * (self.k1 + 1) / (counts[term] + norm)
            if score > 0:
                hits.append({"id": document.id, "title": document.title,
                             "text": document.text, "score": round(score, 6)})
        return sorted(hits, key=lambda h: (-h["score"], h["id"]))[:limit]
