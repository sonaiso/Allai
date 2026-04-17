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

COMMIT;
