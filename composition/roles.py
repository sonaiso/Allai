from formal.model import Decision, ProofState

# v1 boundaries: minimal repeatable patterns supported; deeper constructions deferred.
SUPPORTED_WAZN_PATTERNS = {"simple_clause", "idafa_like"}
DEFERRED_WAZN_PATTERNS = {"poetic_inversion", "deep_ellipsis"}


def assign_roles(state: ProofState) -> tuple[Decision, str, dict]:
    if len(state.tokens) < 2:
        return Decision.SUSPEND, "Role distribution suspended: needs at least two tokens.", {"roles": {}}

    if len(state.tokens) > 8:
        return (
            Decision.SUSPEND,
            "Role distribution deferred: pattern outside v1 supported scope.",
            {"deferred_patterns": sorted(DEFERRED_WAZN_PATTERNS)},
        )

    state.roles = {
        "fa_iliya": state.tokens[0],
        "maf_uliya": state.tokens[1],
        "sababiya": state.tokens[0] if "لأن" in state.tokens else None,
        "musabbabiya": state.tokens[-1] if "لأن" in state.tokens else None,
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
