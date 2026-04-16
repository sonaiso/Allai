from formal.model import Decision, ProofState, Rank, RankContract


def close_perception(state: ProofState) -> tuple[Decision, str, dict]:
    c_f = 1 if state.tokens else 0
    m_f = 1.0 if state.tokens else 0.0
    contract = RankContract(F=Rank.PERCEPTION, x="tokens", C_F=c_f, M_F=m_f, B_F=0, theta_F=1.0)
    decision = contract.decision()
    if decision == Decision.PASS:
        state.perception_closed = True
        return Decision.PASS, "Perception closed from observable token sequence.", {"token_count": len(state.tokens)}
    return Decision.SUSPEND, "Perception not closed: no observable tokens.", {"token_count": 0}
