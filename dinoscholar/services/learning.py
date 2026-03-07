import json
import os
import re
from dataclasses import dataclass, field

import frontmatter
import markdown as md


@dataclass
class Lesson:
    id: str
    title: str
    content_md: str
    content_html: str
    key_terms: list[str] = field(default_factory=list)
    summary: str = ""
    order: int = 0


@dataclass
class Module:
    id: str
    title: str
    description: str
    lessons: list[Lesson] = field(default_factory=list)
    order: int = 0


class LearningService:
    def __init__(self, data_path: str):
        self._modules: list[Module] = []
        self._glossary: dict[str, dict] = {}
        self._data_path = data_path
        self._load_glossary(data_path)
        self._load_all(data_path)

    def _load_glossary(self, data_path: str) -> None:
        filepath = os.path.join(data_path, "glossary.json")
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        for entry in raw:
            self._glossary[entry["term"].lower().replace(" ", "-")] = entry

    def _render_lesson(self, content_md: str, key_terms: list[str]) -> str:
        html = md.markdown(content_md, extensions=["extra", "codehilite", "toc"])
        for term_id in key_terms:
            term_data = self._glossary.get(term_id)
            if term_data:
                pattern = re.compile(
                    r'\b(' + re.escape(term_data["term"]) + r')\b',
                    re.IGNORECASE,
                )
                replacement = (
                    f'<abbr title="{term_data["definition"]}" class="glossary-term">'
                    f'\\1</abbr>'
                )
                html = pattern.sub(replacement, html, count=1)
        return html

    def get_modules(self) -> list[Module]:
        return list(self._modules)

    def get_module(self, module_id: str) -> Module | None:
        for m in self._modules:
            if m.id == module_id:
                return m
        return None

    def get_lesson(self, module_id: str, lesson_id: str) -> Lesson | None:
        module = self.get_module(module_id)
        if not module:
            return None
        for lesson in module.lessons:
            if lesson.id == lesson_id:
                return lesson
        return None

    def get_module_questions(self, module_id: str) -> list[dict]:
        module = self.get_module(module_id)
        if not module:
            return []
        questions_path = os.path.join(
            self._data_path, "modules", module_id, "questions.json"
        )
        if not os.path.exists(questions_path):
            return []
        with open(questions_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Handle both nested {module_id, questions: [...]} and flat [...] formats
        if isinstance(data, dict) and "questions" in data:
            return data["questions"]
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and "questions" in data[0]:
            return data[0]["questions"]
        return data

    def get_all_questions(self) -> list[dict]:
        all_q = []
        for module in self._modules:
            all_q.extend(self.get_module_questions(module.id))
        return all_q

    def get_glossary(self) -> dict[str, dict]:
        # Return copies with 'id' key included for template use
        result = {}
        for key, entry in self._glossary.items():
            result[key] = {**entry, "id": key}
        return result

    def get_glossary_term(self, term_id: str) -> dict | None:
        entry = self._glossary.get(term_id)
        if entry:
            return {**entry, "id": term_id}
        return None

    def _load_all(self, data_path: str) -> None:
        modules_dir = os.path.join(data_path, "modules")
        if not os.path.isdir(modules_dir):
            return
        for dirname in sorted(os.listdir(modules_dir)):
            meta_path = os.path.join(modules_dir, dirname, "meta.json")
            if not os.path.exists(meta_path):
                continue
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            module = Module(
                id=meta["id"],
                title=meta["title"],
                description=meta.get("description", ""),
                order=meta.get("order", 0),
            )
            for lesson_meta in meta.get("lessons", []):
                lesson_path = os.path.join(
                    modules_dir, dirname, lesson_meta["file"]
                )
                if not os.path.exists(lesson_path):
                    continue
                post = frontmatter.load(lesson_path)
                content_html = self._render_lesson(
                    post.content, post.metadata.get("key_terms", [])
                )
                lesson_id = os.path.splitext(lesson_meta["file"])[0]
                lesson = Lesson(
                    id=lesson_id,
                    title=post.metadata.get("title", lesson_meta.get("title", "")),
                    content_md=post.content,
                    content_html=content_html,
                    key_terms=post.metadata.get("key_terms", []),
                    summary=post.metadata.get("summary", ""),
                    order=lesson_meta.get("order", 0),
                )
                module.lessons.append(lesson)
            module.lessons.sort(key=lambda l: l.order)
            self._modules.append(module)
        self._modules.sort(key=lambda m: m.order)
