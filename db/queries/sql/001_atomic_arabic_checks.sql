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

-- هـ. عرض الجذور مع ترتيب الصوامت
SELECT
    r.code AS root_code,
    r.arabic_root,
    rs.radical_index,
    su.code AS segment_code,
    su.arabic_symbol,
    su.arabic_name,
    rs.position_weight
FROM roots r
JOIN root_segments rs ON rs.root_id = r.id
JOIN segment_units su ON su.id = rs.segment_id
ORDER BY r.code, rs.radical_index;

-- و. التحقق من تطابق خانات JSON مع خانات pattern_slots العلائقية
SELECT
    p.code,
    jsonb_array_length(p.abstract_template->'slots') AS template_slots_count,
    COUNT(ps.id) AS relational_slots_count,
    CASE
        WHEN jsonb_array_length(p.abstract_template->'slots') = COUNT(ps.id) THEN 'OK'
        ELSE 'MISMATCH'
    END AS decomposition_status
FROM patterns p
LEFT JOIN pattern_slots ps ON ps.pattern_id = p.id
GROUP BY p.id, p.code, p.abstract_template
ORDER BY p.code;

-- ز. تفسير مكونات score(root, pattern) مباشرة
SELECT
    r.code AS root_code,
    p.code AS pattern_code,
    s.pattern_base_score,
    s.augmentation_fit,
    s.vocalic_fit,
    s.syllabic_balance,
    s.articulatory_cost,
    s.cognitive_cost,
    s.total_score,
    s.score_trace
FROM roots r
JOIN patterns p ON p.root_slots = r.radical_count
CROSS JOIN LATERAL score_root_pattern(r.id, p.id) s
WHERE r.code IN ('KTB', 'DRS', 'QWL')
  AND p.code IN ('FA3ALA', 'FA33ALA', 'FAA3ALA', 'AF3ALA', 'TAFA33ALA', 'ISTAF3ALA', 'FAA3IL', 'MAF3UL', 'MAF3AL', 'TAF3IL')
ORDER BY r.code, s.total_score DESC, p.code;
