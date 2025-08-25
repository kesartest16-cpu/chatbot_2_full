import json
import os
import re
import random
from typing import Dict, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class IntentMatcher:
    def __init__(self, intents_path: str):
        self.intents_path = intents_path
        self.data = self._load_intents()
        self.vectorizer = TfidfVectorizer(analyzer="word", ngram_range=(1,2), stop_words="english")
        self.tags = []
        self.patterns = []
        self._build_index()

    def _load_intents(self) -> Dict:
        with open(self.intents_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_index(self):
        self.tags = []
        self.patterns = []
        for intent in self.data["intents"]:
            tag = intent["tag"]
            for p in intent["patterns"]:
                self.tags.append(tag)
                self.patterns.append(p.lower())
        if self.patterns:
            self.matrix = self.vectorizer.fit_transform(self.patterns)
        else:
            self.matrix = None

    def reload(self):
        self.data = self._load_intents()
        self._build_index()

    @staticmethod
    def _extract_wildcard(pattern: str) -> Tuple[str, bool]:
        # Convert 'my name is *' to regex and indicate wildcard
        if "*" in pattern:
            escaped = re.escape(pattern).replace("\\*", "(.+)")
            return fr"^\s*{escaped}\s*$", True
        return fr"^\s*{re.escape(pattern)}\s*$", False

    def match(self, text: str) -> Tuple[str, Dict[str, str], float]:
        """Return (tag, slots, score). Uses wildcard regex first, then TF‑IDF cosine."""
        text_l = text.lower().strip()

        # 1) Wildcard / exact regex
        for intent in self.data["intents"]:
            for patt in intent["patterns"]:
                patt_regex, has_star = self._extract_wildcard(patt)
                m = re.match(patt_regex, text_l)
                if m:
                    slots = {}
                    if has_star:
                        slots["wildcard"] = m.group(1).strip()
                    return intent["tag"], slots, 1.0

        # 2) TF‑IDF similarity to patterns
        if not self.patterns:
            return "", {}, 0.0
        vec = self.vectorizer.transform([text_l])
        sims = cosine_similarity(vec, self.matrix).flatten()
        best_idx = sims.argmax()
        best_score = float(sims[best_idx])
        tag = self.tags[best_idx]
        return tag if best_score > 0.25 else "", {}, best_score

    def respond(self, tag: str, context: Dict[str, str]) -> str:
        if tag is None:
            return random.choice(self.data["fallback"]["responses"])
        intent = next((i for i in self.data["intents"] if i["tag"] == tag), None)
        if not intent:
            return random.choice(self.data["fallback"]["responses"])
        template = random.choice(intent["responses"])
        try:
            return template.format(**context)
        except KeyError:
            return template