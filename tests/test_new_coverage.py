"""
test_new_coverage.py
====================
Tests targeting previously uncovered code paths:

1. arabic_engine/language/lexicon_layer.py   — 0 % → comprehensive coverage
2. arabic_engine/language/minimal_complete_encoding.py — fill remaining gaps
3. core/trace/chain_validation.py            — fill remaining reachable gaps
"""
from __future__ import annotations

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from arabic_engine.language.lexicon_layer import (
    BUILT_INVENTORY_DEFAULTS,
    EXCEPTION_CLASS_INDEX,
    EXCEPTION_CLASS_REGISTRY,
    BuiltEntry,
    CaseMarkerKind,
    CaseRole,
    Definiteness,
    EntryType,
    ExceptionClass,
    ExceptionClassRecord,
    FinalAnalysisRecord,
    GrammaticalGender,
    GrammaticalNumber,
    InflectedEntry,
    InflectionClass,
    LexiconEntry,
    Operator,
    OperatorResult,
    OperatorType,
    Tense,
    Transitivity,
    _resolve_bina_or_irab,
    _resolve_case_marker_kind,
    _resolve_exception_types,
    apply_lexicon_layer,
)
from arabic_engine.language.minimal_complete_encoding import (
    VALID_SENTENCE_PATTERNS,
    _governance_role,
    _is_lexical_alpha,
    _sentence_pattern,
    apply_minimal_complete_encoding_contract,
)
from core.model import ProofState
from core.trace.chain_validation import _REQUIRED_EVENTS_FOR_JUDGEMENT, validate_trace_chain


# =========================================================
# 1. Tests for arabic_engine/language/lexicon_layer.py
# =========================================================

class LexiconLayerEnumTests(unittest.TestCase):
    """Verify enum values exist and are strings."""

    def test_entry_type_values_are_strings(self) -> None:
        for member in EntryType:
            self.assertIsInstance(member.value, str)

    def test_inflection_class_values(self) -> None:
        self.assertEqual(InflectionClass.MABNI.value, "mabni")
        self.assertEqual(InflectionClass.MURAB_FULL.value, "murab_full")
        self.assertEqual(InflectionClass.MURAB_PARTIAL.value, "murab_partial")

    def test_grammatical_gender_values(self) -> None:
        self.assertEqual(GrammaticalGender.MASCULINE.value, "masculine")
        self.assertEqual(GrammaticalGender.FEMININE.value, "feminine")
        self.assertEqual(GrammaticalGender.COMMON.value, "common")

    def test_grammatical_number_values(self) -> None:
        self.assertEqual(GrammaticalNumber.SINGULAR.value, "singular")
        self.assertEqual(GrammaticalNumber.DUAL.value, "dual")

    def test_case_role_values(self) -> None:
        self.assertEqual(CaseRole.RAF.value, "raf")
        self.assertEqual(CaseRole.NASB.value, "nasb")
        self.assertEqual(CaseRole.JARR.value, "jarr")
        self.assertEqual(CaseRole.BINA.value, "bina")

    def test_tense_values(self) -> None:
        self.assertEqual(Tense.PAST.value, "past")
        self.assertEqual(Tense.PRESENT.value, "present")
        self.assertEqual(Tense.NONE.value, "none")

    def test_transitivity_values(self) -> None:
        self.assertEqual(Transitivity.TRANSITIVE.value, "transitive")
        self.assertEqual(Transitivity.INTRANSITIVE.value, "intransitive")
        self.assertEqual(Transitivity.NONE.value, "none")

    def test_definiteness_values(self) -> None:
        self.assertEqual(Definiteness.DEFINITE.value, "definite")
        self.assertEqual(Definiteness.INDEFINITE.value, "indefinite")
        self.assertEqual(Definiteness.NONE.value, "none")

    def test_operator_type_values(self) -> None:
        self.assertEqual(OperatorType.HARAKA.value, "haraka")
        self.assertEqual(OperatorType.ZAWAID.value, "zawaid")

    def test_exception_class_values(self) -> None:
        self.assertEqual(ExceptionClass.PRONOUN.value, "pronoun")
        self.assertEqual(ExceptionClass.DIPTOTE.value, "diptote")
        self.assertEqual(ExceptionClass.DUAL.value, "dual")
        self.assertEqual(ExceptionClass.FIVE_NOUNS.value, "five_nouns")


class LexiconLayerRegistryTests(unittest.TestCase):
    """Verify exception class registry and index are correctly populated."""

    def test_exception_class_registry_has_twelve_entries(self) -> None:
        self.assertEqual(len(EXCEPTION_CLASS_REGISTRY), 12)

    def test_exception_class_registry_entries_are_records(self) -> None:
        for rec in EXCEPTION_CLASS_REGISTRY:
            self.assertIsInstance(rec, ExceptionClassRecord)
            self.assertIsInstance(rec.code, str)
            self.assertIsInstance(rec.name_ar, str)
            self.assertIsInstance(rec.complexity_score, float)

    def test_exception_class_index_keyed_by_type(self) -> None:
        for exc_type in ExceptionClass:
            self.assertIn(exc_type, EXCEPTION_CLASS_INDEX)
            self.assertIsInstance(EXCEPTION_CLASS_INDEX[exc_type], ExceptionClassRecord)

    def test_exception_class_index_size_matches_registry(self) -> None:
        self.assertEqual(len(EXCEPTION_CLASS_INDEX), len(EXCEPTION_CLASS_REGISTRY))

    def test_built_inventory_defaults_is_non_empty_tuple_of_entries(self) -> None:
        self.assertIsInstance(BUILT_INVENTORY_DEFAULTS, tuple)
        self.assertGreater(len(BUILT_INVENTORY_DEFAULTS), 0)
        for entry in BUILT_INVENTORY_DEFAULTS:
            self.assertIsInstance(entry, LexiconEntry)


class LexiconLayerDataModelTests(unittest.TestCase):
    """Test instantiation of frozen dataclasses."""

    def test_lexicon_entry_instantiation(self) -> None:
        entry = LexiconEntry(
            code="TEST_01",
            arabic_form="في",
            entry_type=EntryType.TOOL,
            inflection_class=InflectionClass.MABNI,
        )
        self.assertEqual(entry.code, "TEST_01")
        self.assertEqual(entry.arabic_form, "في")
        self.assertEqual(entry.gender_default, GrammaticalGender.COMMON)
        self.assertIsNone(entry.notes)

    def test_built_entry_instantiation(self) -> None:
        entry = BuiltEntry(
            entry_code="BE_01",
            sub_type=EntryType.PRONOUN,
            fixed_form="هو",
        )
        self.assertEqual(entry.entry_code, "BE_01")
        self.assertEqual(entry.attachment_type, "free")
        self.assertIsNone(entry.reference_function)

    def test_inflected_entry_instantiation(self) -> None:
        entry = InflectedEntry(
            entry_code="IE_01",
            bare_form="كتب",
            root_code="ك-ت-ب",
            radical_count=3,
        )
        self.assertEqual(entry.entry_code, "IE_01")
        self.assertEqual(entry.gender_default, GrammaticalGender.MASCULINE)
        self.assertTrue(entry.accepts_tanween)

    def test_operator_instantiation(self) -> None:
        op = Operator(
            code="OP_01",
            name_ar="ضمة",
            operator_type=OperatorType.HARAKA,
            applies_to=(EntryType.DERIVED_NOUN,),
            generates=("surface_form_with_damma",),
        )
        self.assertEqual(op.code, "OP_01")
        self.assertEqual(op.priority, 10)

    def test_operator_result_instantiation(self) -> None:
        result = OperatorResult(
            entry_code="TEST",
            operator_code="OP",
            definiteness=Definiteness.INDEFINITE,
            gender=GrammaticalGender.MASCULINE,
            number=GrammaticalNumber.SINGULAR,
            case_role=CaseRole.RAF,
            case_marker_kind=CaseMarkerKind.HARAKA,
            tense=Tense.NONE,
            transitivity=Transitivity.NONE,
            surface_form="كتاب",
        )
        self.assertEqual(result.confidence, 1.0)

    def test_final_analysis_record_instantiation(self) -> None:
        record = FinalAnalysisRecord(
            entry_code="FA_01",
            entry_type=EntryType.DERIVED_NOUN,
            final_surface_form="كتاب",
            case_marker_kind=CaseMarkerKind.HARAKA,
            bina_or_irab="irab",
            definiteness=Definiteness.INDEFINITE,
            gender=GrammaticalGender.MASCULINE,
            number=GrammaticalNumber.SINGULAR,
            case_role=CaseRole.RAF,
            tense=Tense.NONE,
            transitivity=Transitivity.NONE,
        )
        self.assertEqual(record.confidence, 1.0)
        self.assertEqual(record.exception_types, ())
        self.assertIsNone(record.pause_form)


class ResolveExceptionTypesTests(unittest.TestCase):
    """Tests for _resolve_exception_types."""

    def _make_entry(
        self,
        entry_type: EntryType = EntryType.TOOL,
        inflection_class: InflectionClass = InflectionClass.MABNI,
        code: str = "TEST",
        arabic_form: str = "في",
    ) -> LexiconEntry:
        return LexiconEntry(
            code=code,
            arabic_form=arabic_form,
            entry_type=entry_type,
            inflection_class=inflection_class,
        )

    def test_pronoun_entry_infers_pronoun_exception(self) -> None:
        entry = self._make_entry(entry_type=EntryType.PRONOUN)
        result = _resolve_exception_types(entry, {})
        self.assertIn(ExceptionClass.PRONOUN, result)

    def test_demonstrative_entry_infers_demonstrative_relative(self) -> None:
        entry = self._make_entry(entry_type=EntryType.DEMONSTRATIVE)
        result = _resolve_exception_types(entry, {})
        self.assertIn(ExceptionClass.DEMONSTRATIVE_RELATIVE, result)

    def test_relative_entry_infers_demonstrative_relative(self) -> None:
        entry = self._make_entry(entry_type=EntryType.RELATIVE)
        result = _resolve_exception_types(entry, {})
        self.assertIn(ExceptionClass.DEMONSTRATIVE_RELATIVE, result)

    def test_conditional_entry_infers_demonstrative_relative(self) -> None:
        entry = self._make_entry(entry_type=EntryType.CONDITIONAL)
        result = _resolve_exception_types(entry, {})
        self.assertIn(ExceptionClass.DEMONSTRATIVE_RELATIVE, result)

    def test_interrogative_entry_infers_demonstrative_relative(self) -> None:
        entry = self._make_entry(entry_type=EntryType.INTERROGATIVE)
        result = _resolve_exception_types(entry, {})
        self.assertIn(ExceptionClass.DEMONSTRATIVE_RELATIVE, result)

    def test_murab_partial_infers_diptote(self) -> None:
        entry = self._make_entry(
            entry_type=EntryType.DERIVED_NOUN,
            inflection_class=InflectionClass.MURAB_PARTIAL,
        )
        result = _resolve_exception_types(entry, {})
        self.assertIn(ExceptionClass.DIPTOTE, result)

    def test_explicit_exception_map_is_used(self) -> None:
        entry = self._make_entry(entry_type=EntryType.DERIVED_NOUN)
        exception_map = {"TEST": (ExceptionClass.FIVE_NOUNS,)}
        result = _resolve_exception_types(entry, exception_map)
        self.assertIn(ExceptionClass.FIVE_NOUNS, result)

    def test_no_duplicate_exception_types_for_pronoun_with_map(self) -> None:
        entry = self._make_entry(entry_type=EntryType.PRONOUN)
        exception_map = {"TEST": (ExceptionClass.PRONOUN,)}
        result = _resolve_exception_types(entry, exception_map)
        self.assertEqual(result.count(ExceptionClass.PRONOUN), 1)

    def test_no_duplicate_demonstrative_relative_with_map(self) -> None:
        entry = self._make_entry(entry_type=EntryType.DEMONSTRATIVE)
        exception_map = {"TEST": (ExceptionClass.DEMONSTRATIVE_RELATIVE,)}
        result = _resolve_exception_types(entry, exception_map)
        self.assertEqual(result.count(ExceptionClass.DEMONSTRATIVE_RELATIVE), 1)

    def test_no_duplicate_diptote_with_map(self) -> None:
        entry = self._make_entry(
            entry_type=EntryType.DERIVED_NOUN,
            inflection_class=InflectionClass.MURAB_PARTIAL,
        )
        exception_map = {"TEST": (ExceptionClass.DIPTOTE,)}
        result = _resolve_exception_types(entry, exception_map)
        self.assertEqual(result.count(ExceptionClass.DIPTOTE), 1)

    def test_tool_entry_with_no_map_has_no_exceptions(self) -> None:
        entry = self._make_entry(entry_type=EntryType.TOOL, inflection_class=InflectionClass.MABNI)
        result = _resolve_exception_types(entry, {})
        self.assertEqual(result, ())


class ResolveCaseMarkerKindTests(unittest.TestCase):
    """Tests for _resolve_case_marker_kind."""

    def test_five_nouns_raf_returns_letter_waw(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.RAF, GrammaticalNumber.SINGULAR, (ExceptionClass.FIVE_NOUNS,))
        self.assertEqual(result, CaseMarkerKind.LETTER_WAW)

    def test_five_nouns_nasb_returns_letter_alif(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.NASB, GrammaticalNumber.SINGULAR, (ExceptionClass.FIVE_NOUNS,))
        self.assertEqual(result, CaseMarkerKind.LETTER_ALIF)

    def test_five_nouns_jarr_returns_letter_ya(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.JARR, GrammaticalNumber.SINGULAR, (ExceptionClass.FIVE_NOUNS,))
        self.assertEqual(result, CaseMarkerKind.LETTER_YA)

    def test_dual_number_raf_returns_letter_alif(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.RAF, GrammaticalNumber.DUAL, ())
        self.assertEqual(result, CaseMarkerKind.LETTER_ALIF)

    def test_dual_number_nasb_returns_letter_ya(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.NASB, GrammaticalNumber.DUAL, ())
        self.assertEqual(result, CaseMarkerKind.LETTER_YA)

    def test_dual_number_jarr_returns_letter_ya(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.JARR, GrammaticalNumber.DUAL, ())
        self.assertEqual(result, CaseMarkerKind.LETTER_YA)

    def test_dual_exception_class_raf_returns_letter_alif(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.RAF, GrammaticalNumber.SINGULAR, (ExceptionClass.DUAL,))
        self.assertEqual(result, CaseMarkerKind.LETTER_ALIF)

    def test_sound_masc_plural_raf_returns_letter_waw(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.RAF, GrammaticalNumber.SOUND_MASC_PLURAL, ())
        self.assertEqual(result, CaseMarkerKind.LETTER_WAW)

    def test_sound_masc_plural_nasb_returns_letter_ya(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.NASB, GrammaticalNumber.SOUND_MASC_PLURAL, ())
        self.assertEqual(result, CaseMarkerKind.LETTER_YA)

    def test_sound_masc_plural_exception_class_raf_returns_letter_waw(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.RAF, GrammaticalNumber.SINGULAR, (ExceptionClass.SOUND_MASC_PLURAL,))
        self.assertEqual(result, CaseMarkerKind.LETTER_WAW)

    def test_five_verbs_raf_returns_nun_thabut(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.RAF, GrammaticalNumber.SINGULAR, (ExceptionClass.FIVE_VERBS,))
        self.assertEqual(result, CaseMarkerKind.LETTER_NUN_THABUT)

    def test_five_verbs_nasb_returns_nun_hadhf(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.NASB, GrammaticalNumber.SINGULAR, (ExceptionClass.FIVE_VERBS,))
        self.assertEqual(result, CaseMarkerKind.LETTER_NUN_HADHF)

    def test_five_verbs_jazm_returns_nun_hadhf(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.JAZM, GrammaticalNumber.SINGULAR, (ExceptionClass.FIVE_VERBS,))
        self.assertEqual(result, CaseMarkerKind.LETTER_NUN_HADHF)

    def test_bina_case_returns_none(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.BINA, GrammaticalNumber.SINGULAR, ())
        self.assertEqual(result, CaseMarkerKind.NONE)

    def test_default_singular_raf_returns_haraka(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.RAF, GrammaticalNumber.SINGULAR, ())
        self.assertEqual(result, CaseMarkerKind.HARAKA)

    def test_default_singular_nasb_returns_haraka(self) -> None:
        result = _resolve_case_marker_kind(CaseRole.NASB, GrammaticalNumber.SINGULAR, ())
        self.assertEqual(result, CaseMarkerKind.HARAKA)


class ResolveBinaOrIrabTests(unittest.TestCase):
    """Tests for _resolve_bina_or_irab."""

    def test_mabni_returns_bina(self) -> None:
        self.assertEqual(_resolve_bina_or_irab(InflectionClass.MABNI), "bina")

    def test_murab_full_returns_irab(self) -> None:
        self.assertEqual(_resolve_bina_or_irab(InflectionClass.MURAB_FULL), "irab")

    def test_murab_partial_returns_irab(self) -> None:
        self.assertEqual(_resolve_bina_or_irab(InflectionClass.MURAB_PARTIAL), "irab")


class ApplyLexiconLayerTests(unittest.TestCase):
    """Integration tests for apply_lexicon_layer."""

    def test_apply_with_empty_entries_produces_empty_result(self) -> None:
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, ())
        self.assertIn("lexicon_layer", state.conceptual_state)
        self.assertEqual(state.conceptual_state["lexicon_layer"]["entry_count"], 0)
        self.assertEqual(state.conceptual_state["lexicon_layer"]["entries"], [])

    def test_apply_with_empty_entries_still_includes_exception_registry(self) -> None:
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, ())
        registry = state.conceptual_state["lexicon_layer"]["exception_registry"]
        self.assertEqual(len(registry), len(EXCEPTION_CLASS_REGISTRY))

    def test_apply_with_built_inventory_defaults_populates_entries(self) -> None:
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, BUILT_INVENTORY_DEFAULTS)
        layer = state.conceptual_state["lexicon_layer"]
        self.assertEqual(layer["entry_count"], len(BUILT_INVENTORY_DEFAULTS))
        self.assertEqual(len(layer["entries"]), len(BUILT_INVENTORY_DEFAULTS))

    def test_apply_adds_trace_event(self) -> None:
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, BUILT_INVENTORY_DEFAULTS)
        trace_events = [e["event"] for e in state.trace_chain]
        self.assertIn("lexicon_layer", trace_events)

    def test_apply_trace_payload_has_counts(self) -> None:
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, BUILT_INVENTORY_DEFAULTS)
        trace = next(e for e in state.trace_chain if e["event"] == "lexicon_layer")
        self.assertEqual(trace["payload"]["entry_count"], len(BUILT_INVENTORY_DEFAULTS))
        self.assertEqual(trace["payload"]["exception_class_count"], len(EXCEPTION_CLASS_REGISTRY))

    def test_apply_mabni_entry_has_bina(self) -> None:
        entry = LexiconEntry("T1", "في", EntryType.TOOL, InflectionClass.MABNI)
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, (entry,))
        result = state.conceptual_state["lexicon_layer"]["entries"][0]
        self.assertEqual(result["bina_or_irab"], "bina")
        self.assertEqual(result["case_role"], "bina")
        self.assertEqual(result["definiteness"], "none")

    def test_apply_murab_full_entry_has_irab_and_raf(self) -> None:
        entry = LexiconEntry("T2", "كتاب", EntryType.DERIVED_NOUN, InflectionClass.MURAB_FULL)
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, (entry,))
        result = state.conceptual_state["lexicon_layer"]["entries"][0]
        self.assertEqual(result["bina_or_irab"], "irab")
        self.assertEqual(result["case_role"], "raf")
        self.assertEqual(result["definiteness"], "indefinite")

    def test_apply_pronoun_entry_has_pronoun_exception(self) -> None:
        entry = LexiconEntry("P1", "هو", EntryType.PRONOUN, InflectionClass.MABNI, GrammaticalGender.MASCULINE)
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, (entry,))
        result = state.conceptual_state["lexicon_layer"]["entries"][0]
        self.assertIn("pronoun", result["exception_types"])

    def test_apply_demonstrative_entry_has_demonstrative_relative_exception(self) -> None:
        entry = LexiconEntry("D1", "هذا", EntryType.DEMONSTRATIVE, InflectionClass.MABNI, GrammaticalGender.MASCULINE)
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, (entry,))
        result = state.conceptual_state["lexicon_layer"]["entries"][0]
        self.assertIn("demonstrative_relative", result["exception_types"])

    def test_apply_murab_partial_entry_has_diptote_exception(self) -> None:
        entry = LexiconEntry("DP1", "أحمد", EntryType.DERIVED_NOUN, InflectionClass.MURAB_PARTIAL)
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, (entry,))
        result = state.conceptual_state["lexicon_layer"]["entries"][0]
        self.assertIn("diptote", result["exception_types"])

    def test_apply_with_exception_map_uses_provided_exceptions(self) -> None:
        entry = LexiconEntry("FN1", "أب", EntryType.DERIVED_NOUN, InflectionClass.MURAB_FULL)
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, (entry,), exception_map={"FN1": (ExceptionClass.FIVE_NOUNS,)})
        result = state.conceptual_state["lexicon_layer"]["entries"][0]
        self.assertIn("five_nouns", result["exception_types"])
        # five_nouns at RAF → letter_waw
        self.assertEqual(result["case_marker_kind"], "letter_waw")

    def test_apply_without_exception_map_defaults_to_empty(self) -> None:
        entry = LexiconEntry("T3", "من", EntryType.TOOL, InflectionClass.MABNI)
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, (entry,))
        result = state.conceptual_state["lexicon_layer"]["entries"][0]
        self.assertEqual(result["exception_types"], [])

    def test_entry_analysis_trace_contains_source(self) -> None:
        entry = LexiconEntry("T4", "على", EntryType.TOOL, InflectionClass.MABNI)
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, (entry,))
        trace = state.conceptual_state["lexicon_layer"]["entries"][0]["analysis_trace"]
        self.assertEqual(trace["source"], "lexicon_layer_v1")

    def test_exception_registry_entries_have_required_keys(self) -> None:
        state = ProofState(ingress_text="test")
        apply_lexicon_layer(state, ())
        registry = state.conceptual_state["lexicon_layer"]["exception_registry"]
        required_keys = {"code", "name_ar", "exception_type", "behavior_desc", "rule_tag", "complexity_score"}
        for rec in registry:
            self.assertTrue(required_keys.issubset(rec.keys()))

    def test_apply_returns_state(self) -> None:
        state = ProofState(ingress_text="test")
        returned = apply_lexicon_layer(state, ())
        self.assertIs(returned, state)


# =========================================================
# 2. Fill remaining gaps in minimal_complete_encoding.py
# =========================================================

class MinimalCompleteEncodingHelperTests(unittest.TestCase):
    """Direct tests for private helpers to cover missing branches."""

    def test_is_lexical_alpha_empty_string_returns_false(self) -> None:
        # covers line 15: `return False` when `not token`
        self.assertFalse(_is_lexical_alpha(""))

    def test_is_lexical_alpha_pure_letter_returns_true(self) -> None:
        self.assertTrue(_is_lexical_alpha("كتب"))

    def test_is_lexical_alpha_letter_with_diacritic_returns_true(self) -> None:
        # covers line 23: `continue` for category "M" (Arabic diacritic fatha U+064E)
        self.assertTrue(_is_lexical_alpha("كَ"))

    def test_is_lexical_alpha_digit_returns_false(self) -> None:
        # non-letter non-mark → early return False (line 24)
        self.assertFalse(_is_lexical_alpha("1"))

    def test_is_lexical_alpha_symbol_returns_false(self) -> None:
        self.assertFalse(_is_lexical_alpha("!"))

    def test_sentence_pattern_empty_tokens_returns_empty(self) -> None:
        # covers line 30: `return "empty"`
        self.assertEqual(_sentence_pattern([]), "empty")

    def test_sentence_pattern_verbal_prefix_ya_returns_verbal(self) -> None:
        # covers line 34: `return "verbal"` when first char in PRESENT_TENSE_VERB_PREFIXES
        self.assertEqual(_sentence_pattern(["يكتب", "الطالب"]), "verbal")

    def test_sentence_pattern_verbal_prefix_ta_returns_verbal(self) -> None:
        self.assertEqual(_sentence_pattern(["تكتب"]), "verbal")

    def test_sentence_pattern_preposition_returns_prepositional(self) -> None:
        # covers line 36: `return "prepositional"` when first token in _PREPOSITIONS
        self.assertEqual(_sentence_pattern(["في", "البيت"]), "prepositional")
        self.assertEqual(_sentence_pattern(["من", "هنا"]), "prepositional")

    def test_sentence_pattern_nominal_returns_nominal(self) -> None:
        self.assertEqual(_sentence_pattern(["الطالب", "مجتهد"]), "nominal")

    def test_governance_role_verbal_at_index_zero(self) -> None:
        # covers line 43: `return "governor:verb"`
        self.assertEqual(_governance_role("verbal", 0), "governor:verb")

    def test_governance_role_prepositional_at_index_zero(self) -> None:
        # covers line 45: `return "governor:preposition"`
        self.assertEqual(_governance_role("prepositional", 0), "governor:preposition")

    def test_governance_role_nominal_at_index_zero(self) -> None:
        self.assertEqual(_governance_role("nominal", 0), "governor:nominal_anchor")

    def test_governance_role_non_zero_index_returns_dependent(self) -> None:
        self.assertEqual(_governance_role("verbal", 1), "dependent")
        self.assertEqual(_governance_role("nominal", 2), "dependent")


class MinimalCompleteEncodingContractTests(unittest.TestCase):
    """Integration tests via apply_minimal_complete_encoding_contract."""

    def test_verbal_sentence_pattern_and_governance_roles(self) -> None:
        # First token starts with ي → verbal pattern, governor:verb at index 0
        state = ProofState(ingress_text="يكتب الطالب الدرس")
        apply_minimal_complete_encoding_contract(state)
        enc = state.symbolic_state["minimal_complete_encoding"]
        self.assertEqual(enc["sentence_pattern"], "verbal")
        self.assertEqual(enc["token_units"][0]["governance_role"], "governor:verb")
        self.assertEqual(enc["token_units"][1]["governance_role"], "dependent")

    def test_prepositional_sentence_pattern_and_governance_roles(self) -> None:
        # First token is "في" → prepositional pattern, governor:preposition at index 0
        state = ProofState(ingress_text="في البيت نور")
        apply_minimal_complete_encoding_contract(state)
        enc = state.symbolic_state["minimal_complete_encoding"]
        self.assertEqual(enc["sentence_pattern"], "prepositional")
        self.assertEqual(enc["token_units"][0]["governance_role"], "governor:preposition")
        self.assertEqual(enc["token_units"][1]["governance_role"], "dependent")

    def test_empty_text_produces_empty_sentence_pattern(self) -> None:
        # Empty normalized text → tokens=[] → "empty" pattern
        state = ProofState(ingress_text="   ", normalized_text="   ")
        apply_minimal_complete_encoding_contract(state)
        enc = state.symbolic_state["minimal_complete_encoding"]
        self.assertEqual(enc["sentence_pattern"], "empty")
        self.assertEqual(enc["token_count"], 0)
        self.assertFalse(enc["completeness"]["complete"])

    def test_mixed_token_classified_as_mixed_or_symbolic(self) -> None:
        # "1كتب" has a digit followed by letters → not purely lexical alpha
        state = ProofState(ingress_text="1كتب الطالب")
        apply_minimal_complete_encoding_contract(state)
        enc = state.symbolic_state["minimal_complete_encoding"]
        self.assertEqual(enc["token_units"][0]["lexical_axis"]["kind"], "mixed_or_symbolic")

    def test_pure_alpha_token_classified_correctly(self) -> None:
        state = ProofState(ingress_text="الطالب مجتهد")
        apply_minimal_complete_encoding_contract(state)
        enc = state.symbolic_state["minimal_complete_encoding"]
        self.assertEqual(enc["token_units"][0]["lexical_axis"]["kind"], "alpha")

    def test_valid_sentence_patterns_constant(self) -> None:
        self.assertIn("empty", VALID_SENTENCE_PATTERNS)
        self.assertIn("nominal", VALID_SENTENCE_PATTERNS)
        self.assertIn("verbal", VALID_SENTENCE_PATTERNS)
        self.assertIn("prepositional", VALID_SENTENCE_PATTERNS)


# =========================================================
# 3. Fill remaining reachable gaps in chain_validation.py
# =========================================================

class ChainValidationAdditionalTests(unittest.TestCase):
    """Tests for uncovered reachable branches in validate_trace_chain."""

    def _build_trace(self, events: list[str]) -> list[dict]:
        return [
            {"event_id": idx, "event": event, "payload": {}, "timestamp": "2026-01-01T00:00:00+00:00"}
            for idx, event in enumerate(events, start=1)
        ]

    def test_rejects_when_minimal_encoding_contract_missing(self) -> None:
        # All required events present (including composition_applied) but
        # minimal_complete_encoding_contract is absent → line 57
        events = list(_REQUIRED_EVENTS_FOR_JUDGEMENT)
        state = ProofState(ingress_text="x")
        state.trace_chain = self._build_trace(events)
        result = validate_trace_chain(state)
        self.assertFalse(result)
        last = state.trace_chain[-1]
        self.assertEqual(last["event"], "trace_chain_rejected")
        self.assertIn("minimal_complete_encoding_contract", last["payload"]["reason"])

    def test_rejects_when_minimal_encoding_comes_after_composition(self) -> None:
        # All required events in order + minimal_complete_encoding_contract placed AFTER
        # composition_applied → line 61
        events = list(_REQUIRED_EVENTS_FOR_JUDGEMENT) + ["minimal_complete_encoding_contract"]
        state = ProofState(ingress_text="x")
        state.trace_chain = self._build_trace(events)
        result = validate_trace_chain(state)
        self.assertFalse(result)
        last = state.trace_chain[-1]
        self.assertEqual(last["event"], "trace_chain_rejected")
        self.assertEqual(last["payload"]["reason"], "minimal_encoding_event_after_composition")

    def test_validates_successfully_when_minimal_encoding_before_composition(self) -> None:
        # Insert minimal_complete_encoding_contract immediately before composition_applied
        events = list(_REQUIRED_EVENTS_FOR_JUDGEMENT)
        composition_idx = events.index("composition_applied")
        events.insert(composition_idx, "minimal_complete_encoding_contract")
        state = ProofState(ingress_text="x")
        state.trace_chain = self._build_trace(events)
        result = validate_trace_chain(state)
        self.assertTrue(result)
        last_event = state.trace_chain[-1]["event"]
        self.assertEqual(last_event, "trace_chain_validated")

    def test_pre_language_trace_validation_recorded_in_conceptual_state(self) -> None:
        # A valid trace chain should record pre_language trace validation
        events = list(_REQUIRED_EVENTS_FOR_JUDGEMENT)
        composition_idx = events.index("composition_applied")
        events.insert(composition_idx, "minimal_complete_encoding_contract")
        state = ProofState(ingress_text="x")
        state.trace_chain = self._build_trace(events)
        validate_trace_chain(state)
        self.assertIn("pre_language", state.conceptual_state)
        self.assertIn("trace_validation", state.conceptual_state["pre_language"])


if __name__ == "__main__":
    unittest.main()
