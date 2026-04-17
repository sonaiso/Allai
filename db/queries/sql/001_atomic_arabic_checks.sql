-- 4) استعلامات فحص مباشرة

-- أ. عرض الصوامت مع مخارجها
SELECT
    s.code,
    s.arabic_symbol,
    s.arabic_name,
    ap.arabic_name AS articulation_place,
    s.articulation_manner,
    s.voicing,
    s.articulatory_cost
FROM segment_units s
LEFT JOIN articulation_places ap ON ap.id = s.articulation_place_id
ORDER BY s.articulation_rank NULLS LAST, s.code;

-- ب. عرض الحركات مرتبة بحسب الكلفة
SELECT
    code,
    arabic_symbol,
    arabic_name,
    category,
    phonetic_weight,
    temporal_weight,
    closure_degree,
    articulatory_cost,
    perceptual_cost
FROM vowel_units
ORDER BY articulatory_cost, phonetic_weight;

-- ج. عرض الأوزان مع بصمتها البنيوية
SELECT
    code,
    arabic_form,
    pattern_family,
    root_slots,
    augmentation_slots,
    vocalic_signature,
    closure_profile,
    derivational_load,
    cognitive_cost
FROM patterns
ORDER BY pattern_family, code;

-- د. عرض مواضع الزيادة داخل كل وزن
SELECT
    p.code AS pattern_code,
    p.arabic_form,
    a.code AS augmentation_code,
    a.arabic_name,
    pam.slot_position,
    pam.position_type,
    pam.cost_impact,
    pam.semantic_impact
FROM pattern_augmentation_map pam
JOIN patterns p ON p.id = pam.pattern_id
JOIN augmentation_types a ON a.id = pam.augmentation_type_id
ORDER BY p.code, pam.slot_position;
