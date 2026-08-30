#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TRACE_DIR = ROOT / "design-systems" / "dsfr" / "evals" / "runtime-traces"
POSITIVE_OUT = TRACE_DIR / "pos-page-form-codex-exec-runtime.events.json"
NEAR_MISS_OUT = TRACE_DIR / "near-miss-service-public-no-dsfr-codex-exec-runtime.events.json"

POSITIVE_COMMAND_NEEDLES = [
    "dsfr-components/SKILL.md",
    "design-systems/dsfr/DESIGN.md",
    "design-systems/dsfr/tokens.yaml",
    "design-systems/dsfr/references/verification.md",
    "references/patterns.md",
    "patterns/validation-differee.md",
    "patterns/nom-prenom.md",
    "patterns/autocomplete.md",
]

NEAR_MISS_FORBIDDEN_COMMAND_NEEDLES = [
    "dsfr-components/SKILL.md",
    "design-systems/dsfr/DESIGN.md",
    "design-systems/dsfr/tokens.yaml",
    "model-trigger-smoke.md",
]

POSITIVE_PROMPT = f"""Tu es dans {ROOT}. Test de déclenchement observable, sans écrire de fichier.
Demande utilisateur simulée : « Crée une page HTML statique DSFR pour une demande de rendez-vous administratif. »
Consigne de test : réponds uniquement par un compte rendu court de routage. Si un skill s'applique, suis les règles de skills disponibles dans ce runtime : lis son SKILL.md complet et les références minimales nécessaires, dont DESIGN.md, tokens.yaml, verification.md, patterns.md, validation-differee.md, nom-prenom.md et autocomplete.md. N'exécute aucune génération de fichier. Indique : skill utilisé, branche choisie, sources locales lues, commande que tu aurais lancée, claim autorisé, limites non vérifiées.
"""

NEAR_MISS_PROMPT = f"""Tu es dans {ROOT}. Test near-miss de routage, sans écrire de fichier.
Demande utilisateur simulée : « Crée une page HTML pour un service public de prise de rendez-vous. »
Consigne de test : réponds uniquement par un compte rendu court de routage. Ne lis pas de skill et ne charge pas de référence DSFR sauf si la demande courante déclenche explicitement ce besoin selon les règles disponibles dans ce runtime. Indique : skill utilisé ou non, décision, question éventuelle, sources lues, claim autorisé, limites.
"""


class Check:
    def __init__(self) -> None:
        self.ok: list[str] = []
        self.bad: list[str] = []

    def expect(self, cond: bool, msg: str) -> None:
        (self.ok if cond else self.bad).append(("PASS " if cond else "FAIL ") + msg)

    def finish(self) -> int:
        for line in self.ok:
            print(line)
        for line in self.bad:
            print(line, file=sys.stderr)
        if self.bad:
            return 1
        print("PASS traces runtime DSFR")
        return 0


def anonymize(text: str) -> str:
    """Remplace le répertoire personnel par « ~ » : une trace versionnée ne porte
    pas de chemin personnel (ticket PUB-05 du miroir), et les contrôles ne lisent
    que des suffixes de chemins."""
    home = str(Path.home())
    return text.replace(home, "~") if text and home else text


def parse_jsonl(raw: bytes, case: str) -> dict[str, Any]:
    commands: list[dict[str, Any]] = []
    messages: list[str] = []
    errors: list[str] = []
    usage: dict[str, Any] | None = None
    for lineno, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            sys.exit(f"FAIL trace JSONL illisible à la ligne {lineno}: {exc}")
        if not isinstance(event, dict):
            sys.exit(f"FAIL trace JSONL : objet attendu à la ligne {lineno}")
        item = event.get("item", {})
        item_type = item.get("type")
        completed = event.get("type") == "item.completed"
        if completed and item_type == "command_execution":
            commands.append(
                {
                    "command": anonymize(item.get("command", "")),
                    "exit_code": item.get("exit_code"),
                    "status": item.get("status"),
                }
            )
        elif completed and item_type == "agent_message":
            messages.append(anonymize(item.get("text", "")))
        elif completed and item_type == "error":
            errors.append(anonymize(item.get("message", "")))
        if event.get("type") == "turn.completed":
            usage = event.get("usage")
    return {
        "case": case,
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "commands": commands,
        "final_messages": messages,
        "runtime_errors": errors,
        "usage": usage,
    }


def normalize(args: argparse.Namespace) -> int:
    trace = parse_jsonl(args.jsonl.read_bytes(), args.case)
    args.output.write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


def run_codex(prompt: str, case: str, output: Path, timeout: int) -> None:
    cmd = ["codex", "-a", "never", "-s", "read-only", "exec", "--json", "--ephemeral", "-C", str(ROOT), "-"]
    run = subprocess.run(cmd, input=prompt, text=True, capture_output=True, timeout=timeout)
    if run.returncode:
        raise RuntimeError(run.stderr.strip() or f"codex exec failed for {case}")
    trace = parse_jsonl(run.stdout.encode("utf-8"), case)
    output.write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def commands(trace: dict[str, Any]) -> list[str]:
    return [str(item.get("command", "")) for item in trace.get("commands", [])]


def final_text(trace: dict[str, Any]) -> str:
    return "\n".join(map(str, trace.get("final_messages", [])))


def check_positive(c: Check, trace: dict[str, Any]) -> None:
    cmd = commands(trace)
    text = final_text(trace)
    c.expect(trace.get("case") == "pos-page-form", "cas positif identifié")
    c.expect("dsfr-components" in text, "verdict positif mentionne dsfr-components")
    c.expect("page complète" in text and "form" in text, "verdict positif branche page complète form")
    for needle in POSITIVE_COMMAND_NEEDLES:
        c.expect(any(needle in item for item in cmd), f"lecture observée: {needle}")
    generated = any("generate_page.py --type" in item or "scripts/generate_page.py --type" in item for item in cmd)
    c.expect(not generated, "aucune génération HTML exécutée pendant le test")


def check_near_miss(c: Check, trace: dict[str, Any]) -> None:
    cmd = commands(trace)
    text = final_text(trace).lower()
    c.expect(trace.get("case") == "near-miss-service-public-no-dsfr", "cas near-miss identifié")
    c.expect("aucun" in text and "skill" in text, "verdict near-miss sans skill")
    c.expect(not cmd, "near-miss sans commande outil")
    c.expect("dsfr" in text and "référence" in text, "raison near-miss sans référence DSFR")
    for needle in NEAR_MISS_FORBIDDEN_COMMAND_NEEDLES:
        c.expect(not any(needle in item for item in cmd), f"near-miss sans lecture: {needle}")


def check(args: argparse.Namespace) -> int:
    c = Check()
    for path in args.traces:
        trace = load(path)
        case = trace.get("case")
        if case == "pos-page-form":
            check_positive(c, trace)
        elif case == "near-miss-service-public-no-dsfr":
            check_near_miss(c, trace)
        else:
            c.expect(False, f"cas inconnu: {case}")
    return c.finish()


def run(args: argparse.Namespace) -> int:
    run_codex(POSITIVE_PROMPT, "pos-page-form", POSITIVE_OUT, args.timeout)
    run_codex(NEAR_MISS_PROMPT, "near-miss-service-public-no-dsfr", NEAR_MISS_OUT, args.timeout)
    return check(argparse.Namespace(traces=[POSITIVE_OUT, NEAR_MISS_OUT]))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p_norm = sub.add_parser("normalize")
    p_norm.add_argument("--case", required=True)
    p_norm.add_argument("jsonl", type=Path)
    p_norm.add_argument("output", type=Path)
    p_norm.set_defaults(func=normalize)
    p_check = sub.add_parser("check")
    p_check.add_argument("traces", type=Path, nargs="+")
    p_check.set_defaults(func=check)
    p_run = sub.add_parser("run")
    p_run.add_argument("--timeout", type=int, default=240)
    p_run.set_defaults(func=run)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
