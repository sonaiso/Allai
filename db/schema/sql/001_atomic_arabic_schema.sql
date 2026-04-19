BEGIN;

-- =========================================================
-- 0. EXTENSIONS
-- =========================================================
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =========================================================
-- 1. ENUM TYPES
-- =========================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'segment_role_enum') THEN
        CREATE TYPE segment_role_enum AS ENUM (
            'consonant',
            'semi_vowel',
            'long_vowel_carrier',
            'hamza_carrier',
            'boundary_marker'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'voicing_enum') THEN
        CREATE TYPE voicing_enum AS ENUM (
            'voiced',
            'voiceless',
            'neutral'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'manner_enum') THEN
        CREATE TYPE manner_enum AS ENUM (
            'stop',
            'fricative',
            'affricate',
            'nasal',
            'lateral',
            'trill',
            'tap',
            'approximant',
            'glide',
            'carrier',
            'other'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'secondary_feature_enum') THEN
        CREATE TYPE secondary_feature_enum AS ENUM (
            'emphatic',
            'non_emphatic',
            'plain',
            'spread',
            'other'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'vowel_category_enum') THEN
        CREATE TYPE vowel_category_enum AS ENUM (
            'short',
            'sukun',
            'long',
            'tanween',
            'shadda_combo',
            'case_marker',
            'derived_case'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'syllabic_role_enum') THEN
        CREATE TYPE syllabic_role_enum AS ENUM (
            'onset_support',
            'nucleus',
            'coda_modifier',
            'boundary'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'morphological_role_enum') THEN
        CREATE TYPE morphological_role_enum AS ENUM (
            'rootive',
            'augmentive',
            'inflectional',
            'derivational',
            'neutral',
            'mixed'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'syntactic_role_enum') THEN
        CREATE TYPE syntactic_role_enum AS ENUM (
            'nominative',
            'accusative',
            'genitive',
            'jussive',
            'none',
            'mixed'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transition_type_enum') THEN
        CREATE TYPE transition_type_enum AS ENUM (
            'derivational',
            'inflectional',
            'phonological',
            'analogical',
            'compensatory'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transition_scope_enum') THEN
        CREATE TYPE transition_scope_enum AS ENUM (
            'root',
            'stem',
            'word',
            'phrase'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pattern_family_enum') THEN
        CREATE TYPE pattern_family_enum AS ENUM (
            'verb',
            'noun',
            'masdar',
            'adjective',
            'participle',
            'intensive',
            'comparative',
            'instrument',
            'time_noun',
            'place_noun',
            'other'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'augmentation_kind_enum') THEN
        CREATE TYPE augmentation_kind_enum AS ENUM (
            'prefix',
            'infix',
            'suffix',
            'gemination',
            'lengthening'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'position_type_enum') THEN
        CREATE TYPE position_type_enum AS ENUM (
            'pre_root',
            'between_r1_r2',
            'between_r2_r3',
            'between_r3_r4',
            'post_root',
            'geminate_r1',
            'geminate_r2',
            'geminate_r3',
            'lengthen_after_r1',
            'lengthen_after_r2',
            'lengthen_after_r3',
            'fixed_slot'
        );
    END IF;
END
$$;

-- =========================================================
-- 2. REFERENCE TABLES
-- =========================================================

CREATE TABLE IF NOT EXISTS articulation_places (
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(50) NOT NULL UNIQUE,
    arabic_name         VARCHAR(100) NOT NULL,
    rank_order          INTEGER NOT NULL UNIQUE CHECK (rank_order > 0),
    geometric_zone      VARCHAR(30) NOT NULL,
    distance_from_core  NUMERIC(6,3) NOT NULL CHECK (distance_from_core >= 0)
);

CREATE TABLE IF NOT EXISTS augmentation_types (
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(50) NOT NULL UNIQUE,
    arabic_name         VARCHAR(100) NOT NULL,
    kind                augmentation_kind_enum NOT NULL,
    default_cost        NUMERIC(6,3) NOT NULL CHECK (default_cost >= 0),
    semantic_hint       VARCHAR(200)
);

-- =========================================================
-- 3. TABLE 1: segment_units
-- =========================================================

CREATE TABLE IF NOT EXISTS segment_units (
    id                          BIGSERIAL PRIMARY KEY,
    code                        VARCHAR(50) NOT NULL UNIQUE,
    arabic_symbol               VARCHAR(10) NOT NULL,
    arabic_name                 VARCHAR(100) NOT NULL,
    normalized_form             VARCHAR(10) NOT NULL,
    unicode_codepoint           VARCHAR(20),
    segment_role                segment_role_enum NOT NULL,
    articulation_place_id       BIGINT REFERENCES articulation_places(id),
    articulation_rank           INTEGER CHECK (articulation_rank IS NULL OR articulation_rank > 0),
    articulation_manner         manner_enum NOT NULL,
    voicing                     voicing_enum NOT NULL DEFAULT 'neutral',
    secondary_feature           secondary_feature_enum NOT NULL DEFAULT 'plain',
    is_consonant                BOOLEAN NOT NULL DEFAULT TRUE,
    is_sonorant                 BOOLEAN NOT NULL DEFAULT FALSE,
    is_emphatic                 BOOLEAN NOT NULL DEFAULT FALSE,
    is_guttural                 BOOLEAN NOT NULL DEFAULT FALSE,
    is_coronal                  BOOLEAN NOT NULL DEFAULT FALSE,
    stability_score             NUMERIC(6,3) NOT NULL DEFAULT 1.000 CHECK (stability_score >= 0),
    root_compatibility_score    NUMERIC(6,3) NOT NULL DEFAULT 1.000 CHECK (root_compatibility_score >= 0),
    articulatory_cost           NUMERIC(6,3) NOT NULL DEFAULT 1.000 CHECK (articulatory_cost >= 0),
    perceptual_salience         NUMERIC(6,3) NOT NULL DEFAULT 1.000 CHECK (perceptual_salience >= 0),
    notes                       TEXT
);

CREATE INDEX IF NOT EXISTS idx_segment_units_symbol ON segment_units(arabic_symbol);
CREATE INDEX IF NOT EXISTS idx_segment_units_role ON segment_units(segment_role);
CREATE INDEX IF NOT EXISTS idx_segment_units_place ON segment_units(articulation_place_id);

-- =========================================================
-- 4. TABLE 2: vowel_units
-- =========================================================

CREATE TABLE IF NOT EXISTS vowel_units (
    id                      BIGSERIAL PRIMARY KEY,
    code                    VARCHAR(50) NOT NULL UNIQUE,
    arabic_symbol           VARCHAR(10) NOT NULL,
    arabic_name             VARCHAR(100) NOT NULL,
    unicode_codepoint       VARCHAR(20),
    category                vowel_category_enum NOT NULL,
    phonetic_weight         NUMERIC(6,3) NOT NULL CHECK (phonetic_weight >= 0),
    temporal_weight         NUMERIC(6,3) NOT NULL CHECK (temporal_weight >= 0),
    syllabic_role           syllabic_role_enum NOT NULL,
    morphological_role      morphological_role_enum NOT NULL DEFAULT 'neutral',
    syntactic_role          syntactic_role_enum NOT NULL DEFAULT 'none',
    closure_degree          NUMERIC(5,3) NOT NULL CHECK (closure_degree >= 0 AND closure_degree <= 1),
    openness_degree         NUMERIC(5,3) NOT NULL CHECK (openness_degree >= 0 AND openness_degree <= 1),
    articulatory_cost       NUMERIC(6,3) NOT NULL CHECK (articulatory_cost >= 0),
    perceptual_cost         NUMERIC(6,3) NOT NULL CHECK (perceptual_cost >= 0),
    can_lengthen            BOOLEAN NOT NULL DEFAULT FALSE,
    can_geminate            BOOLEAN NOT NULL DEFAULT FALSE,
    can_inflect             BOOLEAN NOT NULL DEFAULT FALSE,
    transition_class        VARCHAR(50),
    notes                   TEXT,
    CHECK (closure_degree + openness_degree <= 1.500)
);

CREATE INDEX IF NOT EXISTS idx_vowel_units_category ON vowel_units(category);
CREATE INDEX IF NOT EXISTS idx_vowel_units_symbol ON vowel_units(arabic_symbol);

-- =========================================================
-- 5. TABLE 3: syllable_patterns
-- =========================================================

CREATE TABLE IF NOT EXISTS syllable_patterns (
    id                      BIGSERIAL PRIMARY KEY,
    code                    VARCHAR(20) NOT NULL UNIQUE,
    arabic_name             VARCHAR(100) NOT NULL,
    shape_length            INTEGER NOT NULL CHECK (shape_length > 0),
    mora_count              NUMERIC(4,2) NOT NULL CHECK (mora_count > 0),
    closure_degree          NUMERIC(5,3) NOT NULL CHECK (closure_degree >= 0 AND closure_degree <= 1),
    articulatory_cost       NUMERIC(6,3) NOT NULL CHECK (articulatory_cost >= 0),
    perceptual_stability    NUMERIC(6,3) NOT NULL CHECK (perceptual_stability >= 0),
    allowed_initial         BOOLEAN NOT NULL DEFAULT TRUE,
    allowed_medial          BOOLEAN NOT NULL DEFAULT TRUE,
    allowed_final           BOOLEAN NOT NULL DEFAULT TRUE,
    notes                   TEXT
);

-- =========================================================
-- 6. TABLE 4: vowel_transitions
-- =========================================================

CREATE TABLE IF NOT EXISTS vowel_transitions (
    id                      BIGSERIAL PRIMARY KEY,
    from_vowel_id           BIGINT NOT NULL REFERENCES vowel_units(id) ON DELETE CASCADE,
    to_vowel_id             BIGINT NOT NULL REFERENCES vowel_units(id) ON DELETE CASCADE,
    transition_type         transition_type_enum NOT NULL,
    trigger_condition       TEXT,
    cost_delta              NUMERIC(6,3) NOT NULL DEFAULT 0,
    closure_delta           NUMERIC(6,3) NOT NULL DEFAULT 0,
    semantic_effect         VARCHAR(200),
    formal_rule             TEXT,
    valid_scope             transition_scope_enum NOT NULL DEFAULT 'word',
    UNIQUE(from_vowel_id, to_vowel_id, transition_type, valid_scope)
);

CREATE INDEX IF NOT EXISTS idx_vowel_transitions_from ON vowel_transitions(from_vowel_id);
CREATE INDEX IF NOT EXISTS idx_vowel_transitions_to ON vowel_transitions(to_vowel_id);

-- =========================================================
-- 7. TABLE 5: patterns
-- =========================================================

CREATE TABLE IF NOT EXISTS patterns (
    id                          BIGSERIAL PRIMARY KEY,
    code                        VARCHAR(50) NOT NULL UNIQUE,
    arabic_form                 VARCHAR(100) NOT NULL,
    transliteration             VARCHAR(100),
    pattern_family              pattern_family_enum NOT NULL,
    root_slots                  INTEGER NOT NULL CHECK (root_slots BETWEEN 2 AND 6),
    augmentation_slots          INTEGER NOT NULL DEFAULT 0 CHECK (augmentation_slots >= 0),
    abstract_template           JSONB NOT NULL,
    vocalic_signature           VARCHAR(100),
    closure_profile             NUMERIC(6,3) NOT NULL DEFAULT 0.500 CHECK (closure_profile >= 0 AND closure_profile <= 1),
    derivational_load           NUMERIC(6,3) NOT NULL DEFAULT 0.000 CHECK (derivational_load >= 0),
    inflectional_potential      NUMERIC(6,3) NOT NULL DEFAULT 0.000 CHECK (inflectional_potential >= 0),
    semantic_base_class         VARCHAR(100),
    usage_stability             NUMERIC(6,3) NOT NULL DEFAULT 1.000 CHECK (usage_stability >= 0),
    metaphor_transferability    NUMERIC(6,3) NOT NULL DEFAULT 0.000 CHECK (metaphor_transferability >= 0),
    cognitive_cost              NUMERIC(6,3) NOT NULL DEFAULT 1.000 CHECK (cognitive_cost >= 0),
    articulatory_cost           NUMERIC(6,3) NOT NULL DEFAULT 1.000 CHECK (articulatory_cost >= 0),
    notes                       TEXT
);

CREATE INDEX IF NOT EXISTS idx_patterns_family ON patterns(pattern_family);
CREATE INDEX IF NOT EXISTS idx_patterns_template ON patterns USING GIN (abstract_template);

-- =========================================================
-- 8. TABLE 6: pattern_augmentation_map
-- =========================================================

CREATE TABLE IF NOT EXISTS pattern_augmentation_map (
    id                      BIGSERIAL PRIMARY KEY,
    pattern_id              BIGINT NOT NULL REFERENCES patterns(id) ON DELETE CASCADE,
    augmentation_type_id    BIGINT NOT NULL REFERENCES augmentation_types(id),
    slot_position           INTEGER NOT NULL CHECK (slot_position > 0),
    position_type           position_type_enum NOT NULL,
    obligatory              BOOLEAN NOT NULL DEFAULT TRUE,
    cost_impact             NUMERIC(6,3) NOT NULL DEFAULT 0 CHECK (cost_impact >= 0),
    semantic_impact         VARCHAR(200),
    notes                   TEXT,
    UNIQUE(pattern_id, augmentation_type_id, slot_position, position_type)
);

CREATE INDEX IF NOT EXISTS idx_pattern_aug_map_pattern ON pattern_augmentation_map(pattern_id);

-- =========================================================
-- 9. TABLE 7: roots
-- =========================================================

CREATE TABLE IF NOT EXISTS roots (
    id                      BIGSERIAL PRIMARY KEY,
    code                    VARCHAR(50) NOT NULL UNIQUE,
    arabic_root             VARCHAR(20) NOT NULL,
    transliteration         VARCHAR(50),
    radical_count           INTEGER NOT NULL CHECK (radical_count BETWEEN 2 AND 6),
    semantic_base_class     VARCHAR(100),
    cognitive_capacity      NUMERIC(6,3) NOT NULL DEFAULT 1.000 CHECK (cognitive_capacity > 0),
    notes                   TEXT
);

-- =========================================================
-- 10. TABLE 8: root_segments
-- =========================================================

CREATE TABLE IF NOT EXISTS root_segments (
    id                      BIGSERIAL PRIMARY KEY,
    root_id                 BIGINT NOT NULL REFERENCES roots(id) ON DELETE CASCADE,
    radical_index           INTEGER NOT NULL CHECK (radical_index BETWEEN 1 AND 6),
    segment_id              BIGINT NOT NULL REFERENCES segment_units(id),
    position_weight         NUMERIC(6,3) NOT NULL DEFAULT 1.000 CHECK (position_weight >= 0),
    UNIQUE(root_id, radical_index)
);

CREATE INDEX IF NOT EXISTS idx_root_segments_root ON root_segments(root_id);
CREATE INDEX IF NOT EXISTS idx_root_segments_segment ON root_segments(segment_id);

-- =========================================================
-- 11. TABLE 9: pattern_slots
-- =========================================================

CREATE TABLE IF NOT EXISTS pattern_slots (
    id                      BIGSERIAL PRIMARY KEY,
    pattern_id              BIGINT NOT NULL REFERENCES patterns(id) ON DELETE CASCADE,
    slot_index              INTEGER NOT NULL CHECK (slot_index > 0),
    slot_kind               VARCHAR(20) NOT NULL CHECK (slot_kind IN ('root', 'vowel', 'augmentation', 'gemination', 'lengthening')),
    root_index              INTEGER CHECK (root_index IS NULL OR root_index BETWEEN 1 AND 6),
    vowel_id                BIGINT REFERENCES vowel_units(id),
    augmentation_type_id    BIGINT REFERENCES augmentation_types(id),
    gemination_target_index INTEGER CHECK (gemination_target_index IS NULL OR gemination_target_index BETWEEN 1 AND 6),
    obligatory              BOOLEAN NOT NULL DEFAULT TRUE,
    cost_impact             NUMERIC(6,3) NOT NULL DEFAULT 0.000 CHECK (cost_impact >= 0),
    notes                   TEXT,
    UNIQUE(pattern_id, slot_index),
    CHECK (
        (slot_kind = 'root' AND root_index IS NOT NULL AND vowel_id IS NULL AND augmentation_type_id IS NULL AND gemination_target_index IS NULL)
        OR
        (slot_kind = 'vowel' AND root_index IS NULL AND vowel_id IS NOT NULL AND augmentation_type_id IS NULL AND gemination_target_index IS NULL)
        OR
        (slot_kind = 'augmentation' AND root_index IS NULL AND vowel_id IS NULL AND augmentation_type_id IS NOT NULL AND gemination_target_index IS NULL)
        OR
        (slot_kind = 'lengthening' AND root_index IS NULL AND vowel_id IS NOT NULL AND augmentation_type_id IS NOT NULL AND gemination_target_index IS NULL)
        OR
        (slot_kind = 'gemination' AND root_index IS NULL AND vowel_id IS NULL AND augmentation_type_id IS NOT NULL AND gemination_target_index IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_pattern_slots_pattern ON pattern_slots(pattern_id);
CREATE INDEX IF NOT EXISTS idx_pattern_slots_kind ON pattern_slots(slot_kind);

-- =========================================================
-- 12. TABLE 10: root_pattern_scores
-- =========================================================

CREATE TABLE IF NOT EXISTS root_pattern_scores (
    id                      BIGSERIAL PRIMARY KEY,
    root_id                 BIGINT NOT NULL REFERENCES roots(id) ON DELETE CASCADE,
    pattern_id              BIGINT NOT NULL REFERENCES patterns(id) ON DELETE CASCADE,
    pattern_base_score      NUMERIC(9,4) NOT NULL,
    augmentation_fit        NUMERIC(9,4) NOT NULL,
    vocalic_fit             NUMERIC(9,4) NOT NULL,
    syllabic_balance        NUMERIC(9,4) NOT NULL,
    articulatory_cost       NUMERIC(9,4) NOT NULL,
    cognitive_cost          NUMERIC(9,4) NOT NULL,
    total_score             NUMERIC(9,4) NOT NULL,
    score_trace             JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(root_id, pattern_id)
);

CREATE INDEX IF NOT EXISTS idx_root_pattern_scores_total ON root_pattern_scores(total_score DESC);

-- =========================================================
-- 13. FUNCTION: score_root_pattern(root, pattern)
-- =========================================================

CREATE OR REPLACE FUNCTION score_root_pattern(p_root_id BIGINT, p_pattern_id BIGINT)
RETURNS TABLE (
    root_id             BIGINT,
    pattern_id          BIGINT,
    pattern_base_score  NUMERIC(9,4),
    augmentation_fit    NUMERIC(9,4),
    vocalic_fit         NUMERIC(9,4),
    syllabic_balance    NUMERIC(9,4),
    articulatory_cost   NUMERIC(9,4),
    cognitive_cost      NUMERIC(9,4),
    total_score         NUMERIC(9,4),
    score_trace         JSONB
)
LANGUAGE SQL
STABLE
AS $$
WITH selected_pattern AS (
    SELECT *
    FROM patterns
    WHERE id = p_pattern_id
),
selected_root AS (
    SELECT *
    FROM roots
    WHERE id = p_root_id
),
root_articulation AS (
    SELECT
        COALESCE(AVG(su.articulatory_cost), 0.000) AS avg_root_articulatory_cost
    FROM root_segments rs
    JOIN segment_units su ON su.id = rs.segment_id
    WHERE rs.root_id = p_root_id
),
augmentation_component AS (
    SELECT
        COALESCE(AVG(GREATEST(0::NUMERIC, 1 - ((pam.cost_impact + at.default_cost) / 2))), 1.000) AS augmentation_fit,
        COALESCE(SUM(pam.cost_impact + at.default_cost), 0.000) AS augmentation_total_cost
    FROM pattern_augmentation_map pam
    JOIN augmentation_types at ON at.id = pam.augmentation_type_id
    WHERE pam.pattern_id = p_pattern_id
),
vocalic_component AS (
    SELECT
        COALESCE(
            AVG((vu.phonetic_weight + vu.temporal_weight) / NULLIF(vu.articulatory_cost + vu.perceptual_cost, 0)),
            1.000
        ) AS vocalic_fit
    FROM pattern_slots ps
    JOIN vowel_units vu ON vu.id = ps.vowel_id
    WHERE ps.pattern_id = p_pattern_id
      AND ps.slot_kind IN ('vowel', 'lengthening')
),
syllabic_component AS (
    SELECT
        COALESCE(MAX(GREATEST(0::NUMERIC, 1 - ABS(sp.closure_degree - p.closure_profile))), 0.500) AS syllabic_balance
    FROM selected_pattern p
    CROSS JOIN syllable_patterns sp
),
components AS (
    SELECT
        r.id AS root_id,
        p.id AS pattern_id,
        ((p.usage_stability + p.derivational_load + p.inflectional_potential) / 3.0)::NUMERIC(9,4) AS pattern_base_score,
        a.augmentation_fit::NUMERIC(9,4) AS augmentation_fit,
        v.vocalic_fit::NUMERIC(9,4) AS vocalic_fit,
        s.syllabic_balance::NUMERIC(9,4) AS syllabic_balance,
        (
            p.articulatory_cost
            + ra.avg_root_articulatory_cost
            + (a.augmentation_total_cost * 0.100)
        )::NUMERIC(9,4) AS articulatory_cost,
        (
            p.cognitive_cost
            + (COALESCE(p.augmentation_slots, 0) * 0.100)
            + (1 / NULLIF(r.cognitive_capacity, 0))
        )::NUMERIC(9,4) AS cognitive_cost
    FROM selected_root r
    CROSS JOIN selected_pattern p
    CROSS JOIN root_articulation ra
    CROSS JOIN augmentation_component a
    CROSS JOIN vocalic_component v
    CROSS JOIN syllabic_component s
)
SELECT
    c.root_id,
    c.pattern_id,
    c.pattern_base_score,
    c.augmentation_fit,
    c.vocalic_fit,
    c.syllabic_balance,
    c.articulatory_cost,
    c.cognitive_cost,
    (
        c.pattern_base_score
        + c.augmentation_fit
        + c.vocalic_fit
        + c.syllabic_balance
        - c.articulatory_cost
        - c.cognitive_cost
    )::NUMERIC(9,4) AS total_score,
    jsonb_build_object(
        'pattern_base_score', c.pattern_base_score,
        'augmentation_fit', c.augmentation_fit,
        'vocalic_fit', c.vocalic_fit,
        'syllabic_balance', c.syllabic_balance,
        'articulatory_cost', c.articulatory_cost,
        'cognitive_cost', c.cognitive_cost
    ) AS score_trace
FROM components c;
$$;

-- =========================================================
-- 14. PHASE-1 (ADDITIVE) TYPES AND TABLES
-- =========================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'haraka_class_enum') THEN
        CREATE TYPE haraka_class_enum AS ENUM (
            'short',
            'sukun',
            'madd',
            'tanween',
            'shadda',
            'inflectional_primary',
            'inflectional_secondary'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'haraka_vowel_quality_enum') THEN
        CREATE TYPE haraka_vowel_quality_enum AS ENUM (
            'a',
            'i',
            'u',
            'zero',
            'long_a',
            'long_i',
            'long_u',
            'tanween_fath',
            'tanween_damm',
            'tanween_kasr'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'haraka_inflectional_role_enum') THEN
        CREATE TYPE haraka_inflectional_role_enum AS ENUM (
            'raf',
            'nasb',
            'jarr',
            'jazm',
            'none'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'haraka_derivational_role_enum') THEN
        CREATE TYPE haraka_derivational_role_enum AS ENUM (
            'original',
            'derivational',
            'augmentive',
            'transformational',
            'none'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'haraka_transition_type_enum') THEN
        CREATE TYPE haraka_transition_type_enum AS ENUM (
            'phonological',
            'morphological',
            'inflectional',
            'derivational'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'articulation_zone_enum') THEN
        CREATE TYPE articulation_zone_enum AS ENUM (
            'laryngeal',
            'pharyngeal',
            'uvular',
            'velar',
            'palatal',
            'alveolar',
            'dental',
            'labial',
            'nasal',
            'glide'
        );
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS haraka_units (
    id                          BIGSERIAL PRIMARY KEY,
    code                        VARCHAR(32) NOT NULL UNIQUE,
    name_ar                     VARCHAR(64) NOT NULL,
    class                       haraka_class_enum NOT NULL,
    vowel_quality               haraka_vowel_quality_enum NOT NULL,
    length_weight               NUMERIC(4,2) NOT NULL CHECK (length_weight >= 0 AND length_weight <= 3.00),
    closure_effect              NUMERIC(4,2) NOT NULL CHECK (closure_effect >= 0 AND closure_effect <= 1.00),
    openness_effect             NUMERIC(4,2) NOT NULL CHECK (openness_effect >= 0 AND openness_effect <= 1.00),
    inflectional_role           haraka_inflectional_role_enum NOT NULL DEFAULT 'none',
    derivational_role           haraka_derivational_role_enum NOT NULL DEFAULT 'none',
    phonological_cost           NUMERIC(5,2) NOT NULL CHECK (phonological_cost >= 0),
    cognitive_cost              NUMERIC(5,2) NOT NULL CHECK (cognitive_cost >= 0),
    can_combine_with_shadda     BOOLEAN NOT NULL DEFAULT FALSE,
    can_form_syllable_peak      BOOLEAN NOT NULL DEFAULT FALSE,
    transition_group            VARCHAR(32),
    notes                       TEXT
);

CREATE TABLE IF NOT EXISTS haraka_transitions (
    id                  BIGSERIAL PRIMARY KEY,
    from_haraka_id      BIGINT NOT NULL REFERENCES haraka_units(id) ON DELETE CASCADE,
    to_haraka_id        BIGINT NOT NULL REFERENCES haraka_units(id) ON DELETE CASCADE,
    transition_type     haraka_transition_type_enum NOT NULL,
    trigger_condition   TEXT,
    cost_delta          NUMERIC(5,2) NOT NULL DEFAULT 0,
    legality            BOOLEAN NOT NULL DEFAULT TRUE,
    proof_rule          VARCHAR(128),
    UNIQUE (from_haraka_id, to_haraka_id, transition_type)
);

CREATE TABLE IF NOT EXISTS phoneme_units (
    id                          BIGSERIAL PRIMARY KEY,
    symbol_ar                   VARCHAR(8) NOT NULL,
    unicode_repr                VARCHAR(32) NOT NULL,
    abstract_phoneme_code       VARCHAR(32) NOT NULL UNIQUE,
    articulation_place_rank     INTEGER NOT NULL CHECK (articulation_place_rank > 0),
    articulation_manner_rank    INTEGER NOT NULL CHECK (articulation_manner_rank > 0),
    voiced                      BOOLEAN NOT NULL DEFAULT FALSE,
    emphatic                    BOOLEAN NOT NULL DEFAULT FALSE,
    continuant                  BOOLEAN NOT NULL DEFAULT FALSE,
    root_eligible               BOOLEAN NOT NULL DEFAULT TRUE,
    augmentation_eligible       BOOLEAN NOT NULL DEFAULT TRUE,
    doubling_cost               NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (doubling_cost >= 0),
    adjacency_constraints       JSONB NOT NULL DEFAULT '{}'::jsonb,
    notes                       TEXT
);

ALTER TABLE articulation_places
    ADD COLUMN IF NOT EXISTS name_ar VARCHAR(64),
    ADD COLUMN IF NOT EXISTS rank_numeric INTEGER,
    ADD COLUMN IF NOT EXISTS zone articulation_zone_enum,
    ADD COLUMN IF NOT EXISTS openness_degree NUMERIC(4,2),
    ADD COLUMN IF NOT EXISTS effort_score NUMERIC(4,2);

COMMENT ON COLUMN articulation_places.name_ar IS 'التسمية العربية المكافئة لحقل arabic_name.';
COMMENT ON COLUMN articulation_places.rank_numeric IS 'رتبة رقمية معيارية للمخرج قابلة للحساب.';
COMMENT ON COLUMN articulation_places.zone IS 'النطاق التجريدي للمخرج ضمن تصنيف المرحلة الأولى.';
COMMENT ON COLUMN articulation_places.openness_degree IS 'درجة الانفتاح [0..1] للمخرج.';
COMMENT ON COLUMN articulation_places.effort_score IS 'درجة الجهد النطقي [0..1] للمخرج.';

COMMENT ON COLUMN haraka_units.length_weight IS 'وزن طولي معياري [0..3]: 0 سكون، 1 قصير، 2 مد، 3 حد علوي مركب.';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_articulation_places_openness_degree'
          AND conrelid = 'articulation_places'::regclass
    ) THEN
        ALTER TABLE articulation_places
            ADD CONSTRAINT chk_articulation_places_openness_degree
            CHECK (openness_degree IS NULL OR (openness_degree >= 0 AND openness_degree <= 1.00));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_articulation_places_effort_score'
          AND conrelid = 'articulation_places'::regclass
    ) THEN
        ALTER TABLE articulation_places
            ADD CONSTRAINT chk_articulation_places_effort_score
            CHECK (effort_score IS NULL OR (effort_score >= 0 AND effort_score <= 1.00));
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS syllable_templates (
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(32) NOT NULL UNIQUE,
    pattern_shape       VARCHAR(16) NOT NULL,
    mora_count          INTEGER NOT NULL CHECK (mora_count > 0),
    closure_degree      NUMERIC(4,2) NOT NULL CHECK (closure_degree >= 0 AND closure_degree <= 1.00),
    articulatory_cost   NUMERIC(5,2) NOT NULL CHECK (articulatory_cost >= 0),
    cognitive_cost      NUMERIC(5,2) NOT NULL CHECK (cognitive_cost >= 0),
    legality_rule       TEXT,
    notes               TEXT
);

CREATE TABLE IF NOT EXISTS syllable_instances (
    id                  BIGSERIAL PRIMARY KEY,
    template_id         BIGINT NOT NULL REFERENCES syllable_templates(id) ON DELETE CASCADE,
    onset_phoneme_id    BIGINT REFERENCES phoneme_units(id),
    nucleus_haraka_id   BIGINT NOT NULL REFERENCES haraka_units(id),
    coda_phoneme_id     BIGINT REFERENCES phoneme_units(id),
    instance_label      VARCHAR(64),
    legality            BOOLEAN NOT NULL DEFAULT TRUE,
    notes               TEXT
);

COMMIT;
