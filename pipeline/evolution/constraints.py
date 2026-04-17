from __future__ import annotations


def prohibited_cta_combo(cta_style: str, hook_style: str, structure_family: str) -> bool:
    bad = {
        ("reflective_question", "question_hook", "analysis"),
        ("checklist_cta", "incident_hook", "incident_report"),
    }
    return (cta_style, hook_style, structure_family) in bad


def enforce_hard_constraints(
    *,
    candidate: dict,
    recent_constraints: dict[str, list[str]],
    window: int,
) -> tuple[bool, str]:
    sf = str(candidate.get("format_family", ""))
    hk = str(candidate.get("hook_style", ""))
    cta = str(candidate.get("cta_style", ""))
    arg = str(candidate.get("argument_flow_motif", ""))

    # Composite tokens keep the guarantee strong but feasible at scale.
    structure_token = f"{sf}|{arg}"
    hook_token = f"{hk}|{sf}"

    recent_struct = recent_constraints.get("structure_family", [])[:window]
    recent_hook = recent_constraints.get("hook_style", [])[:window]
    recent_arg = recent_constraints.get("argument_flow_motif", [])[:window]
    recent_cta = recent_constraints.get("cta_style", [])[:window]

    if structure_token and structure_token in recent_struct:
        return False, f"hard_constraint:reused_structure_family:{structure_token}"
    if hook_token and hook_token in recent_hook:
        return False, f"hard_constraint:reused_hook_type:{hook_token}"
    if arg and arg in recent_arg:
        return False, f"hard_constraint:reused_argument_flow:{arg}"

    if prohibited_cta_combo(cta, hk, sf):
        return False, f"hard_constraint:prohibited_cta_combo:{cta}/{hk}/{sf}"

    # prevent local CTA collapse
    if len(recent_cta) >= 2 and all(x == cta for x in recent_cta[:2]):
        return False, f"hard_constraint:cta_three_in_row:{cta}"

    return True, ""
