import json
import os
from dataclasses import dataclass, field


@dataclass
class GeologicalPeriod:
    id: str
    name: str
    era: str
    start_mya: float
    end_mya: float
    climate: str
    key_events: list[str] = field(default_factory=list)
    dominant_species: list[str] = field(default_factory=list)
    description: str = ""


class TimelineService:
    def __init__(self, data_path: str, encyclopedia_service=None):
        self._periods: list[GeologicalPeriod] = []
        self._encyclopedia = encyclopedia_service
        self._load(data_path)

    def _load(self, path: str) -> None:
        filepath = os.path.join(path, "timeline.json")
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        for entry in raw:
            period = GeologicalPeriod(
                id=entry["id"],
                name=entry["name"],
                era=entry.get("era", ""),
                start_mya=entry["start_mya"],
                end_mya=entry["end_mya"],
                climate=entry.get("climate", ""),
                key_events=entry.get("key_events", []),
                dominant_species=entry.get("dominant_species", []),
                description=entry.get("description", ""),
            )
            self._periods.append(period)
        self._periods.sort(key=lambda p: -p.start_mya)

    def get_all_periods(self) -> list[GeologicalPeriod]:
        return list(self._periods)

    def get_period(self, period_id: str) -> GeologicalPeriod | None:
        for p in self._periods:
            if p.id == period_id:
                return p
        return None

    def get_species_in_period(self, period_id: str) -> list:
        period = self.get_period(period_id)
        if not period or not self._encyclopedia:
            return []
        results = []
        for sp in self._encyclopedia.list_all():
            if sp.period_start_mya <= period.start_mya and sp.period_end_mya >= period.end_mya:
                results.append(sp)
            elif (
                sp.period_start_mya < period.start_mya
                and sp.period_end_mya > period.end_mya
            ):
                results.append(sp)
            elif period.end_mya <= sp.period_start_mya <= period.start_mya:
                results.append(sp)
            elif period.end_mya <= sp.period_end_mya <= period.start_mya:
                results.append(sp)
        # Deduplicate
        seen = set()
        unique = []
        for sp in results:
            if sp.id not in seen:
                seen.add(sp.id)
                unique.append(sp)
        return unique

    def get_total_span(self) -> tuple[float, float]:
        if not self._periods:
            return (0, 0)
        return (
            max(p.start_mya for p in self._periods),
            min(p.end_mya for p in self._periods),
        )
