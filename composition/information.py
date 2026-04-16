from formal.model import Decision, ProofState, Rank, RankContract


def close_information(state: ProofState) -> tuple[Decision, str, dict]:
    relation_candidates = max(len(state.tokens) - 1, 0)
    c_f = 1 if relation_candidates > 0 else 0
    m_f = 1.0 if relation_candidates > 0 else 0.5
    contract = RankContract(F=Rank.INFORMATION, x="relations", C_F=c_f, M_F=m_f, B_F=0, theta_F=1.0)
    decision = contract.decision()
    if decision == Decision.PASS:
        state.information_closed = True
        return Decision.PASS, "Information closed with relation candidates.", {"relation_candidates": relation_candidates}
    return Decision.SUSPEND, "Information suspended: insufficient relation candidates.", {"relation_candidates": relation_candidates}
