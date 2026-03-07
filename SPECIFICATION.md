# DinoScholar — Dinosaur-Themed Adult Education Platform

## Specification Document

**Version:** 1.0  
**Date:** March 6, 2026  
**Language:** Python  

---

## 1. Overview

**DinoScholar** is an interactive, terminal-and-web-based adult education platform built in Python. It uses dinosaurs as the central theme to teach real scientific concepts — paleontology, evolutionary biology, geological time, comparative anatomy, and the scientific method. The platform is designed for adult learners seeking structured, self-paced education with depth and rigor, not a children's game.

---

## 2. Goals

- Deliver genuinely educational content about dinosaurs, Earth history, and biology at an adult level.
- Provide multiple learning modes: structured courses, quiz challenges, interactive timeline exploration, and a specimen database.
- Track learner progress with a profile and achievement system.
- Be extensible — easy to add new modules, species, and quiz content.
- Run as a local web application (Flask) with optional CLI mode for terminal enthusiasts.

---

## 3. Target Audience

Adults (18+) who are:
- Curious about paleontology and natural history.
- Seeking structured self-study outside a university setting.
- Looking for a science-based hobby project or refresher.

---

## 4. Core Features

### 4.1 Species Encyclopedia

A searchable, filterable database of dinosaur species.

| Field             | Description                                      |
|-------------------|--------------------------------------------------|
| Name              | Scientific and common name                       |
| Classification    | Order, suborder, family, genus                   |
| Period            | Triassic / Jurassic / Cretaceous + date range (MYA) |
| Diet              | Herbivore / Carnivore / Omnivore                 |
| Size              | Length, height, estimated weight                  |
| Locomotion        | Bipedal / Quadrupedal                            |
| Fossil Locations  | Continents and key dig sites                     |
| Description       | Multi-paragraph educational summary              |
| Fun Facts         | Curated interesting details                      |
| Related Species   | Links to taxonomically close entries             |

- Full-text search and filtering by period, diet, size range, and location.
- Each entry rendered as a detailed profile page (web) or formatted output (CLI).

### 4.2 Geological Timeline Explorer

An interactive timeline visualising the Mesozoic Era and surrounding periods.

- Displays eras, periods, and epochs with date ranges.
- Clicking/selecting a period shows: climate, dominant species, key events (mass extinctions, continental drift stages).
- Overlay species data onto the timeline to see which dinosaurs coexisted.
- Educational annotations explaining concepts like radiometric dating and stratigraphy.

### 4.3 Structured Learning Modules

Self-paced courses broken into lessons, each with reading material, diagrams (ASCII in CLI / images in web), and a short quiz.

**Module list (v1.0):**

| #  | Module Title                          | Lessons |
|----|---------------------------------------|---------|
| 1  | Introduction to Paleontology          | 5       |
| 2  | The Mesozoic World                    | 6       |
| 3  | Dinosaur Anatomy & Physiology        | 7       |
| 4  | Predators & Prey — Dinosaur Ecology   | 5       |
| 5  | The Great Extinction (K-Pg Event)     | 4       |
| 6  | Fossils: From Discovery to Display   | 5       |
| 7  | Birds: Living Dinosaurs              | 4       |
| 8  | The Scientific Method in Paleontology | 4       |

Each lesson includes:
- **Reading** — 500–1500 words of educational content.
- **Key Terms** — Glossary entries linked to a global glossary.
- **Check Your Understanding** — 3–5 questions (multiple choice, true/false, or short answer).
- **Lesson Summary** — Concise recap.

### 4.4 Quiz & Challenge System

- **Module quizzes** — Automatically generated from lesson question pools.
- **Daily Challenge** — A rotating set of 10 mixed-difficulty questions across all topics.
- **Timed Mode** — Optional countdown for competitive self-testing.
- **Difficulty levels** — Beginner, Intermediate, Advanced. Questions are tagged and filtered accordingly.
- **Explanations** — Every answer (correct or incorrect) shows a detailed explanation.

### 4.5 Comparative Anatomy Tool

An interactive feature where the user selects two or more species and sees a side-by-side comparison:

- Size comparison (visual bar chart or ASCII art).
- Diet, period, classification differences.
- Shared vs. divergent traits.
- Evolutionary relationship summary.

### 4.6 User Profile & Progress Tracking

- Local user profile (SQLite-backed).
- Tracks: completed lessons, quiz scores, streaks, total study time.
- **Achievements** — Unlockable badges (e.g., "Completed all Cretaceous quizzes", "7-day streak", "Perfect score on Advanced quiz").
- Progress dashboard showing completion percentage per module.

### 4.7 Glossary

- A comprehensive glossary of paleontological and geological terms.
- Cross-linked from lesson content and encyclopedia entries.
- Searchable independently.

---

## 5. Technical Architecture

### 5.1 Project Structure

```
dinoscholar/
├── app.py                  # Flask application entry point
├── cli.py                  # CLI entry point (Click-based)
├── config.py               # App configuration
├── requirements.txt
├── README.md
├── data/
│   ├── species.json        # Dinosaur species database
│   ├── timeline.json       # Geological periods data
│   ├── glossary.json       # Term definitions
│   └── modules/
│       ├── module_01/
│       │   ├── meta.json   # Module metadata
│       │   ├── lesson_01.md
│       │   ├── lesson_02.md
│       │   └── questions.json
│       └── ...
├── models/
│   ├── __init__.py
│   ├── species.py          # Species data model
│   ├── user.py             # User profile model
│   ├── progress.py         # Progress tracking model
│   └── quiz.py             # Quiz/question model
├── services/
│   ├── __init__.py
│   ├── encyclopedia.py     # Species search & retrieval
│   ├── timeline.py         # Timeline data service
│   ├── learning.py         # Module/lesson management
│   ├── quiz_engine.py      # Quiz generation & scoring
│   ├── comparison.py       # Comparative anatomy logic
│   └── achievements.py     # Achievement tracking
├── web/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py         # Home, dashboard routes
│   │   ├── encyclopedia.py # Species routes
│   │   ├── timeline.py     # Timeline routes
│   │   ├── learning.py     # Module/lesson routes
│   │   └── quiz.py         # Quiz routes
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── encyclopedia/
│   │   ├── timeline/
│   │   ├── learning/
│   │   └── quiz/
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── cli_ui/
│   ├── __init__.py
│   ├── encyclopedia.py     # CLI encyclopedia commands
│   ├── timeline.py         # CLI timeline display
│   ├── learning.py         # CLI lesson viewer
│   └── quiz.py             # CLI quiz runner
├── database/
│   ├── __init__.py
│   ├── db.py               # SQLite connection management
│   └── migrations/         # Schema migrations
└── tests/
    ├── test_encyclopedia.py
    ├── test_quiz_engine.py
    ├── test_learning.py
    ├── test_comparison.py
    └── test_achievements.py
```

### 5.2 Technology Stack

| Component       | Technology                        |
|-----------------|-----------------------------------|
| Language         | Python 3.10+                     |
| Web Framework    | Flask 3.x                        |
| CLI Framework    | Click                            |
| Database         | SQLite (via SQLAlchemy)          |
| Templating       | Jinja2 (Flask default)           |
| Frontend CSS     | Bootstrap 5 (minimal custom JS) |
| Data Format      | JSON for static content, Markdown for lessons |
| Testing          | pytest                           |
| Linting          | ruff                             |
| Package Mgmt     | pip + requirements.txt           |

### 5.3 Database Schema

```
users
├── id              INTEGER PRIMARY KEY
├── username        TEXT UNIQUE NOT NULL
├── created_at      DATETIME
└── last_active     DATETIME

lesson_progress
├── id              INTEGER PRIMARY KEY
├── user_id         INTEGER FK → users.id
├── module_id       TEXT NOT NULL
├── lesson_id       TEXT NOT NULL
├── completed       BOOLEAN DEFAULT FALSE
├── completed_at    DATETIME
└── UNIQUE(user_id, module_id, lesson_id)

quiz_attempts
├── id              INTEGER PRIMARY KEY
├── user_id         INTEGER FK → users.id
├── quiz_type       TEXT NOT NULL  (module / daily / timed)
├── module_id       TEXT NULLABLE
├── score           INTEGER NOT NULL
├── total           INTEGER NOT NULL
├── difficulty      TEXT NOT NULL
├── started_at      DATETIME
└── completed_at    DATETIME

achievements
├── id              INTEGER PRIMARY KEY
├── user_id         INTEGER FK → users.id
├── achievement_key TEXT NOT NULL
├── unlocked_at     DATETIME
└── UNIQUE(user_id, achievement_key)

study_sessions
├── id              INTEGER PRIMARY KEY
├── user_id         INTEGER FK → users.id
├── started_at      DATETIME
└── duration_sec    INTEGER
```

### 5.4 Key Design Decisions

1. **Content as data files** — All educational content lives in JSON/Markdown under `data/`. This separates content authoring from code and makes it trivial to add or update material without touching Python.
2. **Dual interface** — Flask web UI for a richer experience; Click CLI for terminal users. Both share the same `services/` layer.
3. **SQLite** — No server dependency. The database file lives locally. Suitable for single-user, local-first education software.
4. **No external API dependency** — All content is bundled. The app works fully offline.

---

## 6. User Flows

### 6.1 First Launch
1. User runs `python app.py` (web) or `python cli.py` (CLI).
2. Prompted to create a username.
3. Shown a welcome screen with a brief orientation and link to Module 1.

### 6.2 Studying a Lesson
1. User navigates to a module → selects a lesson.
2. Reads the lesson content (rendered Markdown).
3. Reviews key terms (linked to glossary).
4. Completes the "Check Your Understanding" questions.
5. Lesson marked as complete; progress updated.

### 6.3 Taking a Quiz
1. User selects quiz type (module review, daily challenge, or timed).
2. Questions are drawn from the question pool, randomized.
3. User answers each question; immediate feedback after each (or at end for timed mode).
4. Score recorded; achievements checked and awarded if earned.

### 6.4 Exploring the Encyclopedia
1. User opens the encyclopedia.
2. Browses species list or uses search/filter.
3. Selects a species → views detailed profile.
4. Optionally sends species to the comparison tool.

---

## 7. Content Guidelines

- All content must be scientifically accurate and cite current paleontological consensus.
- Writing level: clear, accessible prose suitable for an educated adult audience. No condescension.
- Avoid overly technical jargon without definition; all specialist terms must appear in the glossary.
- Where scientific debate exists (e.g., warm-blooded vs. cold-blooded dinosaurs), present multiple perspectives fairly.

---

## 8. Non-Functional Requirements

| Requirement       | Target                                           |
|-------------------|--------------------------------------------------|
| Startup time      | < 3 seconds to first page load                   |
| Offline capable   | 100% — no network required after installation     |
| Data safety       | SQLite WAL mode; no data loss on crash            |
| Accessibility     | Semantic HTML; keyboard navigable; screen-reader friendly (web) |
| Cross-platform    | Windows, macOS, Linux                             |
| Python version    | 3.10 or higher                                    |

---

## 9. Future Enhancements (Out of Scope for v1.0)

- **Spaced repetition** — Integrate an SRS algorithm for long-term retention of quiz material.
- **3D model viewer** — Embed simple 3D dinosaur skeletal models in the web UI.
- **Community content** — Allow users to submit species entries or quiz questions.
- **PDF export** — Export completed module notes and quiz results as PDF.
- **AI tutor** — LLM-powered Q&A for freeform dinosaur questions.
- **Multiplayer quizzes** — Networked competitive quiz mode.

---

## 10. Milestones

| Milestone | Deliverable                                   | Description                                           |
|-----------|-----------------------------------------------|-------------------------------------------------------|
| M1        | Project skeleton & data models                | Project structure, database schema, config, base templates |
| M2        | Species encyclopedia                          | Full species database + search/filter + web & CLI views |
| M3        | Geological timeline                           | Interactive timeline with period data and species overlay |
| M4        | Learning modules (Modules 1–4)                | First four courses with lessons, glossary, and quizzes |
| M5        | Quiz & challenge system                       | Module quizzes, daily challenge, timed mode, scoring   |
| M6        | User profiles & achievements                  | Progress tracking, dashboard, achievement badges       |
| M7        | Learning modules (Modules 5–8)                | Remaining four courses                                 |
| M8        | Comparative anatomy tool                      | Side-by-side species comparison feature                |
| M9        | Polish & testing                              | Full test suite, bug fixes, UI polish, documentation   |

---

## 11. Getting Started (Post-Spec)

Once approved, development begins at **M1**:

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from database.db import init_db; init_db()"

# Run web app
python app.py

# Or run CLI
python cli.py --help
```

---

*End of specification.*
