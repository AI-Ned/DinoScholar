import json
import os
from dataclasses import dataclass, field


@dataclass
class SpeciesRecord:
    id: str
    scientific_name: str
    common_name: str
    order: str
    suborder: str
    family: str
    genus: str
    period: str
    period_start_mya: float
    period_end_mya: float
    diet: str
    length_m: float
    height_m: float
    weight_kg: float
    locomotion: str
    fossil_locations: list[str] = field(default_factory=list)
    description: str = ""
    fun_facts: list[str] = field(default_factory=list)
    related_species: list[str] = field(default_factory=list)


class EncyclopediaService:
    def __init__(self, data_path: str):
        self._species: dict[str, SpeciesRecord] = {}
        self._load(data_path)

    def _load(self, path: str) -> None:
        filepath = os.path.join(path, "species.json")
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        for entry in raw:
            rec = SpeciesRecord(
                id=entry["id"],
                scientific_name=entry["scientific_name"],
                common_name=entry.get("common_name", ""),
                order=entry.get("classification", {}).get("order", ""),
                suborder=entry.get("classification", {}).get("suborder", ""),
                family=entry.get("classification", {}).get("family", ""),
                genus=entry.get("classification", {}).get("genus", ""),
                period=entry.get("period", {}).get("name", ""),
                period_start_mya=entry.get("period", {}).get("start_mya", 0),
                period_end_mya=entry.get("period", {}).get("end_mya", 0),
                diet=entry.get("diet", ""),
                length_m=entry.get("size", {}).get("length_m", 0),
                height_m=entry.get("size", {}).get("height_m", 0),
                weight_kg=entry.get("size", {}).get("weight_kg", 0),
                locomotion=entry.get("locomotion", ""),
                fossil_locations=entry.get("fossil_locations", []),
                description=entry.get("description", ""),
                fun_facts=entry.get("fun_facts", []),
                related_species=entry.get("related_species", []),
            )
            self._species[rec.id] = rec

    def get(self, species_id: str) -> SpeciesRecord | None:
        return self._species.get(species_id)

    def search(self, query: str) -> list[SpeciesRecord]:
        q = query.lower()
        results = []
        for sp in self._species.values():
            if (
                q in sp.scientific_name.lower()
                or q in sp.common_name.lower()
                or q in sp.description.lower()
                or any(q in fact.lower() for fact in sp.fun_facts)
            ):
                results.append(sp)
        return sorted(results, key=lambda s: s.scientific_name)

    def filter(
        self,
        *,
        period: str | None = None,
        diet: str | None = None,
        min_length: float | None = None,
        max_length: float | None = None,
        location: str | None = None,
    ) -> list[SpeciesRecord]:
        results = list(self._species.values())
        if period:
            p = period.lower()
            results = [s for s in results if p in s.period.lower()]
        if diet:
            d = diet.lower()
            results = [s for s in results if s.diet.lower() == d]
        if min_length is not None:
            results = [s for s in results if s.length_m >= min_length]
        if max_length is not None:
            results = [s for s in results if s.length_m <= max_length]
        if location:
            loc = location.lower()
            results = [
                s
                for s in results
                if any(loc in l.lower() for l in s.fossil_locations)
            ]
        return sorted(results, key=lambda s: s.scientific_name)

    def list_all(self, sort_by: str = "scientific_name") -> list[SpeciesRecord]:
        species = list(self._species.values())
        return sorted(species, key=lambda s: getattr(s, sort_by, s.scientific_name))

    def get_related(self, species_id: str) -> list[SpeciesRecord]:
        sp = self.get(species_id)
        if not sp:
            return []
        return [self._species[rid] for rid in sp.related_species if rid in self._species]

    def get_periods(self) -> list[str]:
        return sorted(set(s.period for s in self._species.values()))

    def get_diets(self) -> list[str]:
        return sorted(set(s.diet for s in self._species.values()))
