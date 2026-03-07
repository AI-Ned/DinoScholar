from dataclasses import dataclass, field


@dataclass
class ComparisonResult:
    species: list
    size_comparison: dict
    shared_traits: list[str] = field(default_factory=list)
    differences: list[dict] = field(default_factory=list)
    evolutionary_note: str = ""


class ComparisonService:
    def __init__(self, encyclopedia_service):
        self._encyclopedia = encyclopedia_service

    def compare(self, species_ids: list[str]) -> ComparisonResult | None:
        species = []
        for sid in species_ids:
            sp = self._encyclopedia.get(sid)
            if sp:
                species.append(sp)
        if len(species) < 2:
            return None

        size_comparison = {}
        for sp in species:
            size_comparison[sp.id] = {
                "name": sp.scientific_name,
                "length_m": sp.length_m,
                "height_m": sp.height_m,
                "weight_kg": sp.weight_kg,
            }

        shared = self._compute_shared_traits(species)
        diffs = self._compute_differences(species)
        evo_note = self._generate_evolutionary_note(species)

        return ComparisonResult(
            species=species,
            size_comparison=size_comparison,
            shared_traits=shared,
            differences=diffs,
            evolutionary_note=evo_note,
        )

    def _compute_shared_traits(self, species: list) -> list[str]:
        shared = []
        # Check common period
        periods = set(sp.period for sp in species)
        if len(periods) == 1:
            shared.append(f"Same period: {periods.pop()}")

        # Check common diet
        diets = set(sp.diet for sp in species)
        if len(diets) == 1:
            shared.append(f"Same diet: {diets.pop()}")

        # Check common locomotion
        locomotions = set(sp.locomotion for sp in species)
        if len(locomotions) == 1:
            shared.append(f"Same locomotion: {locomotions.pop()}")

        # Check common order
        orders = set(sp.order for sp in species)
        if len(orders) == 1:
            shared.append(f"Same order: {orders.pop()}")

        # Check overlapping locations
        all_locations = [set(sp.fossil_locations) for sp in species]
        if all_locations:
            common_locations = all_locations[0]
            for loc_set in all_locations[1:]:
                common_locations &= loc_set
            if common_locations:
                shared.append(f"Shared locations: {', '.join(common_locations)}")

        return shared

    def _compute_differences(self, species: list) -> list[dict]:
        diffs = []
        traits = ["period", "diet", "locomotion", "order", "suborder", "family"]
        for trait in traits:
            values = [getattr(sp, trait) for sp in species]
            if len(set(values)) > 1:
                diff = {"trait": trait.replace("_", " ").title(), "values": {}}
                for sp in species:
                    diff["values"][sp.scientific_name] = getattr(sp, trait)
                diffs.append(diff)
        return diffs

    def _generate_evolutionary_note(self, species: list) -> str:
        orders = set(sp.order for sp in species)
        families = set(sp.family for sp in species)
        names = [sp.scientific_name for sp in species]

        if len(orders) == 1 and len(families) == 1:
            return (
                f"{' and '.join(names)} belong to the same family ({families.pop()}), "
                f"indicating a close evolutionary relationship."
            )
        elif len(orders) == 1:
            return (
                f"{' and '.join(names)} belong to the same order ({orders.pop()}) "
                f"but different families, suggesting a more distant common ancestor."
            )
        else:
            return (
                f"{' and '.join(names)} belong to different orders "
                f"({', '.join(orders)}), indicating they diverged early in dinosaur evolution."
            )
