from formal.model import Decision, ProofState, RankContract


def close_concept(state: ProofState) -> tuple[Decision, str, dict]:
    c_f = 1 if state.information_closed else 0
    m_f = 1.0 if state.information_closed else 0.0
    contract = RankContract(F="CONCEPT", x="compositional_concept", C_F=c_f, M_F=m_f, B_F=0, theta_F=1.0)
    decision = contract.decision()
    if decision == Decision.PASS:
        state.concept_closed = True
        return Decision.PASS, "Concept closed as coherent relational structure.", {"concept_closed": True}
    return Decision.SUSPEND, "Concept suspended: informational closure not complete.", {"concept_closed": False}
