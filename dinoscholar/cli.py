import os
import click
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.panel import Panel

from services.encyclopedia import EncyclopediaService
from services.timeline import TimelineService
from services.learning import LearningService
from services.quiz_engine import QuizEngine
from services.comparison import ComparisonService

console = Console()
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def get_services():
    enc = EncyclopediaService(DATA_DIR)
    timeline = TimelineService(DATA_DIR, encyclopedia_service=enc)
    learning = LearningService(DATA_DIR)
    quiz = QuizEngine(learning)
    comparison = ComparisonService(enc)
    return enc, timeline, learning, quiz, comparison


@click.group()
@click.version_option(version="1.0.0", prog_name="DinoScholar")
def cli():
    """🦕 DinoScholar — Adult Dinosaur Education Platform"""
    pass


# ─── Encyclopedia ────────────────────────────────────────


@cli.group()
def encyclopedia():
    """Browse and search the dinosaur species encyclopedia."""
    pass


@encyclopedia.command("list")
@click.option("--period", default=None, help="Filter by geological period")
@click.option("--diet", default=None, help="Filter by diet (herbivore/carnivore/omnivore)")
@click.option("--sort", default="scientific_name", help="Sort field")
def enc_list(period, diet, sort):
    """List all dinosaur species."""
    enc, *_ = get_services()
    if period or diet:
        species = enc.filter(period=period, diet=diet)
    else:
        species = enc.list_all(sort_by=sort)

    table = Table(title="Dinosaur Species Encyclopedia")
    table.add_column("Species", style="bold green")
    table.add_column("Period")
    table.add_column("Diet")
    table.add_column("Length (m)", justify="right")
    table.add_column("Weight (kg)", justify="right")

    for sp in species:
        table.add_row(
            sp.scientific_name,
            sp.period,
            sp.diet.capitalize(),
            f"{sp.length_m}",
            f"{int(sp.weight_kg)}",
        )
    console.print(table)


@encyclopedia.command("search")
@click.argument("query")
def enc_search(query):
    """Search species by name or description."""
    enc, *_ = get_services()
    results = enc.search(query)
    if not results:
        console.print("[yellow]No species found.[/yellow]")
        return
    for sp in results:
        console.print(f"  [bold green]{sp.scientific_name}[/bold green] — {sp.period}, {sp.diet}")


@encyclopedia.command("show")
@click.argument("species_id")
def enc_show(species_id):
    """Show detailed information about a species."""
    enc, *_ = get_services()
    sp = enc.get(species_id)
    if not sp:
        console.print("[red]Species not found.[/red]")
        return
    console.print(Panel(
        f"[bold]{sp.scientific_name}[/bold]\n"
        f"Common name: {sp.common_name}\n"
        f"Period: {sp.period} ({sp.period_start_mya}–{sp.period_end_mya} MYA)\n"
        f"Diet: {sp.diet.capitalize()}\n"
        f"Size: {sp.length_m}m long, {sp.height_m}m tall, {int(sp.weight_kg)}kg\n"
        f"Locomotion: {sp.locomotion.capitalize()}\n"
        f"Order: {sp.order} > {sp.suborder} > {sp.family}\n\n"
        f"{sp.description}",
        title=sp.scientific_name,
    ))
    if sp.fun_facts:
        console.print("\n[bold]Fun Facts:[/bold]")
        for fact in sp.fun_facts:
            console.print(f"  • {fact}")
    if sp.fossil_locations:
        console.print("\n[bold]Fossil Locations:[/bold]")
        for loc in sp.fossil_locations:
            console.print(f"  📍 {loc}")


@encyclopedia.command("compare")
@click.argument("ids", nargs=-1, required=True)
def enc_compare(ids):
    """Compare 2-4 species side by side."""
    enc, _, _, _, comparison = get_services()
    result = comparison.compare(list(ids))
    if not result:
        console.print("[red]Need at least 2 valid species IDs.[/red]")
        return

    table = Table(title="Species Comparison")
    table.add_column("Trait", style="bold")
    for sp in result.species:
        table.add_column(sp.scientific_name)

    rows = [
        ("Period", [sp.period for sp in result.species]),
        ("Diet", [sp.diet.capitalize() for sp in result.species]),
        ("Length", [f"{sp.length_m} m" for sp in result.species]),
        ("Height", [f"{sp.height_m} m" for sp in result.species]),
        ("Weight", [f"{int(sp.weight_kg)} kg" for sp in result.species]),
        ("Locomotion", [sp.locomotion.capitalize() for sp in result.species]),
    ]
    for label, values in rows:
        table.add_row(label, *values)
    console.print(table)

    if result.shared_traits:
        console.print("\n[bold]Shared Traits:[/bold]")
        for t in result.shared_traits:
            console.print(f"  • {t}")
    if result.evolutionary_note:
        console.print(f"\n[bold]Evolutionary Note:[/bold] {result.evolutionary_note}")


# ─── Timeline ────────────────────────────────────────────


@cli.group()
def timeline():
    """Explore the geological timeline."""
    pass


@timeline.command("show")
def timeline_show():
    """Display the full geological timeline."""
    _, tl, *_ = get_services()
    periods = tl.get_all_periods()
    if not periods:
        console.print("[yellow]No timeline data available.[/yellow]")
        return
    table = Table(title="Geological Timeline")
    table.add_column("Period", style="bold")
    table.add_column("Era")
    table.add_column("Start (MYA)", justify="right")
    table.add_column("End (MYA)", justify="right")
    for p in periods:
        table.add_row(p.name, p.era, f"{p.start_mya}", f"{p.end_mya}")
    console.print(table)


@timeline.command("period")
@click.argument("period_id")
def timeline_period(period_id):
    """Show details for a geological period."""
    _, tl, *_ = get_services()
    p = tl.get_period(period_id)
    if not p:
        console.print("[red]Period not found.[/red]")
        return
    console.print(Panel(
        f"[bold]{p.name}[/bold] ({p.era} Era)\n"
        f"{p.start_mya}–{p.end_mya} MYA\n\n"
        f"{p.description}\n\n"
        f"[bold]Climate:[/bold] {p.climate}",
        title=p.name,
    ))
    if p.key_events:
        console.print("\n[bold]Key Events:[/bold]")
        for e in p.key_events:
            console.print(f"  • {e}")


# ─── Learn ───────────────────────────────────────────────


@cli.group()
def learn():
    """Study structured learning modules."""
    pass


@learn.command("modules")
def learn_modules():
    """List all available learning modules."""
    _, _, learning, *_ = get_services()
    modules = learning.get_modules()
    if not modules:
        console.print("[yellow]No modules available.[/yellow]")
        return
    table = Table(title="Learning Modules")
    table.add_column("#", justify="right")
    table.add_column("Title", style="bold")
    table.add_column("Lessons", justify="right")
    for m in modules:
        table.add_row(str(m.order), m.title, str(len(m.lessons)))
    console.print(table)


@learn.command("lesson")
@click.argument("module_id")
@click.argument("lesson_id")
def learn_lesson(module_id, lesson_id):
    """Read a specific lesson."""
    _, _, learning, *_ = get_services()
    lesson = learning.get_lesson(module_id, lesson_id)
    if not lesson:
        console.print("[red]Lesson not found.[/red]")
        return
    console.print(Panel(f"[bold]{lesson.title}[/bold]", subtitle=f"{module_id} / {lesson_id}"))
    console.print(Markdown(lesson.content_md))
    if lesson.summary:
        console.print(f"\n[bold]Summary:[/bold] {lesson.summary}")


# ─── Quiz ────────────────────────────────────────────────


@cli.group()
def quiz():
    """Take quizzes and challenges."""
    pass


@quiz.command("module")
@click.argument("module_id")
@click.option("--difficulty", default="all", help="beginner/intermediate/advanced/all")
def quiz_module(module_id, difficulty):
    """Take a module quiz."""
    _, _, learning, engine, _ = get_services()
    questions = engine.generate_module_quiz(module_id, difficulty=difficulty)
    _run_cli_quiz(questions, engine)


@quiz.command("daily")
def quiz_daily():
    """Take today's daily challenge."""
    _, _, learning, engine, _ = get_services()
    questions = engine.generate_daily_challenge()
    _run_cli_quiz(questions, engine)


@quiz.command("timed")
@click.option("--difficulty", default="all")
@click.option("--count", default=20, type=int)
def quiz_timed(difficulty, count):
    """Take a timed quiz (honor system for timing in CLI)."""
    _, _, learning, engine, _ = get_services()
    questions = engine.generate_timed_quiz(difficulty=difficulty, count=count)
    console.print("[bold yellow]⏱️ Timed mode — pace yourself![/bold yellow]\n")
    _run_cli_quiz(questions, engine)


def _run_cli_quiz(questions, engine):
    if not questions:
        console.print("[yellow]No questions available.[/yellow]")
        return
    answers = []
    for i, q in enumerate(questions):
        console.print(f"\n[bold]Question {i+1}/{len(questions)}[/bold] [{q.difficulty}]")
        console.print(q.question)
        if q.type == "multiple_choice" and q.options:
            for j, opt in enumerate(q.options):
                console.print(f"  {j}) {opt}")
            ans = click.prompt("Your answer (number)", type=int, default=-1)
        elif q.type == "true_false":
            ans = click.prompt("True or False", type=str, default="")
        else:
            ans = click.prompt("Your answer", type=str, default="")
        answers.append(ans)

    result = engine.score(questions, answers)
    console.print(f"\n[bold]Score: {result.score}/{result.total}[/bold]")
    for i, q in enumerate(result.questions):
        mark = "✅" if result.correct_answers[i] else "❌"
        console.print(f"  {mark} Q{i+1}: {q.explanation}")


# ─── Glossary ────────────────────────────────────────────


@cli.group()
def glossary():
    """Look up paleontological terms."""
    pass


@glossary.command("list")
def glossary_list():
    """List all glossary terms."""
    _, _, learning, *_ = get_services()
    terms = learning.get_glossary()
    for tid, t in sorted(terms.items(), key=lambda x: x[1]["term"].lower()):
        console.print(f"  [bold]{t['term']}[/bold] — {t['definition'][:80]}...")


@glossary.command("lookup")
@click.argument("term")
def glossary_lookup(term):
    """Look up a glossary term."""
    _, _, learning, *_ = get_services()
    t = learning.get_glossary_term(term)
    if not t:
        # Try search
        glossary = learning.get_glossary()
        for tid, entry in glossary.items():
            if term.lower() in entry["term"].lower():
                t = entry
                break
    if not t:
        console.print("[red]Term not found.[/red]")
        return
    console.print(f"[bold]{t['term']}[/bold]")
    console.print(t["definition"])


# ─── Dashboard (simple) ─────────────────────────────────


@cli.command()
def dashboard():
    """Show your progress (requires web app for full tracking)."""
    console.print("[yellow]Full dashboard is available via the web UI (python app.py).[/yellow]")
    console.print("CLI progress tracking is limited. Use the web dashboard for full stats.")


if __name__ == "__main__":
    cli()
