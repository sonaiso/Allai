-- 3) أول دفعة بيانات معيارية فعلية

-- 3.1 جداول المخارج المرجعية
BEGIN;

INSERT INTO articulation_places (code, arabic_name, rank_order, geometric_zone, distance_from_core)
VALUES
('GLOTTAL', 'حنجري', 1, 'glottal', 0.100),
('PHARYNGEAL', 'حلقي', 2, 'deep', 0.200),
('UVULAR', 'لهوي', 3, 'deep', 0.300),
('VELAR', 'طبقي', 4, 'mid', 0.400),
('PALATAL', 'حنكي', 5, 'mid', 0.500),
('POSTALVEOLAR', 'لثوي خلفي', 6, 'front', 0.600),
('ALVEOLAR', 'لثوي', 7, 'front', 0.700),
('DENTAL', 'أسناني', 8, 'front', 0.800),
('LABIODENTAL', 'شفوي أسناني', 9, 'lip', 0.900),
('BILABIAL', 'شفوي', 10, 'lip', 1.000),
('NASAL_CAVITY', 'أنفي', 11, 'nasal', 0.850)
ON CONFLICT (code) DO NOTHING;

COMMIT;

-- 3.2 جدول أنواع الزيادة المرجعية
BEGIN;

INSERT INTO augmentation_types (code, arabic_name, kind, default_cost, semantic_hint)
VALUES
('AUG_ALIF_PREFIX', 'همزة/ألف في الصدر', 'prefix', 0.300, 'إدخال أو تعدية أو طلب بحسب الباب'),
('AUG_TA_PREFIX', 'تاء في الصدر', 'prefix', 0.250, 'مطاوعة أو تكلف أو انعكاس'),
('AUG_SIN_PREFIX', 'سين في الصدر', 'prefix', 0.350, 'طلب أو توجه'),
('AUG_MIM_PREFIX', 'ميم في الصدر', 'prefix', 0.280, 'اسمية أو مفعولية أو اسم مكان/زمان بحسب الصيغة'),
('AUG_ALIF_MEDIAL', 'ألف بعد الأصل الأول', 'lengthening', 0.220, 'مشاركة أو امتداد أو اسم فاعل'),
('AUG_WAW_MEDIAL', 'واو مدية وسطى', 'lengthening', 0.260, 'امتداد أو بنية اسمية'),
('AUG_YA_MEDIAL', 'ياء مدية وسطى', 'lengthening', 0.260, 'امتداد أو بنية وصفية/اسمية'),
('AUG_GEMINATE_R2', 'تضعيف الأصل الثاني', 'gemination', 0.450, 'تكثير أو تقوية أو تعدية'),
('AUG_NUN_SUFFIX', 'نون لاحقة', 'suffix', 0.300, 'علامة صرفية أو بنيوية'),
('AUG_TA_SUFFIX', 'تاء لاحقة', 'suffix', 0.250, 'مصدرية أو تأنيث أو بنية اسمية')
ON CONFLICT (code) DO NOTHING;

COMMIT;

-- 3.3 جدول الصوامت segment_units
BEGIN;

INSERT INTO segment_units (
    code, arabic_symbol, arabic_name, normalized_form, unicode_codepoint,
    segment_role, articulation_place_id, articulation_rank, articulation_manner,
    voicing, secondary_feature, is_consonant, is_sonorant, is_emphatic,
    is_guttural, is_coronal, stability_score, root_compatibility_score,
    articulatory_cost, perceptual_salience, notes
)
SELECT * FROM (
    VALUES
    ('HAMZA', 'ء', 'همزة', 'ء', 'U+0621', 'consonant',
        (SELECT id FROM articulation_places WHERE code='GLOTTAL'), 1, 'stop',
        'voiceless', 'plain', TRUE, FALSE, FALSE, TRUE, FALSE, 0.900, 0.850, 1.250, 1.100, 'وقف حنجري'),

    ('HA', 'ه', 'هاء', 'ه', 'U+0647', 'consonant',
        (SELECT id FROM articulation_places WHERE code='GLOTTAL'), 1, 'fricative',
        'voiceless', 'plain', TRUE, FALSE, FALSE, TRUE, FALSE, 1.050, 1.000, 0.950, 0.950, 'هاء مهموسة'),

    ('AIN', 'ع', 'عين', 'ع', 'U+0639', 'consonant',
        (SELECT id FROM articulation_places WHERE code='PHARYNGEAL'), 2, 'fricative',
        'voiced', 'plain', TRUE, FALSE, FALSE, TRUE, FALSE, 0.950, 0.900, 1.350, 1.200, 'حلقي مجهور'),

    ('HA_PHARYNGEAL', 'ح', 'حاء', 'ح', 'U+062D', 'consonant',
        (SELECT id FROM articulation_places WHERE code='PHARYNGEAL'), 2, 'fricative',
        'voiceless', 'plain', TRUE, FALSE, FALSE, TRUE, FALSE, 0.980, 0.930, 1.200, 1.050, 'حلقي مهموس'),

    ('KHA', 'خ', 'خاء', 'خ', 'U+062E', 'consonant',
        (SELECT id FROM articulation_places WHERE code='UVULAR'), 3, 'fricative',
        'voiceless', 'plain', TRUE, FALSE, FALSE, TRUE, FALSE, 0.970, 0.940, 1.180, 1.020, 'لهوي مهموس'),

    ('QAF', 'ق', 'قاف', 'ق', 'U+0642', 'consonant',
        (SELECT id FROM articulation_places WHERE code='UVULAR'), 3, 'stop',
        'voiceless', 'plain', TRUE, FALSE, FALSE, FALSE, FALSE, 1.050, 1.020, 1.150, 1.120, 'شديد لهوي'),

    ('KAF', 'ك', 'كاف', 'ك', 'U+0643', 'consonant',
        (SELECT id FROM articulation_places WHERE code='VELAR'), 4, 'stop',
        'voiceless', 'plain', TRUE, FALSE, FALSE, FALSE, FALSE, 1.080, 1.050, 1.000, 1.050, 'شديد طبقي'),

    ('JIM', 'ج', 'جيم', 'ج', 'U+062C', 'consonant',
        (SELECT id FROM articulation_places WHERE code='PALATAL'), 5, 'affricate',
        'voiced', 'plain', TRUE, FALSE, FALSE, FALSE, FALSE, 1.000, 0.970, 1.100, 1.100, 'مركب'),

    ('SHIN', 'ش', 'شين', 'ش', 'U+0634', 'consonant',
        (SELECT id FROM articulation_places WHERE code='POSTALVEOLAR'), 6, 'fricative',
        'voiceless', 'plain', TRUE, FALSE, FALSE, FALSE, TRUE, 1.020, 1.000, 1.050, 1.080, 'احتكاكي'),

    ('SAD', 'ص', 'صاد', 'ص', 'U+0635', 'consonant',
        (SELECT id FROM articulation_places WHERE code='ALVEOLAR'), 7, 'fricative',
        'voiceless', 'emphatic', TRUE, FALSE, TRUE, FALSE, TRUE, 0.980, 0.960, 1.220, 1.150, 'مطبق'),

    ('DAD', 'ض', 'ضاد', 'ض', 'U+0636', 'consonant',
        (SELECT id FROM articulation_places WHERE code='ALVEOLAR'), 7, 'stop',
        'voiced', 'emphatic', TRUE, FALSE, TRUE, FALSE, TRUE, 0.920, 0.900, 1.300, 1.200, 'مطبق مجهور'),

    ('TA', 'ط', 'طاء', 'ط', 'U+0637', 'consonant',
        (SELECT id FROM articulation_places WHERE code='ALVEOLAR'), 7, 'stop',
        'voiceless', 'emphatic', TRUE, FALSE, TRUE, FALSE, TRUE, 0.980, 0.960, 1.250, 1.150, 'شديد مطبق'),

    ('ZA', 'ظ', 'ظاء', 'ظ', 'U+0638', 'consonant',
        (SELECT id FROM articulation_places WHERE code='DENTAL'), 8, 'fricative',
        'voiced', 'emphatic', TRUE, FALSE, TRUE, FALSE, TRUE, 0.900, 0.880, 1.280, 1.170, 'أسناني مطبق'),

    ('DAL', 'د', 'دال', 'د', 'U+062F', 'consonant',
        (SELECT id FROM articulation_places WHERE code='DENTAL'), 8, 'stop',
        'voiced', 'plain', TRUE, FALSE, FALSE, FALSE, TRUE, 1.100, 1.060, 0.900, 1.050, 'شديد مجهور'),

    ('TA_SIMPLE', 'ت', 'تاء', 'ت', 'U+062A', 'consonant',
        (SELECT id FROM articulation_places WHERE code='DENTAL'), 8, 'stop',
        'voiceless', 'plain', TRUE, FALSE, FALSE, FALSE, TRUE, 1.120, 1.080, 0.920, 1.040, 'شديد مهموس'),

    ('THA', 'ث', 'ثاء', 'ث', 'U+062B', 'consonant',
        (SELECT id FROM articulation_places WHERE code='DENTAL'), 8, 'fricative',
        'voiceless', 'plain', TRUE, FALSE, FALSE, FALSE, TRUE, 1.000, 0.980, 1.000, 1.000, 'أسناني مهموس'),

    ('DHAL', 'ذ', 'ذال', 'ذ', 'U+0630', 'consonant',
        (SELECT id FROM articulation_places WHERE code='DENTAL'), 8, 'fricative',
        'voiced', 'plain', TRUE, FALSE, FALSE, FALSE, TRUE, 0.980, 0.960, 1.020, 1.040, 'أسناني مجهور'),

    ('RA', 'ر', 'راء', 'ر', 'U+0631', 'consonant',
        (SELECT id FROM articulation_places WHERE code='ALVEOLAR'), 7, 'trill',
        'voiced', 'plain', TRUE, TRUE, FALSE, FALSE, TRUE, 1.050, 1.020, 0.980, 1.180, 'مكرر'),

    ('ZAY', 'ز', 'زاي', 'ز', 'U+0632', 'consonant',
        (SELECT id FROM articulation_places WHERE code='ALVEOLAR'), 7, 'fricative',
        'voiced', 'plain', TRUE, FALSE, FALSE, FALSE, TRUE, 1.040, 1.010, 0.960, 1.080, 'احتكاكي مجهور'),

    ('SIN', 'س', 'سين', 'س', 'U+0633', 'consonant',
        (SELECT id FROM articulation_places WHERE code='ALVEOLAR'), 7, 'fricative',
        'voiceless', 'plain', TRUE, FALSE, FALSE, FALSE, TRUE, 1.060, 1.030, 0.940, 1.050, 'احتكاكي مهموس'),

    ('LAM', 'ل', 'لام', 'ل', 'U+0644', 'consonant',
        (SELECT id FROM articulation_places WHERE code='ALVEOLAR'), 7, 'lateral',
        'voiced', 'plain', TRUE, TRUE, FALSE, FALSE, TRUE, 1.150, 1.100, 0.900, 1.150, 'جانبي'),

    ('NUN', 'ن', 'نون', 'ن', 'U+0646', 'consonant',
        (SELECT id FROM articulation_places WHERE code='NASAL_CAVITY'), 11, 'nasal',
        'voiced', 'plain', TRUE, TRUE, FALSE, FALSE, TRUE, 1.120, 1.080, 0.950, 1.120, 'أنفي'),

    ('FA', 'ف', 'فاء', 'ف', 'U+0641', 'consonant',
        (SELECT id FROM articulation_places WHERE code='LABIODENTAL'), 9, 'fricative',
        'voiceless', 'plain', TRUE, FALSE, FALSE, FALSE, FALSE, 1.050, 1.010, 0.980, 1.050, 'شفوي أسناني'),

    ('BA', 'ب', 'باء', 'ب', 'U+0628', 'consonant',
        (SELECT id FROM articulation_places WHERE code='BILABIAL'), 10, 'stop',
        'voiced', 'plain', TRUE, FALSE, FALSE, FALSE, FALSE, 1.120, 1.080, 0.900, 1.040, 'شفوي مجهور'),

    ('MIM', 'م', 'ميم', 'م', 'U+0645', 'consonant',
        (SELECT id FROM articulation_places WHERE code='BILABIAL'), 10, 'nasal',
        'voiced', 'plain', TRUE, TRUE, FALSE, FALSE, FALSE, 1.150, 1.100, 0.940, 1.130, 'أنفي شفوي'),

    ('WAW', 'و', 'واو', 'و', 'U+0648', 'semi_vowel',
        (SELECT id FROM articulation_places WHERE code='BILABIAL'), 10, 'glide',
        'voiced', 'plain', FALSE, TRUE, FALSE, FALSE, FALSE, 1.000, 0.950, 1.020, 1.080, 'شبه صائت'),

    ('YA', 'ي', 'ياء', 'ي', 'U+064A', 'semi_vowel',
        (SELECT id FROM articulation_places WHERE code='PALATAL'), 5, 'glide',
        'voiced', 'plain', FALSE, TRUE, FALSE, FALSE, FALSE, 1.000, 0.950, 1.000, 1.100, 'شبه صائت'),

    ('ALIF', 'ا', 'ألف', 'ا', 'U+0627', 'long_vowel_carrier',
        NULL, NULL, 'carrier',
        'neutral', 'plain', FALSE, TRUE, FALSE, FALSE, FALSE, 0.950, 0.700, 0.800, 0.900, 'حامل مد')
) AS t(
    code, arabic_symbol, arabic_name, normalized_form, unicode_codepoint,
    segment_role, articulation_place_id, articulation_rank, articulation_manner,
    voicing, secondary_feature, is_consonant, is_sonorant, is_emphatic,
    is_guttural, is_coronal, stability_score, root_compatibility_score,
    articulatory_cost, perceptual_salience, notes
)
ON CONFLICT (code) DO NOTHING;

COMMIT;

-- 3.4 جدول الحركات vowel_units
BEGIN;

INSERT INTO vowel_units (
    code, arabic_symbol, arabic_name, unicode_codepoint, category,
    phonetic_weight, temporal_weight, syllabic_role, morphological_role,
    syntactic_role, closure_degree, openness_degree, articulatory_cost,
    perceptual_cost, can_lengthen, can_geminate, can_inflect,
    transition_class, notes
)
VALUES
('FATHA', 'َ', 'فتحة', 'U+064E', 'short',
    1.000, 1.000, 'nucleus', 'neutral',
    'none', 0.350, 0.850, 0.900, 0.850, TRUE, FALSE, TRUE,
    'open_short', 'حركة قصيرة منفتحة'),

('DAMMA', 'ُ', 'ضمة', 'U+064F', 'short',
    1.100, 1.000, 'nucleus', 'neutral',
    'none', 0.550, 0.650, 1.000, 0.900, TRUE, FALSE, TRUE,
    'rounded_short', 'حركة قصيرة مستديرة'),

('KASRA', 'ِ', 'كسرة', 'U+0650', 'short',
    1.050, 1.000, 'nucleus', 'neutral',
    'none', 0.450, 0.750, 0.950, 0.880, TRUE, FALSE, TRUE,
    'front_short', 'حركة قصيرة أمامية'),

('SUKUN', 'ْ', 'سكون', 'U+0652', 'sukun',
    0.800, 0.000, 'coda_modifier', 'neutral',
    'jussive', 0.950, 0.050, 0.850, 0.950, FALSE, TRUE, TRUE,
    'closure_stop', 'انغلاق مقطعي'),

('ALIF_MADD', 'ا', 'ألف مد', 'U+0627', 'long',
    1.400, 2.000, 'nucleus', 'derivational',
    'none', 0.300, 0.900, 0.950, 0.850, FALSE, FALSE, FALSE,
    'open_long', 'مد بالألف'),

('WAW_MADD', 'و', 'واو مد', 'U+0648', 'long',
    1.450, 2.000, 'nucleus', 'derivational',
    'none', 0.600, 0.550, 1.050, 0.950, FALSE, FALSE, FALSE,
    'rounded_long', 'مد بالواو'),

('YA_MADD', 'ي', 'ياء مد', 'U+064A', 'long',
    1.450, 2.000, 'nucleus', 'derivational',
    'none', 0.500, 0.650, 1.000, 0.920, FALSE, FALSE, FALSE,
    'front_long', 'مد بالياء'),

('TANWEEN_FATH', 'ً', 'تنوين فتح', 'U+064B', 'tanween',
    1.300, 1.200, 'nucleus', 'inflectional',
    'accusative', 0.400, 0.800, 1.100, 1.000, FALSE, FALSE, TRUE,
    'nunation_open', 'تنوين منصوب'),

('TANWEEN_DAMM', 'ٌ', 'تنوين ضم', 'U+064C', 'tanween',
    1.350, 1.200, 'nucleus', 'inflectional',
    'nominative', 0.600, 0.600, 1.150, 1.050, FALSE, FALSE, TRUE,
    'nunation_rounded', 'تنوين مرفوع'),

('TANWEEN_KASR', 'ٍ', 'تنوين كسر', 'U+064D', 'tanween',
    1.300, 1.200, 'nucleus', 'inflectional',
    'genitive', 0.500, 0.700, 1.120, 1.020, FALSE, FALSE, TRUE,
    'nunation_front', 'تنوين مجرور'),

('SHADDA_FATHA', 'َّ', 'شدة مع فتحة', 'U+0651+064E', 'shadda_combo',
    1.800, 1.400, 'nucleus', 'mixed',
    'none', 0.700, 0.500, 1.350, 1.100, FALSE, FALSE, FALSE,
    'geminated_open', 'تشديد مع فتحة'),

('SHADDA_DAMMA', 'ُّ', 'شدة مع ضمة', 'U+0651+064F', 'shadda_combo',
    1.900, 1.400, 'nucleus', 'mixed',
    'none', 0.780, 0.420, 1.420, 1.150, FALSE, FALSE, FALSE,
    'geminated_rounded', 'تشديد مع ضمة'),

('SHADDA_KASRA', 'ِّ', 'شدة مع كسرة', 'U+0651+0650', 'shadda_combo',
    1.850, 1.400, 'nucleus', 'mixed',
    'none', 0.720, 0.480, 1.380, 1.120, FALSE, FALSE, FALSE,
    'geminated_front', 'تشديد مع كسرة'),

('SHADDA_SUKUN', 'ّْ', 'شدة مع سكون', 'U+0651+0652', 'shadda_combo',
    1.950, 1.100, 'coda_modifier', 'mixed',
    'jussive', 0.920, 0.100, 1.500, 1.250, FALSE, FALSE, TRUE,
    'geminated_closed', 'تشديد مع سكون'),

('CASE_DAMMA', 'ُ', 'علامة رفع أصلية', 'U+064F', 'case_marker',
    1.000, 1.000, 'nucleus', 'inflectional',
    'nominative', 0.550, 0.650, 0.980, 0.900, FALSE, FALSE, TRUE,
    'case_nom', 'ضمة إعرابية'),

('CASE_FATHA', 'َ', 'علامة نصب أصلية', 'U+064E', 'case_marker',
    1.000, 1.000, 'nucleus', 'inflectional',
    'accusative', 0.350, 0.850, 0.900, 0.850, FALSE, FALSE, TRUE,
    'case_acc', 'فتحة إعرابية'),

('CASE_KASRA', 'ِ', 'علامة جر أصلية', 'U+0650', 'case_marker',
    1.000, 1.000, 'nucleus', 'inflectional',
    'genitive', 0.450, 0.750, 0.950, 0.880, FALSE, FALSE, TRUE,
    'case_gen', 'كسرة إعرابية'),

('CASE_SUKUN', 'ْ', 'علامة جزم أصلية', 'U+0652', 'case_marker',
    0.800, 0.000, 'coda_modifier', 'inflectional',
    'jussive', 0.950, 0.050, 0.850, 0.950, FALSE, FALSE, TRUE,
    'case_jus', 'سكون جزمي')
ON CONFLICT (code) DO NOTHING;

COMMIT;

-- 3.5 جدول المقاطع syllable_patterns
BEGIN;

INSERT INTO syllable_patterns (
    code, arabic_name, shape_length, mora_count, closure_degree,
    articulatory_cost, perceptual_stability, allowed_initial,
    allowed_medial, allowed_final, notes
)
VALUES
('CV', 'صامت + حركة قصيرة', 2, 1.00, 0.300, 1.000, 1.200, TRUE, TRUE, TRUE, 'المقطع الخفيف المفتوح'),
('CVC', 'صامت + حركة قصيرة + صامت', 3, 2.00, 0.700, 1.350, 1.300, TRUE, TRUE, TRUE, 'مقطع مغلق'),
('CVV', 'صامت + حركة طويلة', 3, 2.00, 0.450, 1.250, 1.250, TRUE, TRUE, TRUE, 'مقطع ممدود'),
('CVVC', 'صامت + حركة طويلة + صامت', 4, 3.00, 0.780, 1.600, 1.350, FALSE, TRUE, TRUE, 'مقطع ثقيل مغلق'),
('CVCC', 'صامت + حركة قصيرة + صامتين', 4, 3.00, 0.900, 1.850, 1.100, FALSE, FALSE, TRUE, 'مقطع أثقل'),
('CCV', 'صامتان + حركة', 3, 1.50, 0.650, 1.500, 0.950, FALSE, TRUE, FALSE, 'يُستعمل فقط إن أجاز النظام العنقود')
ON CONFLICT (code) DO NOTHING;

COMMIT;

-- 3.6 جدول انتقالات الحركات vowel_transitions
BEGIN;

INSERT INTO vowel_transitions (
    from_vowel_id, to_vowel_id, transition_type, trigger_condition,
    cost_delta, closure_delta, semantic_effect, formal_rule, valid_scope
)
VALUES
(
    (SELECT id FROM vowel_units WHERE code='FATHA'),
    (SELECT id FROM vowel_units WHERE code='ALIF_MADD'),
    'phonological',
    'امتداد الفتحة في بنية تسمح بالمد',
    0.400,
    -0.050,
    'امتداد زمني وانفتاح نسبي',
    'a -> aa',
    'stem'
),
(
    (SELECT id FROM vowel_units WHERE code='DAMMA'),
    (SELECT id FROM vowel_units WHERE code='WAW_MADD'),
    'phonological',
    'امتداد الضمة في بنية تسمح بالمد',
    0.350,
    0.050,
    'استدارة ممتدة',
    'u -> uu',
    'stem'
),
(
    (SELECT id FROM vowel_units WHERE code='KASRA'),
    (SELECT id FROM vowel_units WHERE code='YA_MADD'),
    'phonological',
    'امتداد الكسرة في بنية تسمح بالمد',
    0.350,
    0.050,
    'أمامية ممتدة',
    'i -> ii',
    'stem'
),
(
    (SELECT id FROM vowel_units WHERE code='FATHA'),
    (SELECT id FROM vowel_units WHERE code='CASE_FATHA'),
    'inflectional',
    'تحول الحركة إلى وظيفة إعرابية صريحة',
    0.000,
    0.000,
    'نصب',
    'lexical_fatha -> accusative_fatha',
    'word'
),
(
    (SELECT id FROM vowel_units WHERE code='DAMMA'),
    (SELECT id FROM vowel_units WHERE code='CASE_DAMMA'),
    'inflectional',
    'تحول الحركة إلى وظيفة إعرابية صريحة',
    0.000,
    0.000,
    'رفع',
    'lexical_damma -> nominative_damma',
    'word'
),
(
    (SELECT id FROM vowel_units WHERE code='KASRA'),
    (SELECT id FROM vowel_units WHERE code='CASE_KASRA'),
    'inflectional',
    'تحول الحركة إلى وظيفة إعرابية صريحة',
    0.000,
    0.000,
    'جر',
    'lexical_kasra -> genitive_kasra',
    'word'
),
(
    (SELECT id FROM vowel_units WHERE code='SUKUN'),
    (SELECT id FROM vowel_units WHERE code='CASE_SUKUN'),
    'inflectional',
    'تحول السكون إلى علامة جزم صريحة',
    0.000,
    0.000,
    'جزم',
    'lexical_sukun -> jussive_sukun',
    'word'
),
(
    (SELECT id FROM vowel_units WHERE code='FATHA'),
    (SELECT id FROM vowel_units WHERE code='SHADDA_FATHA'),
    'derivational',
    'دخول التضعيف مع الحركة المفتوحة',
    0.700,
    0.350,
    'تكثير أو تقوية أو تعدية',
    'a -> CCa',
    'stem'
),
(
    (SELECT id FROM vowel_units WHERE code='DAMMA'),
    (SELECT id FROM vowel_units WHERE code='SHADDA_DAMMA'),
    'derivational',
    'دخول التضعيف مع الحركة المضمومة',
    0.800,
    0.230,
    'تقوية مع استدارة',
    'u -> CCu',
    'stem'
),
(
    (SELECT id FROM vowel_units WHERE code='KASRA'),
    (SELECT id FROM vowel_units WHERE code='SHADDA_KASRA'),
    'derivational',
    'دخول التضعيف مع الحركة المكسورة',
    0.780,
    0.270,
    'تقوية مع أمامية',
    'i -> CCi',
    'stem'
)
ON CONFLICT DO NOTHING;

COMMIT;

-- 3.7 جدول الأوزان patterns
BEGIN;

INSERT INTO patterns (
    code, arabic_form, transliteration, pattern_family,
    root_slots, augmentation_slots, abstract_template, vocalic_signature,
    closure_profile, derivational_load, inflectional_potential,
    semantic_base_class, usage_stability, metaphor_transferability,
    cognitive_cost, articulatory_cost, notes
)
VALUES
(
    'FA3ALA',
    'فَعَلَ',
    'faʿala',
    'verb',
    3,
    0,
    '{
      "slots": [
        {"type":"root","index":1},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":2},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":3},
        {"type":"vowel","value":"FATHA"}
      ]
    }'::jsonb,
    'a-a-a',
    0.550,
    0.300,
    0.900,
    'event_basic',
    1.500,
    0.800,
    1.000,
    1.000,
    'الأصل الفعلي البسيط'
),
(
    'FA33ALA',
    'فَعَّلَ',
    'faʿʿala',
    'verb',
    3,
    1,
    '{
      "slots": [
        {"type":"root","index":1},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":2},
        {"type":"gemination","target":"root2"},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":3},
        {"type":"vowel","value":"FATHA"}
      ]
    }'::jsonb,
    'a-~a-a',
    0.720,
    0.800,
    0.850,
    'causative_intensive',
    1.300,
    0.900,
    1.350,
    1.400,
    'باب التفعيل'
),
(
    'FAA3ALA',
    'فَاعَلَ',
    'faaʿala',
    'verb',
    3,
    1,
    '{
      "slots": [
        {"type":"root","index":1},
        {"type":"vowel","value":"FATHA"},
        {"type":"lengthening","value":"ALIF_MADD"},
        {"type":"root","index":2},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":3},
        {"type":"vowel","value":"FATHA"}
      ]
    }'::jsonb,
    'aa-a-a',
    0.620,
    0.650,
    0.800,
    'participatory_relational',
    1.250,
    1.000,
    1.200,
    1.250,
    'باب المفاعلة'
),
(
    'AF3ALA',
    'أَفْعَلَ',
    'ʾafʿala',
    'verb',
    3,
    1,
    '{
      "slots": [
        {"type":"augmentation","value":"AUG_ALIF_PREFIX"},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":1},
        {"type":"vowel","value":"SUKUN"},
        {"type":"root","index":2},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":3},
        {"type":"vowel","value":"FATHA"}
      ]
    }'::jsonb,
    'a-0-a-a',
    0.680,
    0.900,
    0.850,
    'causative_entry',
    1.350,
    0.850,
    1.250,
    1.300,
    'باب الإفعال'
),
(
    'TAFA33ALA',
    'تَفَعَّلَ',
    'tafaʿʿala',
    'verb',
    3,
    2,
    '{
      "slots": [
        {"type":"augmentation","value":"AUG_TA_PREFIX"},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":1},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":2},
        {"type":"gemination","target":"root2"},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":3},
        {"type":"vowel","value":"FATHA"}
      ]
    }'::jsonb,
    'ta-a-~a-a',
    0.760,
    1.100,
    0.800,
    'reflexive_intensive',
    1.150,
    1.000,
    1.500,
    1.520,
    'باب التفعل'
),
(
    'ISTAF3ALA',
    'اسْتَفْعَلَ',
    'istafʿala',
    'verb',
    3,
    3,
    '{
      "slots": [
        {"type":"augmentation","value":"AUG_ALIF_PREFIX"},
        {"type":"augmentation","value":"AUG_SIN_PREFIX"},
        {"type":"augmentation","value":"AUG_TA_PREFIX"},
        {"type":"root","index":1},
        {"type":"vowel","value":"SUKUN"},
        {"type":"root","index":2},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":3},
        {"type":"vowel","value":"FATHA"}
      ]
    }'::jsonb,
    'ista-0-a-a',
    0.820,
    1.400,
    0.750,
    'request_or_seek',
    1.100,
    1.050,
    1.700,
    1.650,
    'باب الاستفعال'
),
(
    'FAA3IL',
    'فَاعِل',
    'faaʿil',
    'participle',
    3,
    1,
    '{
      "slots": [
        {"type":"root","index":1},
        {"type":"vowel","value":"FATHA"},
        {"type":"lengthening","value":"ALIF_MADD"},
        {"type":"root","index":2},
        {"type":"vowel","value":"KASRA"},
        {"type":"root","index":3}
      ]
    }'::jsonb,
    'aa-i',
    0.500,
    0.700,
    0.700,
    'agentive',
    1.400,
    1.100,
    1.100,
    1.080,
    'اسم الفاعل'
),
(
    'MAF3UL',
    'مَفْعُول',
    'mafʿuul',
    'participle',
    3,
    2,
    '{
      "slots": [
        {"type":"augmentation","value":"AUG_MIM_PREFIX"},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":1},
        {"type":"vowel","value":"SUKUN"},
        {"type":"root","index":2},
        {"type":"vowel","value":"DAMMA"},
        {"type":"lengthening","value":"WAW_MADD"},
        {"type":"root","index":3}
      ]
    }'::jsonb,
    'ma-0-uu',
    0.700,
    0.950,
    0.650,
    'patientive',
    1.300,
    0.950,
    1.250,
    1.280,
    'اسم المفعول'
),
(
    'MAF3AL',
    'مَفْعَل',
    'mafʿal',
    'place_noun',
    3,
    1,
    '{
      "slots": [
        {"type":"augmentation","value":"AUG_MIM_PREFIX"},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":1},
        {"type":"vowel","value":"SUKUN"},
        {"type":"root","index":2},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":3}
      ]
    }'::jsonb,
    'ma-0-a',
    0.650,
    0.800,
    0.700,
    'place_or_time',
    1.350,
    0.900,
    1.100,
    1.100,
    'اسم مكان/زمان محتمل'
),
(
    'TAF3IL',
    'تَفْعِيل',
    'tafʿiil',
    'masdar',
    3,
    2,
    '{
      "slots": [
        {"type":"augmentation","value":"AUG_TA_PREFIX"},
        {"type":"vowel","value":"FATHA"},
        {"type":"root","index":1},
        {"type":"vowel","value":"SUKUN"},
        {"type":"root","index":2},
        {"type":"vowel","value":"KASRA"},
        {"type":"lengthening","value":"YA_MADD"},
        {"type":"root","index":3}
      ]
    }'::jsonb,
    'ta-0-ii',
    0.680,
    1.000,
    0.500,
    'verbal_noun_process',
    1.250,
    1.000,
    1.250,
    1.220,
    'مصدر تفعيل'
)
ON CONFLICT (code) DO NOTHING;

COMMIT;

-- 3.8 جدول مواضع الزيادة pattern_augmentation_map
BEGIN;

INSERT INTO pattern_augmentation_map (
    pattern_id, augmentation_type_id, slot_position, position_type,
    obligatory, cost_impact, semantic_impact, notes
)
VALUES
(
    (SELECT id FROM patterns WHERE code='FA33ALA'),
    (SELECT id FROM augmentation_types WHERE code='AUG_GEMINATE_R2'),
    1,
    'geminate_r2',
    TRUE,
    0.450,
    'تكثير/تقوية',
    'باب التفعيل'
),
(
    (SELECT id FROM patterns WHERE code='FAA3ALA'),
    (SELECT id FROM augmentation_types WHERE code='AUG_ALIF_MEDIAL'),
    1,
    'lengthen_after_r1',
    TRUE,
    0.220,
    'مشاركة/مفاعلة',
    'باب المفاعلة'
),
(
    (SELECT id FROM patterns WHERE code='AF3ALA'),
    (SELECT id FROM augmentation_types WHERE code='AUG_ALIF_PREFIX'),
    1,
    'pre_root',
    TRUE,
    0.300,
    'إدخال/تعدية',
    'باب الإفعال'
),
(
    (SELECT id FROM patterns WHERE code='TAFA33ALA'),
    (SELECT id FROM augmentation_types WHERE code='AUG_TA_PREFIX'),
    1,
    'pre_root',
    TRUE,
    0.250,
    'مطاوعة/انعكاس',
    'باب التفعل'
),
(
    (SELECT id FROM patterns WHERE code='TAFA33ALA'),
    (SELECT id FROM augmentation_types WHERE code='AUG_GEMINATE_R2'),
    2,
    'geminate_r2',
    TRUE,
    0.450,
    'تكثير',
    'باب التفعل'
),
(
    (SELECT id FROM patterns WHERE code='ISTAF3ALA'),
    (SELECT id FROM augmentation_types WHERE code='AUG_ALIF_PREFIX'),
    1,
    'pre_root',
    TRUE,
    0.300,
    'بنية افتتاحية',
    'باب الاستفعال'
),
(
    (SELECT id FROM patterns WHERE code='ISTAF3ALA'),
    (SELECT id FROM augmentation_types WHERE code='AUG_SIN_PREFIX'),
    2,
    'pre_root',
    TRUE,
    0.350,
    'طلب/سعي',
    'باب الاستفعال'
),
(
    (SELECT id FROM patterns WHERE code='ISTAF3ALA'),
    (SELECT id FROM augmentation_types WHERE code='AUG_TA_PREFIX'),
    3,
    'pre_root',
    TRUE,
    0.250,
    'توجه بنيوي',
    'باب الاستفعال'
),
(
    (SELECT id FROM patterns WHERE code='FAA3IL'),
    (SELECT id FROM augmentation_types WHERE code='AUG_ALIF_MEDIAL'),
    1,
    'lengthen_after_r1',
    TRUE,
    0.220,
    'اسمية فاعلية',
    'اسم الفاعل'
),
(
    (SELECT id FROM patterns WHERE code='MAF3UL'),
    (SELECT id FROM augmentation_types WHERE code='AUG_MIM_PREFIX'),
    1,
    'pre_root',
    TRUE,
    0.280,
    'اسمية مفعولية',
    'اسم المفعول'
),
(
    (SELECT id FROM patterns WHERE code='MAF3UL'),
    (SELECT id FROM augmentation_types WHERE code='AUG_WAW_MEDIAL'),
    2,
    'lengthen_after_r2',
    TRUE,
    0.260,
    'مد مفعولي',
    'اسم المفعول'
),
(
    (SELECT id FROM patterns WHERE code='MAF3AL'),
    (SELECT id FROM augmentation_types WHERE code='AUG_MIM_PREFIX'),
    1,
    'pre_root',
    TRUE,
    0.280,
    'اسمية مكان/زمان',
    'اسم مكان/زمان'
),
(
    (SELECT id FROM patterns WHERE code='TAF3IL'),
    (SELECT id FROM augmentation_types WHERE code='AUG_TA_PREFIX'),
    1,
    'pre_root',
    TRUE,
    0.250,
    'مصدرية',
    'مصدر تفعيل'
),
(
    (SELECT id FROM patterns WHERE code='TAF3IL'),
    (SELECT id FROM augmentation_types WHERE code='AUG_YA_MEDIAL'),
    2,
    'lengthen_after_r2',
    TRUE,
    0.260,
    'امتداد مصدري',
    'مصدر تفعيل'
)
ON CONFLICT DO NOTHING;

COMMIT;
