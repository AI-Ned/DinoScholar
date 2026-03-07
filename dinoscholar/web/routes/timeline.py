from flask import Blueprint, render_template, request, current_app

timeline_bp = Blueprint("timeline", __name__)


@timeline_bp.route("/")
def index():
    svc = current_app.config["TIMELINE_SERVICE"]
    periods = svc.get_all_periods()
    total_span = svc.get_total_span()
    return render_template(
        "timeline/index.html",
        periods=periods,
        total_span=total_span,
    )


@timeline_bp.route("/<period_id>")
def period_detail(period_id):
    svc = current_app.config["TIMELINE_SERVICE"]
    enc_svc = current_app.config["ENCYCLOPEDIA_SERVICE"]
    period = svc.get_period(period_id)
    if not period:
        return "Period not found", 404
    species_in_period = svc.get_species_in_period(period_id)
    return render_template(
        "timeline/period_detail.html",
        period=period,
        species=species_in_period,
    )
