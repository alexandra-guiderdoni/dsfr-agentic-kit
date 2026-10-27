"""Contrat d'état commun : observer chaque moteur sans imiter le moteur de parcours AY11."""

import hashlib
import json
from pathlib import Path


def contract_digest(info: dict) -> str:
    return hashlib.sha256(
        json.dumps(info.get("state") or {}, sort_keys=True).encode()
    ).hexdigest()


def native_capture_options(config: dict, info: dict, root: Path) -> list[str]:
    options = ["--profile", config.get("campaign", {}).get("profile", "rgaa-106")]
    if config.get("browser", {}).get("temporal_probes", False):
        options.append("--temporal-probes")
    state = info.get("state")
    if state:
        journey = (root / state["journey"]).resolve()
        if not journey.is_relative_to(root.resolve()) or not journey.is_file():
            raise ValueError("Parcours d'état absent ou hors de la campagne.")
        options += [
            "--journey",
            str(journey),
            "--expect",
            state["expect"],
            "--expect-selector",
            state["expect_selector"],
        ]
    return options


async def require_page_state(
    page, info: dict, root: Path, engine: str, viewport: str
) -> dict:
    """Aucune mesure d'un état demandé sans preuve locale ; aucun parcours rejoué ici."""
    contract = info.get("state")
    observation = {
        "engine": engine,
        "page": info["id"],
        "viewport": viewport,
        "state_contract_sha256": contract_digest(info),
        "dom_sha256": hashlib.sha256((await page.content()).encode()).hexdigest(),
        "status": "not_requested",
        "invariant_verified": False,
        "produces_conformity": False,
    }
    if contract:
        from playwright.async_api import Error as PlaywrightError

        try:
            target = page.locator(contract["expect_selector"])
            count = await target.count()
            visible = count == 1 and await target.is_visible()
            # Comparaison en mémoire uniquement : aucune valeur saisie persistée.
            matches = (
                visible
                and contract["expect"].casefold()
                in (await target.inner_text()).casefold()
            )
        except (PlaywrightError, ValueError) as exc:
            count, visible, matches = None, None, False
            observation["invariant_error_type"] = type(exc).__name__
        observation.update(
            status="unsupported_preparation",
            invariant_observed=bool(matches),
            target_count=count,
            target_visible=bool(visible),
            reason="Le moteur ne prend pas en charge le parcours natif AY11 ; cet état ne peut pas être crédité.",
        )
    destination = root / "observations" / engine / info["id"]
    destination.mkdir(parents=True, exist_ok=True)
    number = len(list(destination.glob(f"{viewport}-*.json"))) + 1
    path = destination / f"{viewport}-{number:03d}.json"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(observation, ensure_ascii=False, indent=2) + "\n")
    if contract:
        await page.context.close()
        raise ValueError(
            "État demandé non pris en charge par ce moteur ; voir le reçu d'observation."
        )
    return observation


def reject_unprepared_reports(config: dict) -> None:
    if any(info.get("state") for info in config.get("sample", [])) and any(
        config.get("phases", {}).get(name, False)
        for name in ("browser_checks", "rgaa_checks", "dsfr_checks")
    ):
        raise ValueError(
            "Comparaison et rapports refusés : les moteurs secondaires ne prennent pas en charge le parcours d'état natif AY11."
        )


def native_state_observation(info: dict, manifest: dict) -> dict:
    trace = manifest.get("journey_trace") if isinstance(manifest, dict) else None
    trace = trace if isinstance(trace, dict) else {}
    target = trace.get("expectation_target") or {}
    verified = (
        bool(info.get("state"))
        and isinstance(trace, dict)
        and isinstance(target, dict)
        and (
            trace.get("expectation_verified") is True
            and trace.get("expectation_mode") == "target_state_observed"
            and target.get("match_count") == 1
            and target.get("visible") is True
        )
    )
    return {
        "engine": "ay11",
        "state_contract_sha256": contract_digest(info),
        "status": "observed"
        if verified
        else ("not_verified" if info.get("state") else "not_requested"),
        "invariant_verified": verified,
        "produces_conformity": False,
    }
