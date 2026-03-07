# DinoScholar — Design Plan

**Version:** 1.0  
**Date:** March 6, 2026  
**Based on:** SPECIFICATION.md v1.0  

---

## Table of Contents

1. [Development Phases](#1-development-phases)
2. [Phase 1 — Foundation (M1)](#2-phase-1--foundation-m1)
3. [Phase 2 — Encyclopedia (M2)](#3-phase-2--encyclopedia-m2)
4. [Phase 3 — Timeline (M3)](#4-phase-3--timeline-m3)
5. [Phase 4 — Learning Modules Batch 1 (M4)](#5-phase-4--learning-modules-batch-1-m4)
6. [Phase 5 — Quiz System (M5)](#6-phase-5--quiz-system-m5)
7. [Phase 6 — Profiles & Achievements (M6)](#7-phase-6--profiles--achievements-m6)
8. [Phase 7 — Learning Modules Batch 2 (M7)](#8-phase-7--learning-modules-batch-2-m7)
9. [Phase 8 — Comparative Anatomy (M8)](#9-phase-8--comparative-anatomy-m8)
10. [Phase 9 — Polish & Testing (M9)](#10-phase-9--polish--testing-m9)
11. [Content Population Strategy](#11-content-population-strategy)
12. [Data Schema Details](#12-data-schema-details)
13. [API & Route Design](#13-api--route-design)
14. [CLI Command Design](#14-cli-command-design)
15. [UI/UX Wireframes](#15-uiux-wireframes)
16. [Testing Strategy](#16-testing-strategy)
17. [Dependency List](#17-dependency-list)
18. [Risk Register](#18-risk-register)

---

## 1. Development Phases

Each phase maps to a spec milestone. The rule: **every phase produces a working, runnable application**. No phase leaves the app in a broken state.

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
  M1          M2          M3          M4          M5
Foundation  Encyclop.   Timeline   Lessons 1-4  Quizzes
                                        │
Phase 9 ◄── Phase 8 ◄── Phase 7 ◄── Phase 6
  M9          M8          M7          M6
 Polish     Comparison  Lessons 5-8  Profiles
```

---

## 2. Phase 1 — Foundation (M1)

**Goal:** Establish the project skeleton so that all subsequent phases plug into a working framework.

### 2.1 Tasks

| #   | Task                                  | Output File(s)                          |
|-----|---------------------------------------|-----------------------------------------|
| 1.1 | Create project directory structure    | Full tree per SPECIFICATION §5.1        |
| 1.2 | Write `config.py`                     | `dinoscholar/config.py`                 |
| 1.3 | Set up SQLAlchemy + SQLite            | `database/db.py`                        |
| 1.4 | Define all ORM models                 | `models/user.py`, `progress.py`, `quiz.py` |
| 1.5 | Create database migration script      | `database/migrations/001_initial.py`    |
| 1.6 | Build Flask app factory               | `app.py`                                |
| 1.7 | Build base HTML template              | `web/templates/base.html`               |
| 1.8 | Build home page (placeholder)         | `web/templates/home.html`, `web/routes/main.py` |
| 1.9 | Set up Click CLI skeleton             | `cli.py`                                |
| 1.10| Write `requirements.txt`             | `requirements.txt`                      |
| 1.11| Seed empty data files                | `data/species.json`, `timeline.json`, `glossary.json` |
| 1.12| Verify app starts (web + CLI)        | Manual smoke test                       |

### 2.2 Design Decisions for This Phase

**App factory pattern (Flask):**
```python
# app.py
from flask import Flask
from database.db import db
from web.routes import register_routes

def create_app(config_name="default"):
    app = Flask(__name__,
                template_folder="web/templates",
                static_folder="web/static")
    app.config.from_object(f"config.{config_name}")
    db.init_app(app)
    register_routes(app)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
```

**Config structure:**
```python
# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class default:
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'dinoscholar.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_DIR = os.path.join(BASE_DIR, "data")

class testing:
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_DIR = os.path.join(BASE_DIR, "data")
```

**SQLAlchemy model base:**
```python
# database/db.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    with app.app_context():
        db.create_all()
```

**ORM models (all in `models/`):**
```python
# models/user.py
from database.db import db
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# models/progress.py
class LessonProgress(db.Model):
    __tablename__ = "lesson_progress"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    module_id = db.Column(db.Text, nullable=False)
    lesson_id = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    __table_args__ = (db.UniqueConstraint("user_id", "module_id", "lesson_id"),)

# models/quiz.py
class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_type = db.Column(db.Text, nullable=False)      # module / daily / timed
    module_id = db.Column(db.Text, nullable=True)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

class Achievement(db.Model):
    __tablename__ = "achievements"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    achievement_key = db.Column(db.Text, nullable=False)
    unlocked_at = db.Column(db.DateTime)
    __table_args__ = (db.UniqueConstraint("user_id", "achievement_key"),)

class StudySession(db.Model):
    __tablename__ = "study_sessions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    started_at = db.Column(db.DateTime)
    duration_sec = db.Column(db.Integer)
```

### 2.3 Exit Criteria

- `python app.py` starts Flask on port 5000, serves the home page.
- `python cli.py --help` shows the CLI help text.
- Database file is created with all tables on first run.
- All tests pass (`pytest` returns 0).

---

## 3. Phase 2 — Encyclopedia (M2)

**Goal:** Build the species database, search/filter service, and both web + CLI views.

### 3.1 Tasks

| #   | Task                                    | Output File(s)                         |
|-----|-----------------------------------------|----------------------------------------|
| 2.1 | Design `species.json` schema            | See §12.1                              |
| 2.2 | Write data population script            | `scripts/populate_species.py`          |
| 2.3 | Populate species data (~200 entries)    | `data/species.json`                    |
| 2.4 | Build `EncyclopediaService`             | `services/encyclopedia.py`             |
| 2.5 | Build web routes + templates            | `web/routes/encyclopedia.py`, templates |
| 2.6 | Build CLI commands                      | `cli_ui/encyclopedia.py`               |
| 2.7 | Write unit tests                        | `tests/test_encyclopedia.py`           |

### 3.2 Service Layer Design

```python
# services/encyclopedia.py
import json
from dataclasses import dataclass, field

@dataclass
class SpeciesRecord:
    id: str                          # slug: "tyrannosaurus-rex"
    scientific_name: str
    common_name: str
    order: str
    suborder: str
    family: str
    genus: str
    period: str                      # "Late Cretaceous"
    period_start_mya: float
    period_end_mya: float
    diet: str                        # herbivore / carnivore / omnivore
    length_m: float
    height_m: float
    weight_kg: float
    locomotion: str                  # bipedal / quadrupedal
    fossil_locations: list[str]
    description: str
    fun_facts: list[str]
    related_species: list[str]       # list of species IDs

class EncyclopediaService:
    def __init__(self, data_path: str):
        self._species: dict[str, SpeciesRecord] = {}
        self._load(data_path)

    def _load(self, path: str) -> None:
        """Load species.json into memory."""

    def get(self, species_id: str) -> SpeciesRecord | None:
        """Retrieve a single species by ID."""

    def search(self, query: str) -> list[SpeciesRecord]:
        """Full-text search across name, description, fun facts."""

    def filter(self, *,
               period: str | None = None,
               diet: str | None = None,
               min_length: float | None = None,
               max_length: float | None = None,
               location: str | None = None) -> list[SpeciesRecord]:
        """Filter species by structured fields."""

    def list_all(self, sort_by: str = "scientific_name") -> list[SpeciesRecord]:
        """Return all species, sorted."""

    def get_related(self, species_id: str) -> list[SpeciesRecord]:
        """Return related species for a given entry."""
```

### 3.3 Web Routes

| Method | Path                        | Description                  |
|--------|-----------------------------|------------------------------|
| GET    | `/encyclopedia`             | Species list with search/filter sidebar |
| GET    | `/encyclopedia/<id>`        | Species detail page          |

### 3.4 Web Template Plan

**`encyclopedia/list.html`** — Extends `base.html`. Contains:
- Search bar (text input, submits as `?q=...`).
- Filter panel: dropdowns for period, diet, locomotion; sliders for size range.
- Results table/card grid with species name, period, diet, size summary.
- Pagination (25 per page).

**`encyclopedia/detail.html`** — Extends `base.html`. Contains:
- Species header: scientific name, common name, classification badges.
- Info card: period, diet, size metrics, locomotion.
- Fossil location list with continent labels.
- Description section (rendered Markdown).
- Fun facts list.
- Related species links.
- "Compare" button → sends to comparison tool (Phase 8).

### 3.5 CLI Commands

```
dinoscholar encyclopedia list [--period TEXT] [--diet TEXT] [--sort TEXT]
dinoscholar encyclopedia search <query>
dinoscholar encyclopedia show <species_id>
```

### 3.6 Exit Criteria

- `/encyclopedia` renders a paginated list of ~200 species.
- Search by name returns correct results.
- Filters narrow results accurately.
- Detail page shows all fields for any species.
- CLI commands mirror web functionality.

---

## 4. Phase 3 — Timeline (M3)

**Goal:** Interactive geological timeline with period details and species overlay.

### 4.1 Tasks

| #   | Task                                   | Output File(s)                          |
|-----|----------------------------------------|-----------------------------------------|
| 3.1 | Design `timeline.json` schema          | See §12.2                               |
| 3.2 | Populate timeline data                 | `data/timeline.json`                    |
| 3.3 | Build `TimelineService`                | `services/timeline.py`                  |
| 3.4 | Build web routes + templates           | `web/routes/timeline.py`, templates     |
| 3.5 | Build CLI commands                     | `cli_ui/timeline.py`                    |
| 3.6 | Write unit tests                       | `tests/test_timeline.py`               |

### 4.2 Service Layer Design

```python
# services/timeline.py
from dataclasses import dataclass

@dataclass
class GeologicalPeriod:
    id: str                        # "late-cretaceous"
    name: str                      # "Late Cretaceous"
    era: str                       # "Mesozoic"
    start_mya: float               # 100.5
    end_mya: float                 # 66.0
    climate: str                   # paragraph description
    key_events: list[str]          # notable events
    dominant_species: list[str]    # species IDs from encyclopedia
    description: str               # educational summary

class TimelineService:
    def __init__(self, data_path: str, encyclopedia_service):
        self._periods: list[GeologicalPeriod] = []
        self._encyclopedia = encyclopedia_service
        self._load(data_path)

    def get_all_periods(self) -> list[GeologicalPeriod]:
        """Return all periods in chronological order (oldest first)."""

    def get_period(self, period_id: str) -> GeologicalPeriod | None:
        """Get details for a single period."""

    def get_species_in_period(self, period_id: str) -> list:
        """Cross-reference encyclopedia to find species in this period."""

    def get_coexisting_species(self, species_id: str) -> list:
        """Find all species that overlapped temporally with the given one."""
```

### 4.3 Web Template Plan

**`timeline/index.html`:**
- Horizontal scrollable timeline bar (CSS/JS). Each period is a proportionally-sized coloured block.
- Clicking a period block expands a detail panel below showing: name, date range, climate, key events, dominant species (linked to encyclopedia).
- Toggle to overlay species dots onto the timeline.

**Frontend approach:**
- Timeline rendering uses a `<div>` bar with CSS `flex` proportional widths (no heavy JS framework).
- A small vanilla JS script handles click-to-expand and species overlay toggle.
- Data injected as a `<script>` JSON block to avoid AJAX calls.

### 4.4 CLI Display

```
══════════════════════ MESOZOIC ERA ══════════════════════

TRIASSIC          JURASSIC            CRETACEOUS
252─────201.3─────145──────────────────66 MYA
████████░░░░░░░░░░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

Select a period [1-3]: _
```

Rich-formatted with `rich` library for terminal colour and layout.

### 4.5 Exit Criteria

- Web timeline renders all periods proportionally.
- Clicking a period shows correct data.
- Species overlay shows species dots in the correct period range.
- CLI displays a navigable timeline.

---

## 5. Phase 4 — Learning Modules Batch 1 (M4)

**Goal:** Build the learning engine and publish modules 1–4.

### 5.1 Tasks

| #   | Task                                   | Output File(s)                         |
|-----|----------------------------------------|----------------------------------------|
| 4.1 | Design module `meta.json` schema       | See §12.3                              |
| 4.2 | Design `questions.json` schema         | See §12.4                              |
| 4.3 | Build `LearningService`                | `services/learning.py`                 |
| 4.4 | Write content for Module 1 (5 lessons) | `data/modules/module_01/`              |
| 4.5 | Write content for Module 2 (6 lessons) | `data/modules/module_02/`              |
| 4.6 | Write content for Module 3 (7 lessons) | `data/modules/module_03/`              |
| 4.7 | Write content for Module 4 (5 lessons) | `data/modules/module_04/`              |
| 4.8 | Populate glossary entries              | `data/glossary.json`                   |
| 4.9 | Build web routes + templates           | `web/routes/learning.py`, templates    |
| 4.10| Build CLI commands                     | `cli_ui/learning.py`                   |
| 4.11| Write unit tests                       | `tests/test_learning.py`               |

### 5.2 Service Layer Design

```python
# services/learning.py
from dataclasses import dataclass
import markdown

@dataclass
class Lesson:
    id: str
    title: str
    content_md: str          # raw Markdown
    content_html: str        # rendered HTML (computed)
    key_terms: list[str]     # glossary term IDs
    summary: str
    order: int

@dataclass
class Module:
    id: str
    title: str
    description: str
    lessons: list[Lesson]
    order: int

class LearningService:
    def __init__(self, data_dir: str):
        self._modules: list[Module] = []
        self._load_all(data_dir)

    def get_modules(self) -> list[Module]:
        """Return all modules in order."""

    def get_module(self, module_id: str) -> Module | None:
        """Get a specific module with its lessons."""

    def get_lesson(self, module_id: str, lesson_id: str) -> Lesson | None:
        """Get a specific lesson."""

    def get_lesson_questions(self, module_id: str, lesson_id: str) -> list[dict]:
        """Load questions for the check-your-understanding section."""

    def render_lesson(self, lesson: Lesson) -> str:
        """Convert Markdown to HTML with glossary term linking."""
```

**Glossary linking:** During `render_lesson`, scan the HTML for glossary terms and wrap them in `<abbr>` tags with tooltip definitions, plus link them to `/glossary/<term_id>`.

### 5.3 Content Authoring Workflow

Each lesson file (`lesson_XX.md`) follows this template:

```markdown
---
title: "What is Paleontology?"
order: 1
key_terms: ["paleontology", "fossil", "stratigraphy"]
summary: "Paleontology is the study of ancient life through fossils..."
---

# What is Paleontology?

Paleontology is the scientific study of life that existed prior to...

## The Fossil Record

Fossils are the preserved remains or traces of organisms...

## Why Study Paleontology?

Understanding extinct life helps us understand...
```

YAML frontmatter parsed with `python-frontmatter`. Body rendered with `markdown` library.

### 5.4 Question Schema

Each module's `questions.json`:
```json
{
  "lesson_01": [
    {
      "id": "m01_l01_q01",
      "type": "multiple_choice",
      "difficulty": "beginner",
      "question": "What is the primary subject of paleontology?",
      "options": [
        "The study of rocks",
        "The study of ancient life",
        "The study of modern ecosystems",
        "The study of planetary orbits"
      ],
      "correct": 1,
      "explanation": "Paleontology focuses on ancient life as preserved in the fossil record..."
    }
  ]
}
```

### 5.5 Web Routes

| Method | Path                                    | Description              |
|--------|-----------------------------------------|--------------------------|
| GET    | `/learn`                                | Module list              |
| GET    | `/learn/<module_id>`                    | Module overview + lesson list |
| GET    | `/learn/<module_id>/<lesson_id>`        | Lesson content           |
| POST   | `/learn/<module_id>/<lesson_id>/complete` | Mark lesson complete   |

### 5.6 Web Template Plan

**`learning/modules.html`** — Card grid of modules, each showing title, description, lesson count, and user's completion progress bar.

**`learning/module_detail.html`** — Module title/description, ordered lesson list with checkmarks for completed lessons.

**`learning/lesson.html`** — Full lesson content:
- Rendered Markdown in a readable column (max-width 720px, good typography).
- Sidebar or inline glossary highlights.
- "Check Your Understanding" section at bottom with interactive question forms.
- "Mark Complete & Next" button.

### 5.7 Exit Criteria

- All 4 modules display with correct lesson content.
- Glossary terms are highlighted and linked in lesson text.
- Check-your-understanding questions work with immediate feedback.
- Completing a lesson updates the user's progress.

---

## 6. Phase 5 — Quiz System (M5)

**Goal:** Build the full quiz engine: module quizzes, daily challenge, timed mode.

### 6.1 Tasks

| #   | Task                                  | Output File(s)                          |
|-----|---------------------------------------|-----------------------------------------|
| 5.1 | Build `QuizEngine` service            | `services/quiz_engine.py`              |
| 5.2 | Implement module quiz generation      | (within quiz_engine.py)                |
| 5.3 | Implement daily challenge logic       | (within quiz_engine.py)                |
| 5.4 | Implement timed mode                  | (JS countdown + backend scoring)       |
| 5.5 | Build web routes + templates          | `web/routes/quiz.py`, templates        |
| 5.6 | Build CLI quiz runner                 | `cli_ui/quiz.py`                       |
| 5.7 | Write unit tests                      | `tests/test_quiz_engine.py`            |

### 6.2 Service Layer Design

```python
# services/quiz_engine.py
import random
from datetime import date
from dataclasses import dataclass

@dataclass
class Question:
    id: str
    type: str               # multiple_choice / true_false / short_answer
    difficulty: str          # beginner / intermediate / advanced
    question: str
    options: list[str] | None
    correct: int | str       # index for MC, "true"/"false" for T/F, text for short
    explanation: str
    module_id: str
    lesson_id: str

@dataclass
class QuizResult:
    questions: list[Question]
    answers: list[int | str]
    score: int
    total: int
    duration_sec: int | None

class QuizEngine:
    def __init__(self, learning_service):
        self._learning = learning_service

    def generate_module_quiz(self, module_id: str, difficulty: str = "all",
                             count: int = 10) -> list[Question]:
        """Pull questions from a module's pool, randomize, return subset."""

    def generate_daily_challenge(self) -> list[Question]:
        """Deterministic daily set: seed RNG with today's date,
        draw 10 questions across all modules, mixed difficulty."""

    def generate_timed_quiz(self, difficulty: str, count: int = 20) -> list[Question]:
        """Draw from all modules for a timed session."""

    def score(self, questions: list[Question],
              answers: list[int | str]) -> QuizResult:
        """Compare answers to correct values, compute score."""
```

**Daily challenge determinism:**
```python
def generate_daily_challenge(self) -> list[Question]:
    seed = int(date.today().strftime("%Y%m%d"))
    rng = random.Random(seed)
    all_questions = self._get_all_questions()
    return rng.sample(all_questions, min(10, len(all_questions)))
```

### 6.3 Web Routes

| Method | Path                          | Description                    |
|--------|-------------------------------|--------------------------------|
| GET    | `/quiz`                       | Quiz hub: choose type          |
| GET    | `/quiz/module/<module_id>`    | Start a module quiz            |
| GET    | `/quiz/daily`                 | Start today's daily challenge  |
| GET    | `/quiz/timed`                 | Start a timed quiz             |
| POST   | `/quiz/submit`                | Submit answers, get results    |

### 6.4 Timed Mode (Frontend)

- Server returns questions + `time_limit_sec` (e.g. 300 for 5 minutes).
- Vanilla JS countdown timer displayed at top of page.
- On expiry, form auto-submits with whatever answers are filled.
- No client-side answer validation — all scoring is server-side.

### 6.5 Exit Criteria

- Module quiz draws correct questions from the specified module.
- Daily challenge returns the same questions for all users on the same day.
- Timed mode countdown works; auto-submits on expiry.
- Scores are recorded in `quiz_attempts` table.
- Explanations shown for every question after submission.

---

## 7. Phase 6 — Profiles & Achievements (M6)

**Goal:** User dashboard, progress tracking, streaks, and achievement badges.

### 7.1 Tasks

| #   | Task                                   | Output File(s)                         |
|-----|----------------------------------------|----------------------------------------|
| 6.1 | Build user registration/login flow     | `web/routes/main.py`, `services/user.py` |
| 6.2 | Build `AchievementService`             | `services/achievements.py`             |
| 6.3 | Define achievement catalogue           | `data/achievements.json`               |
| 6.4 | Build dashboard page                   | `web/templates/dashboard.html`         |
| 6.5 | Integrate study session tracking       | Middleware / CLI wrapper               |
| 6.6 | Write unit tests                       | `tests/test_achievements.py`           |

### 7.2 Achievement Catalogue (v1.0)

| Key                      | Name                     | Condition                                      |
|--------------------------|--------------------------|------------------------------------------------|
| `first_lesson`           | First Steps              | Complete any lesson                            |
| `module_complete_{n}`    | Module Master (per mod)  | Complete all lessons in module N               |
| `all_modules`            | Scholar Supreme          | Complete all 8 modules                         |
| `quiz_perfect`           | Flawless                 | Score 100% on any quiz                         |
| `quiz_perfect_advanced`  | Apex Predator            | Score 100% on an Advanced quiz                 |
| `daily_streak_3`         | Three-Day Streak         | Complete daily challenge 3 days running         |
| `daily_streak_7`         | Week Warrior             | Complete daily challenge 7 days running         |
| `daily_streak_30`        | Monthly Monument         | Complete daily challenge 30 days running        |
| `species_explorer_50`    | Fossil Hunter            | View 50 different species in the encyclopedia  |
| `species_explorer_all`   | Walking Encyclopedia     | View every species                             |
| `first_comparison`       | Side by Side             | Use the comparison tool for the first time     |
| `study_time_1h`          | Dedicated Learner        | Accumulate 1 hour of study time                |
| `study_time_10h`         | Devoted Scholar          | Accumulate 10 hours of study time              |

### 7.3 Achievement Checking Logic

Achievements are evaluated **on trigger events**, not by polling:
- `lesson_completed` → check `first_lesson`, `module_complete_*`, `all_modules`
- `quiz_submitted` → check `quiz_perfect`, `quiz_perfect_advanced`, streaks
- `species_viewed` → check `species_explorer_*`
- `session_ended` → check `study_time_*`

```python
# services/achievements.py
class AchievementService:
    def __init__(self, db_session, catalogue_path: str):
        self._db = db_session
        self._catalogue = self._load_catalogue(catalogue_path)

    def check_and_award(self, user_id: int, event: str, context: dict) -> list[str]:
        """Evaluate all achievements triggered by this event.
        Returns list of newly unlocked achievement keys."""

    def get_user_achievements(self, user_id: int) -> list[dict]:
        """Return all achievements with unlocked status for a user."""

    def get_progress(self, user_id: int) -> dict:
        """Return dashboard data: completion %, scores, streaks, study time."""
```

### 7.4 Dashboard Design

The dashboard page (`/dashboard`) shows:
- **Welcome header** with username and "last active" date.
- **Module progress** — horizontal bars for each module (X of Y lessons complete).
- **Quiz stats** — average score, best score, total quizzes taken.
- **Streak counter** — current daily challenge streak.
- **Study time** — total hours logged.
- **Achievements grid** — all badges, greyed out if locked, coloured if earned, with earned date.

### 7.5 User Flow: First-Time Registration

Since this is local-only software, "registration" is lightweight:
1. On first visit (no user in DB), show a "Welcome to DinoScholar" page with a username input.
2. Create `User` row. Set a session cookie with `user_id`.
3. Redirect to dashboard.
4. Subsequent visits: read cookie, look up user, continue.

No passwords — this is a single-machine personal tool.

### 7.6 Exit Criteria

- Dashboard shows accurate progress for a user who has completed some lessons and quizzes.
- Achievements unlock correctly on the triggering event.
- Study session duration is tracked.
- Streak logic correctly counts consecutive days.

---

## 8. Phase 7 — Learning Modules Batch 2 (M7)

**Goal:** Author and publish modules 5–8, populate remaining glossary entries.

### 8.1 Tasks

| #   | Task                                   | Output File(s)                         |
|-----|----------------------------------------|----------------------------------------|
| 7.1 | Write Module 5 — The Great Extinction (4 lessons)     | `data/modules/module_05/` |
| 7.2 | Write Module 6 — Fossils: Discovery to Display (5)    | `data/modules/module_06/` |
| 7.3 | Write Module 7 — Birds: Living Dinosaurs (4)          | `data/modules/module_07/` |
| 7.4 | Write Module 8 — Scientific Method in Paleo (4)       | `data/modules/module_08/` |
| 7.5 | Add glossary entries for new terms                     | `data/glossary.json`      |
| 7.6 | Add quiz questions for modules 5–8                     | `questions.json` per module |

### 8.2 Content Notes

This is a **content-only phase** — no new code. The learning engine from Phase 4 handles everything. The focus is writing high-quality, scientifically accurate educational material.

### 8.3 Exit Criteria

- All 8 modules accessible. 40 total lessons render correctly.
- All glossary terms referenced in lessons exist in `glossary.json`.
- Module quizzes work for modules 5–8.

---

## 9. Phase 8 — Comparative Anatomy (M8)

**Goal:** Side-by-side species comparison tool.

### 9.1 Tasks

| #   | Task                                   | Output File(s)                         |
|-----|----------------------------------------|----------------------------------------|
| 8.1 | Build `ComparisonService`              | `services/comparison.py`               |
| 8.2 | Build web route + template             | `web/routes/encyclopedia.py` (extend), templates |
| 8.3 | Build CLI command                      | `cli_ui/encyclopedia.py` (extend)      |
| 8.4 | Write unit tests                       | `tests/test_comparison.py`             |

### 9.2 Service Layer Design

```python
# services/comparison.py
from dataclasses import dataclass

@dataclass
class ComparisonResult:
    species: list          # list of SpeciesRecord
    size_comparison: dict  # {species_id: {length, height, weight}} for chart data
    shared_traits: list[str]
    differences: list[dict]
    evolutionary_note: str

class ComparisonService:
    def __init__(self, encyclopedia_service):
        self._encyclopedia = encyclopedia_service

    def compare(self, species_ids: list[str]) -> ComparisonResult:
        """Compare 2+ species and return structured comparison data."""

    def _compute_shared_traits(self, species: list) -> list[str]:
        """Find traits shared across all selected species."""

    def _compute_differences(self, species: list) -> list[dict]:
        """Highlight key differences in a structured format."""

    def _generate_evolutionary_note(self, species: list) -> str:
        """Describe taxonomic/evolutionary relationship."""
```

### 9.3 Web Template

**`encyclopedia/compare.html`:**
- Species selector: multi-select dropdown or search box to add species (2–4 max).
- Side-by-side cards showing each species' key stats.
- Bar chart (CSS-based, no charting library) comparing length, height, weight.
- Shared traits / differences section.
- Evolutionary relationship note.

### 9.4 CLI Output

```
┌─────────────────┬────────────────────┬────────────────────┐
│                 │ T. rex             │ Triceratops        │
├─────────────────┼────────────────────┼────────────────────┤
│ Period          │ Late Cretaceous    │ Late Cretaceous    │
│ Diet            │ Carnivore          │ Herbivore          │
│ Length          │ 12.3 m  ████████   │ 9.0 m  ██████     │
│ Height          │ 3.7 m   ████       │ 3.0 m  ███        │
│ Weight          │ 8400 kg ████████   │ 6000 kg ██████    │
│ Locomotion      │ Bipedal            │ Quadrupedal        │
├─────────────────┼────────────────────┴────────────────────┤
│ Shared          │ Late Cretaceous, North America          │
│ Evolutionary    │ Both dinosaurs but different orders...   │
└─────────────────┴─────────────────────────────────────────┘
```

### 9.5 Exit Criteria

- Comparison page renders correctly for any 2–4 species.
- Size bars are proportionally accurate.
- Shared traits and differences are logically correct.

---

## 10. Phase 9 — Polish & Testing (M9)

**Goal:** Full test coverage, bug fixes, UI refinement, documentation.

### 10.1 Tasks

| #    | Task                                  |
|------|---------------------------------------|
| 9.1  | Achieve ≥80% test coverage            |
| 9.2  | Cross-browser testing (Chrome, Firefox, Safari) |
| 9.3  | Keyboard navigation audit (web)       |
| 9.4  | Screen reader testing with NVDA       |
| 9.5  | Performance audit: startup < 3s       |
| 9.6  | Content review: fact-check all lessons |
| 9.7  | Fix all known bugs                    |
| 9.8  | Write `README.md`                     |
| 9.9  | Add `--version` flag and release tag  |
| 9.10 | Final manual walkthrough of all flows |

---

## 11. Content Population Strategy

### 11.1 Species Data

**Source:** Paleobiology Database (PBDB) — `https://paleobiodb.org/data1.2/`

**Population script** (`scripts/populate_species.py`):
1. Query PBDB API for Dinosauria occurrences with taxonomic and geographic data.
2. Deduplicate by genus, select the ~200 best-documented species.
3. Map API fields to our `SpeciesRecord` schema.
4. For each species, generate a description stub and fun facts placeholder.
5. Output to `data/species.json`.
6. Manually review and enrich top ~50 flagship species (T. rex, Triceratops, Velociraptor, etc.) with hand-written descriptions.

**PBDB API example query:**
```
GET paleobiodb.org/data1.2/occs/list.json?base_name=Dinosauria&show=full&limit=500
```

### 11.2 Timeline Data

**Source:** International Chronostratigraphic Chart (ICS 2024).

Manually encoded — this is a small, stable dataset (~15 entries). No automation needed.

### 11.3 Glossary

Authored progressively during lesson writing. Each lesson defines its `key_terms` in YAML frontmatter; we maintain a `glossary.json` file that grows with each module.

### 11.4 Lesson Content

**Approach:** Draft each lesson with an LLM, then fact-check against:
- Peer-reviewed sources (accessible via Google Scholar).
- Museum educational materials (AMNH, Smithsonian, NHM London — all have open educational text).
- Wikipedia (for factual scaffolding, not as a primary source).

All text is original prose — never copy-pasted from any source.

### 11.5 Quiz Questions

Written per lesson during content authoring. Target: 3–5 questions per lesson = ~160–200 total. Each question includes a detailed explanation.

---

## 12. Data Schema Details

### 12.1 `species.json`

```json
[
  {
    "id": "tyrannosaurus-rex",
    "scientific_name": "Tyrannosaurus rex",
    "common_name": "Tyrant Lizard King",
    "classification": {
      "order": "Saurischia",
      "suborder": "Theropoda",
      "family": "Tyrannosauridae",
      "genus": "Tyrannosaurus"
    },
    "period": {
      "name": "Late Cretaceous",
      "start_mya": 68.0,
      "end_mya": 66.0
    },
    "diet": "carnivore",
    "size": {
      "length_m": 12.3,
      "height_m": 3.7,
      "weight_kg": 8400
    },
    "locomotion": "bipedal",
    "fossil_locations": [
      "North America — Montana, South Dakota, Wyoming, Alberta"
    ],
    "description": "Tyrannosaurus rex is among the largest land predators...",
    "fun_facts": [
      "T. rex had a bite force of over 12,800 pounds.",
      "Its tiny arms could still bench-press about 400 pounds."
    ],
    "related_species": ["albertosaurus", "gorgosaurus", "tarbosaurus"]
  }
]
```

### 12.2 `timeline.json`

```json
[
  {
    "id": "late-cretaceous",
    "name": "Late Cretaceous",
    "era": "Mesozoic",
    "start_mya": 100.5,
    "end_mya": 66.0,
    "climate": "Warm greenhouse climate with no polar ice. Sea levels were high...",
    "key_events": [
      "Deccan Traps volcanism begins (~68 MYA)",
      "Chicxulub impact and K-Pg mass extinction (66 MYA)",
      "Flowering plants diversify rapidly"
    ],
    "dominant_species": ["tyrannosaurus-rex", "triceratops", "edmontosaurus"],
    "description": "The Late Cretaceous was the final chapter of the Age of Dinosaurs..."
  }
]
```

### 12.3 Module `meta.json`

```json
{
  "id": "module_01",
  "title": "Introduction to Paleontology",
  "description": "A foundation course covering what paleontology is, how fossils form...",
  "order": 1,
  "lessons": [
    {"id": "lesson_01", "title": "What is Paleontology?", "file": "lesson_01.md"},
    {"id": "lesson_02", "title": "How Fossils Form", "file": "lesson_02.md"},
    {"id": "lesson_03", "title": "Types of Fossils", "file": "lesson_03.md"},
    {"id": "lesson_04", "title": "Dating Fossils", "file": "lesson_04.md"},
    {"id": "lesson_05", "title": "Famous Fossil Sites", "file": "lesson_05.md"}
  ]
}
```

### 12.4 Module `questions.json`

```json
{
  "lesson_01": [
    {
      "id": "m01_l01_q01",
      "type": "multiple_choice",
      "difficulty": "beginner",
      "question": "What is the primary subject of paleontology?",
      "options": [
        "The study of rocks and minerals",
        "The study of ancient life through fossils",
        "The study of modern animal behaviour",
        "The study of weather patterns"
      ],
      "correct": 1,
      "explanation": "Paleontology is specifically the study of ancient life..."
    },
    {
      "id": "m01_l01_q02",
      "type": "true_false",
      "difficulty": "beginner",
      "question": "Paleontology and archaeology are the same discipline.",
      "correct": "false",
      "explanation": "Archaeology studies human history and artefacts..."
    }
  ]
}
```

### 12.5 `glossary.json`

```json
[
  {
    "id": "paleontology",
    "term": "Paleontology",
    "definition": "The scientific study of prehistoric life through the examination of fossils.",
    "related_terms": ["fossil", "stratigraphy", "taxonomy"]
  },
  {
    "id": "fossil",
    "term": "Fossil",
    "definition": "The preserved remains, impressions, or traces of organisms from past geological ages.",
    "related_terms": ["paleontology", "permineralization", "trace-fossil"]
  }
]
```

### 12.6 `achievements.json`

```json
[
  {
    "key": "first_lesson",
    "name": "First Steps",
    "description": "Complete your first lesson.",
    "icon": "footprints",
    "trigger_event": "lesson_completed"
  },
  {
    "key": "quiz_perfect",
    "name": "Flawless",
    "description": "Score 100% on any quiz.",
    "icon": "star",
    "trigger_event": "quiz_submitted"
  }
]
```

---

## 13. API & Route Design

Complete route table for the Flask web application:

| Method | Path                                      | Handler                     | Description                        |
|--------|-------------------------------------------|-----------------------------|------------------------------------|
| GET    | `/`                                       | `main.home`                 | Home / landing page                |
| GET    | `/dashboard`                              | `main.dashboard`            | User progress dashboard            |
| POST   | `/register`                               | `main.register`             | Create user profile                |
| GET    | `/encyclopedia`                           | `encyclopedia.list`         | Species list with search/filter    |
| GET    | `/encyclopedia/<id>`                      | `encyclopedia.detail`       | Species detail page                |
| GET    | `/encyclopedia/compare`                   | `encyclopedia.compare`      | Comparison tool                    |
| GET    | `/timeline`                               | `timeline.index`            | Geological timeline view           |
| GET    | `/timeline/<period_id>`                   | `timeline.period_detail`    | Period detail (AJAX or full page)  |
| GET    | `/learn`                                  | `learning.modules`          | Module list                        |
| GET    | `/learn/<module_id>`                      | `learning.module_detail`    | Module overview                    |
| GET    | `/learn/<module_id>/<lesson_id>`          | `learning.lesson`           | Lesson content                     |
| POST   | `/learn/<module_id>/<lesson_id>/complete` | `learning.mark_complete`    | Mark lesson done                   |
| GET    | `/quiz`                                   | `quiz.hub`                  | Quiz type selector                 |
| GET    | `/quiz/module/<module_id>`                | `quiz.module_quiz`          | Module quiz page                   |
| GET    | `/quiz/daily`                             | `quiz.daily_challenge`      | Daily challenge page               |
| GET    | `/quiz/timed`                             | `quiz.timed_quiz`           | Timed quiz page                    |
| POST   | `/quiz/submit`                            | `quiz.submit`               | Submit quiz answers                |
| GET    | `/glossary`                               | `main.glossary`             | Full glossary                      |
| GET    | `/glossary/<term_id>`                     | `main.glossary_term`        | Single term definition             |

---

## 14. CLI Command Design

```
dinoscholar
├── encyclopedia
│   ├── list     [--period] [--diet] [--sort]     List all species
│   ├── search   <query>                           Search species
│   ├── show     <species_id>                      View species detail
│   └── compare  <id1> <id2> [<id3>] [<id4>]      Compare species
├── timeline
│   ├── show                                       Display full timeline
│   └── period   <period_id>                       Show period detail
├── learn
│   ├── modules                                    List all modules
│   ├── start    <module_id>                       Begin / resume a module
│   └── lesson   <module_id> <lesson_id>           Read a specific lesson
├── quiz
│   ├── module   <module_id> [--difficulty]         Module quiz
│   ├── daily                                       Daily challenge
│   └── timed    [--difficulty] [--count]           Timed quiz
├── glossary
│   ├── list                                       All terms
│   └── lookup   <term>                            Look up a term
├── dashboard                                      Show progress
└── --version                                      Print version
```

All CLI output uses the `rich` library for colour, tables, and formatted text. Lesson Markdown rendered with `rich.markdown`.

---

## 15. UI/UX Wireframes

### 15.1 Home Page (Web)

```
┌──────────────────────────────────────────────────────────┐
│  🦕 DinoScholar          [Encyclopedia] [Timeline]       │
│                          [Learn] [Quiz] [Dashboard]      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│     Welcome to DinoScholar                               │
│     Your journey into the world of dinosaurs             │
│     starts here.                                         │
│                                                          │
│     ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│     │ Start    │  │ Browse   │  │ Take a   │            │
│     │ Learning │  │ Species  │  │ Quiz     │            │
│     └──────────┘  └──────────┘  └──────────┘            │
│                                                          │
│     Daily Challenge: 10 questions — [Start]              │
│     Your streak: 3 days                                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 15.2 Encyclopedia List (Web)

```
┌──────────────────────────────────────────────────────────┐
│  🦕 DinoScholar          [Encyclopedia] [Timeline] ...   │
├──────────────────────────────────────────────────────────┤
│  Search: [___________________________] [Search]          │
│                                                          │
│  Filters:                                                │
│  Period: [All ▾]  Diet: [All ▾]  Size: [0]──[50m]       │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Tyrannosaurus rex    │ Late Cretaceous │ Carnivore │  │
│  │ Triceratops horridus │ Late Cretaceous │ Herbivore │  │
│  │ Velociraptor mong.   │ Late Cretaceous │ Carnivore │  │
│  │ Stegosaurus stenops  │ Late Jurassic   │ Herbivore │  │
│  │ ...                  │                 │           │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  Page 1 of 8    [< Prev]  [Next >]                       │
└──────────────────────────────────────────────────────────┘
```

### 15.3 Lesson View (Web)

```
┌──────────────────────────────────────────────────────────┐
│  Module 1 > Lesson 1: What is Paleontology?              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  # What is Paleontology?                                 │
│                                                          │
│  Paleontology is the scientific study of ancient life    │
│  through the examination of [fossils]. The field         │
│  bridges biology and geology...                          │
│                                                          │
│  ## The Fossil Record                                    │
│  ...                                                     │
│                                                          │
│  ─────────────────────────────────────────                │
│  Key Terms: [paleontology] [fossil] [stratigraphy]       │
│  ─────────────────────────────────────────                │
│                                                          │
│  ### Check Your Understanding                            │
│  1. What is the primary subject of paleontology?         │
│     ○ The study of rocks                                 │
│     ● The study of ancient life  ✓ Correct!              │
│     ○ The study of modern ecosystems                     │
│     ○ The study of planetary orbits                      │
│                                                          │
│  [Mark Complete & Continue →]                            │
└──────────────────────────────────────────────────────────┘
```

### 15.4 Dashboard (Web)

```
┌──────────────────────────────────────────────────────────┐
│  Dashboard — Welcome back, Alex                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Module Progress                                         │
│  1. Intro to Paleontology     ████████░░  4/5 (80%)     │
│  2. The Mesozoic World        ██░░░░░░░░  1/6 (17%)     │
│  3. Dinosaur Anatomy          ░░░░░░░░░░  0/7  (0%)     │
│  ...                                                     │
│                                                          │
│  Quiz Stats                      Streak                  │
│  Avg Score: 78%                  🔥 3 days               │
│  Best Score: 100%                                        │
│  Total Quizzes: 12               Study Time: 4.2 hrs     │
│                                                          │
│  Achievements                                            │
│  [✓ First Steps] [✓ Flawless] [  Apex Predator  ]       │
│  [  Week Warrior ] [✓ Fossil Hunter] [  Scholar  ]       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 16. Testing Strategy

### 16.1 Unit Tests

| Test File                  | Covers                                          |
|----------------------------|-------------------------------------------------|
| `test_encyclopedia.py`     | Search, filter, retrieval, edge cases            |
| `test_timeline.py`         | Period loading, chronological ordering, cross-ref |
| `test_learning.py`         | Module/lesson loading, Markdown rendering, glossary linking |
| `test_quiz_engine.py`      | Question sampling, scoring, daily determinism, timed logic |
| `test_comparison.py`       | Multi-species comparison, shared traits, size math |
| `test_achievements.py`     | Event-triggered unlock logic, streak calculation  |
| `test_models.py`           | ORM model creation, constraints, relationships   |

### 16.2 Integration Tests

- **Web routes:** Use Flask test client to hit every route and verify status codes + key content.
- **CLI commands:** Use Click's `CliRunner` to invoke every command and check output.

### 16.3 Content Validation Tests

- Every species in `species.json` passes schema validation.
- Every module's `meta.json` references lesson files that exist.
- Every `questions.json` entry has a valid `correct` value.
- Every `key_term` referenced in lesson frontmatter exists in `glossary.json`.
- No broken `related_species` links in `species.json`.

### 16.4 Coverage Target

- **≥80% line coverage** overall.
- **100% coverage** on `quiz_engine.py` scoring logic (correctness-critical).

---

## 17. Dependency List

```
# requirements.txt
flask>=3.0,<4.0
flask-sqlalchemy>=3.1,<4.0
sqlalchemy>=2.0,<3.0
click>=8.1,<9.0
rich>=13.0,<14.0
markdown>=3.5,<4.0
python-frontmatter>=1.1,<2.0
pytest>=8.0,<9.0
pytest-cov>=5.0,<6.0
ruff>=0.3,<1.0
```

No heavy dependencies. No JavaScript build tooling — Bootstrap 5 loaded via CDN or vendored.

---

## 18. Risk Register

| Risk                                    | Impact | Likelihood | Mitigation                                        |
|-----------------------------------------|--------|------------|---------------------------------------------------|
| PBDB API changes or goes down           | Medium | Low        | Cache results locally; script only runs once       |
| Content inaccuracies slip through       | High   | Medium     | Dedicated fact-check pass in Phase 9; cite sources |
| Scope creep from future enhancements    | Medium | Medium     | Strict v1.0 boundary; future features documented but deferred |
| SQLite locking under heavy CLI use      | Low    | Low        | WAL mode enabled; single-user design               |
| Lesson Markdown rendering edge cases    | Low    | Medium     | Use well-tested `markdown` library; test with varied content |
| Bootstrap CDN unavailable offline       | Medium | Low        | Vendor Bootstrap CSS/JS into `static/` for offline use |

---

*End of design plan.*
