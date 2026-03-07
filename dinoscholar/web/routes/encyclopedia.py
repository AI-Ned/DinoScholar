from flask import Blueprint, render_template, request, current_app

encyclopedia_bp = Blueprint("encyclopedia", __name__)


@encyclopedia_bp.route("/")
def list_species():
    svc = current_app.config["ENCYCLOPEDIA_SERVICE"]
    query = request.args.get("q", "").strip()
    period = request.args.get("period", "").strip()
    diet = request.args.get("diet", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 25

    if query:
        species = svc.search(query)
    elif period or diet:
        species = svc.filter(
            period=period or None,
            diet=diet or None,
        )
    else:
        species = svc.list_all()

    total = len(species)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    page_species = species[start : start + per_page]

    return render_template(
        "encyclopedia/list.html",
        species=page_species,
        query=query,
        period=period,
        diet=diet,
        page=page,
        total_pages=total_pages,
        total=total,
        periods=svc.get_periods(),
        diets=svc.get_diets(),
    )


@encyclopedia_bp.route("/<species_id>")
def detail(species_id):
    svc = current_app.config["ENCYCLOPEDIA_SERVICE"]
    sp = svc.get(species_id)
    if not sp:
        return "Species not found", 404
    related = svc.get_related(species_id)
    return render_template("encyclopedia/detail.html", species=sp, related=related)


@encyclopedia_bp.route("/compare")
def compare():
    svc = current_app.config["ENCYCLOPEDIA_SERVICE"]
    comparison_svc = current_app.config["COMPARISON_SERVICE"]
    ids = request.args.getlist("species")
    result = None
    if len(ids) >= 2:
        result = comparison_svc.compare(ids[:4])
    all_species = svc.list_all()
    return render_template(
        "encyclopedia/compare.html",
        result=result,
        selected_ids=ids,
        all_species=all_species,
    )
