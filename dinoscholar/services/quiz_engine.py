import random
from datetime import date
from dataclasses import dataclass, field


@dataclass
class Question:
    id: str
    type: str  # multiple_choice / true_false / short_answer
    difficulty: str  # beginner / intermediate / advanced
    question: str
    options: list[str] | None
    correct: int | str
    explanation: str
    module_id: str = ""
    lesson_id: str = ""


@dataclass
class QuizResult:
    questions: list[Question]
    answers: list[int | str]
    correct_answers: list[bool]
    score: int
    total: int
    duration_sec: int | None = None


class QuizEngine:
    def __init__(self, learning_service):
        self._learning = learning_service

    def _build_question(self, raw: dict, module_id: str = "", lesson_id: str = "") -> Question:
        return Question(
            id=raw["id"],
            type=raw.get("type", "multiple_choice"),
            difficulty=raw.get("difficulty", "beginner"),
            question=raw.get("question", raw.get("text", "")),
            options=raw.get("choices", raw.get("options")),
            correct=raw.get("answer", raw.get("correct")),
            explanation=raw.get("explanation", ""),
            module_id=module_id or raw.get("module", ""),
            lesson_id=lesson_id or raw.get("lesson_id", ""),
        )

    def _get_all_questions(self) -> list[Question]:
        questions = []
        for module in self._learning.get_modules():
            raw_questions = self._learning.get_module_questions(module.id)
            for rq in raw_questions:
                questions.append(self._build_question(rq, module_id=module.id))
        return questions

    def generate_module_quiz(
        self, module_id: str, difficulty: str = "all", count: int = 10
    ) -> list[Question]:
        raw_questions = self._learning.get_module_questions(module_id)
        questions = [self._build_question(rq, module_id=module_id) for rq in raw_questions]
        if difficulty != "all":
            questions = [q for q in questions if q.difficulty == difficulty]
        random.shuffle(questions)
        return questions[:count]

    def generate_daily_challenge(self) -> list[Question]:
        seed = int(date.today().strftime("%Y%m%d"))
        rng = random.Random(seed)
        all_questions = self._get_all_questions()
        if not all_questions:
            return []
        return rng.sample(all_questions, min(10, len(all_questions)))

    def generate_timed_quiz(
        self, difficulty: str = "all", count: int = 20
    ) -> list[Question]:
        all_questions = self._get_all_questions()
        if difficulty != "all":
            all_questions = [q for q in all_questions if q.difficulty == difficulty]
        random.shuffle(all_questions)
        return all_questions[:count]

    def score(
        self, questions: list[Question], answers: list[int | str]
    ) -> QuizResult:
        correct_answers = []
        score = 0
        for q, a in zip(questions, answers):
            if q.type == "multiple_choice":
                is_correct = int(a) == q.correct
            elif q.type == "true_false":
                is_correct = str(a).lower() == str(q.correct).lower()
            else:
                is_correct = str(a).strip().lower() == str(q.correct).strip().lower()
            correct_answers.append(is_correct)
            if is_correct:
                score += 1
        return QuizResult(
            questions=questions,
            answers=answers,
            correct_answers=correct_answers,
            score=score,
            total=len(questions),
        )
