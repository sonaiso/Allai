from __future__ import annotations

import pathlib
from typing import Any, Dict

import yaml

from core.model import ProofState

_ADAM_PROPERTIES_PATH = (
    pathlib.Path(__file__).resolve().parents[3] / "specs" / "adam_properties.yaml"
)


def _load_adam_properties() -> Dict[str, Any]:
    """حمّل ملف الخواص الأولى. أعد قاموسًا فارغًا عند الفشل."""
    try:
        with open(_ADAM_PROPERTIES_PATH, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            return data.get("layers", {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


_ADAM_LAYERS: Dict[str, Any] = _load_adam_properties()


def apply_ontological_property_layer(state: ProofState) -> ProofState:
    pre_language = state.conceptual_state.get("pre_language", {})
    percept_units = pre_language.get("percept_units", [])
    proto_concepts = pre_language.get("proto_concepts", [])
    alignment = pre_language.get("reality_alignment", {})
    property_bundles: list[dict] = state.conceptual_state.get("property_bundles", [])

    # بنِ ملخص الخواص مصنَّفًا بالطبقات السبع
    property_summary: Dict[str, list[str]] = {
        layer: [] for layer in (
            "existence", "identity", "boundary",
            "perception", "relation", "action", "judgment",
        )
    }

    for bundle in property_bundles:
        for layer in property_summary:
            key = f"{layer}_props"
            props = bundle.get(key, [])
            for p in props:
                if p not in property_summary[layer]:
                    property_summary[layer].append(p)

    # أضف جميع الخواص الممكنة من specs/adam_properties.yaml بوصفها دليلًا مرجعيًا
    adam_reference: Dict[str, list[str]] = {}
    for layer_name, layer_data in _ADAM_LAYERS.items():
        if isinstance(layer_data, dict):
            adam_reference[layer_name] = [
                prop.get("key", "") for prop in layer_data.get("properties", [])
                if isinstance(prop, dict)
            ]

    state.conceptual_state["ontological_property_layer"] = {
        "percept_units": len(percept_units),
        "proto_concepts": len(proto_concepts),
        "alignment_score": alignment.get("score", 0.0),
        "alignment_non_blocking": True,
        "property_bundles_count": len(property_bundles),
        "property_summary": property_summary,
        "adam_reference_loaded": bool(adam_reference),
        "adam_layers_available": list(adam_reference.keys()),
    }
    state.add_trace(
        "ontological_property_layer",
        {
            "percept_units": len(percept_units),
            "proto_concepts": len(proto_concepts),
            "property_bundles_count": len(property_bundles),
            "layers_populated": [k for k, v in property_summary.items() if v],
            "alignment_non_blocking": True,
        },
    )
    return state
