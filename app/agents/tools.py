import json
import re
from pathlib import Path
from typing import Any

import numexpr as ne
from langchain_core.tools import tool


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


class BankingToolset:
    def __init__(self, faq_path: Path, kb_path: Path) -> None:
        self.faq_items = self._load_faq(faq_path)
        self.kb_text = self._load_kb(kb_path)

    @staticmethod
    def _load_faq(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return [
            {
                "question": item.get("question", ""),
                "answer": item.get("answer", ""),
            }
            for item in data
        ]

    @staticmethod
    def _load_kb(path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def _faq_lookup_impl(self, query: str) -> str:
        query_norm = _normalize(query)
        ranked = []
        for item in self.faq_items:
            q = _normalize(item["question"])
            score = sum(token in q for token in query_norm.split())
            ranked.append((score, item))

        ranked.sort(key=lambda x: x[0], reverse=True)
        top = [item for score, item in ranked if score > 0][:3]

        if not top:
            return "No direct FAQ match found."

        lines = ["Top FAQ matches:"]
        for item in top:
            lines.append(f"Q: {item['question']}\\nA: {item['answer']}")
        return "\n\n".join(lines)

    def _kb_retriever_impl(self, query: str) -> str:
        query_tokens = {token for token in _normalize(query).split() if len(token) > 2}
        if not query_tokens:
            return "No meaningful query tokens found."

        chunks = [chunk.strip() for chunk in self.kb_text.split("\n\n") if chunk.strip()]
        scored: list[tuple[int, str]] = []
        for chunk in chunks:
            chunk_norm = _normalize(chunk)
            score = sum(token in chunk_norm for token in query_tokens)
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        matches = [chunk for score, chunk in scored if score > 0][:3]

        if not matches:
            return "No strong knowledge-base match found."

        return "\n\n".join(matches)

    @staticmethod
    def _calculator_impl(expression: str) -> str:
        allowed = re.compile(r"^[0-9\s\+\-\*\/\(\)\.%]+$")
        if not allowed.match(expression):
            return "Invalid expression. Use numbers and arithmetic operators only."

        try:
            result: Any = ne.evaluate(expression)
            return f"Result: {result}"
        except Exception:
            return "Could not evaluate expression."

    def build_tools(self):
        @tool("faq_lookup")
        def faq_lookup(query: str) -> str:
            """Find relevant question-answer pairs from internal banking FAQs."""
            return self._faq_lookup_impl(query)

        @tool("knowledge_base_retriever")
        def knowledge_base_retriever(query: str) -> str:
            """Retrieve relevant internal banking knowledge snippets."""
            return self._kb_retriever_impl(query)

        @tool("banking_calculator")
        def banking_calculator(expression: str) -> str:
            """Evaluate arithmetic expressions for banking calculations (EMI components, totals, etc.)."""
            return self._calculator_impl(expression)

        return [faq_lookup, knowledge_base_retriever, banking_calculator]
