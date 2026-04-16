from formal.model import Decision, ProofState

# v1 boundaries: minimal repeatable patterns supported; deeper constructions deferred.
SUPPORTED_WAZN_PATTERNS = {"simple_clause", "idafa_like"}
DEFERRED_WAZN_PATTERNS = {"poetic_inversion", "deep_ellipsis"}
CAUSAL_CONNECTOR = "لأن"


def assign_roles(state: ProofState) -> tuple[Decision, str, dict]:
    if len(state.tokens) < 2:
        return Decision.SUSPEND, "Role distribution suspended: needs at least two tokens.", {"roles": {}}

    if len(state.tokens) > 8:
        return (
            Decision.SUSPEND,
            "Role distribution deferred: pattern outside v1 supported scope.",
            {"deferred_patterns": sorted(DEFERRED_WAZN_PATTERNS)},
        )

    has_causal_connector = CAUSAL_CONNECTOR in state.tokens or CAUSAL_CONNECTOR in (state.normalized_unicode or "")
    state.roles = {
        "fa_iliya": state.tokens[0],
        "maf_uliya": state.tokens[1],
        "sababiya": state.tokens[0] if has_causal_connector else None,
        "musabbabiya": state.tokens[-1] if has_causal_connector else None,
    }
    return (
        Decision.PASS,
        "Roles distributed under v1 role-mizan rules.",
        {
            "roles": state.roles,
            "supported_patterns": sorted(SUPPORTED_WAZN_PATTERNS),
            "deferred_patterns": sorted(DEFERRED_WAZN_PATTERNS),
        },
    )
