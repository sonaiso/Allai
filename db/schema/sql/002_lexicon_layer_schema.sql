BEGIN;

-- =========================================================
-- 002_LEXICON_LAYER_SCHEMA
-- طبقة المعجم: الاستيراد على طبقات
--
-- الهيكل:
--   RawLexicon → BuiltInventory + InflectedInventory
--                     ↓
--               Operators (حركات + زوائد + موقع + وزن + سياق)
--                     ↓
--               ExceptionClasses (وحدات خاصة)
--                     ↓
--               FinalAnalysis
--
-- جدول البحث الموحد:
--   EntryType + Pattern + Zawaid + Harakat + ExceptionClass
--   → FinalAnalysis
-- =========================================================

-- =========================================================
-- 1. ENUM TYPES — طبقة المعجم
-- =========================================================

DO $$
BEGIN

    -- نوع المدخل المعجمي
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'entry_type_enum') THEN
        CREATE TYPE entry_type_enum AS ENUM (
            'tool',                 -- أداة
            'pronoun',              -- ضمير
            'demonstrative',        -- اسم إشارة
            'relative',             -- موصول
            'conditional',          -- اسم شرط
            'interrogative',        -- اسم استفهام
            'verbal_noun',          -- اسم فعل
            'past_verb_bare',       -- فعل ماضٍ مجرد
            'past_verb_augmented',  -- فعل ماضٍ مزيد
            'imperative_verb',      -- فعل أمر
            'frozen_noun',          -- اسم جامد
            'trilateral_root',      -- جذر ثلاثي
            'quadrilateral_root',   -- جذر رباعي
            'present_verb',         -- فعل مضارع
            'derived_noun'          -- اسم مشتق
        );
    END IF;

    -- فئة الإعراب / البناء
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'inflection_class_enum') THEN
        CREATE TYPE inflection_class_enum AS ENUM (
            'mabni',                -- مبني (لا يتغير)
            'murab_full',           -- معرب كامل
            'murab_partial'         -- معرب ناقص (ممنوع من الصرف)
        );
    END IF;

    -- الجنس النحوي
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'grammatical_gender_enum') THEN
        CREATE TYPE grammatical_gender_enum AS ENUM (
            'masculine',
            'feminine',
            'common'
        );
    END IF;

    -- العدد النحوي
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'grammatical_number_enum') THEN
        CREATE TYPE grammatical_number_enum AS ENUM (
            'singular',
            'dual',
            'sound_masculine_plural',   -- جمع مذكر سالم
            'sound_feminine_plural',    -- جمع مؤنث سالم
            'broken_plural'             -- جمع تكسير
        );
    END IF;

    -- الإعراب (علامة الإعراب)
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'case_role_enum') THEN
        CREATE TYPE case_role_enum AS ENUM (
            'raf',      -- رفع
            'nasb',     -- نصب
            'jarr',     -- جر
            'jazm',     -- جزم
            'bina',     -- بناء (لا محل)
            'none'
        );
    END IF;

    -- نوع علامة الإعراب
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'case_marker_kind_enum') THEN
        CREATE TYPE case_marker_kind_enum AS ENUM (
            'haraka',           -- حركة (ضمة / فتحة / كسرة / سكون)
            'letter_waw',       -- واو (جمع مذكر سالم / أسماء خمسة)
            'letter_alif',      -- ألف (مثنى / أسماء خمسة)
            'letter_ya',        -- ياء (مثنى / جمع مذكر سالم / أسماء خمسة)
            'letter_nun_thabut',-- ثبوت النون (أفعال خمسة)
            'letter_nun_hadhf', -- حذف النون (أفعال خمسة)
            'none'
        );
    END IF;

    -- الزمن الصرفي
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tense_enum') THEN
        CREATE TYPE tense_enum AS ENUM (
            'past',
            'present',
            'imperative',
            'none'
        );
    END IF;

    -- التعدية / اللزوم
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transitivity_enum') THEN
        CREATE TYPE transitivity_enum AS ENUM (
            'transitive',       -- متعدٍّ
            'intransitive',     -- لازم
            'both',
            'none'
        );
    END IF;

    -- التعريف / النكرة
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'definiteness_enum') THEN
        CREATE TYPE definiteness_enum AS ENUM (
            'definite',         -- معرفة
            'indefinite',       -- نكرة
            'proper_noun',      -- علم
            'none'
        );
    END IF;

    -- نوع الوحدة الخاصة (صنف الاستثناء)
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'exception_class_enum') THEN
        CREATE TYPE exception_class_enum AS ENUM (
            'pronoun',                  -- الضمائر
            'demonstrative_relative',   -- أسماء الإشارة والموصول والشرط والاستفهام
            'diptote',                  -- الممنوع من الصرف
            'five_nouns',               -- الأسماء الخمسة
            'dual',                     -- المثنى
            'sound_masc_plural',        -- جمع المذكر السالم
            'five_verbs',               -- الأفعال الخمسة
            'defective_hamza_doubled',  -- المعتل والمهموز والمضعف
            'diminutive_nisba',         -- التصغير والنسب
            'broken_plural',            -- جمع التكسير
            'masdar',                   -- المصادر
            'pause_script'              -- الوقف والابتداء والرسم
        );
    END IF;

    -- نوع المشغّل
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'operator_type_enum') THEN
        CREATE TYPE operator_type_enum AS ENUM (
            'haraka',       -- حركات
            'zawaid',       -- الزوائد العشرة
            'position',     -- الموقع
            'pattern',      -- الوزن
            'context'       -- السياق
        );
    END IF;

END
$$;

-- =========================================================
-- 2. TABLE: lexicon_entries — المعجم الخام
--    الطبقة الأولى من الاستيراد
-- =========================================================

CREATE TABLE IF NOT EXISTS lexicon_entries (
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(80)  NOT NULL UNIQUE,
    arabic_form         VARCHAR(200) NOT NULL,
    transliteration     VARCHAR(200),
    entry_type          entry_type_enum        NOT NULL,
    inflection_class    inflection_class_enum  NOT NULL,
    gender_default      grammatical_gender_enum NOT NULL DEFAULT 'common',
    semantic_class      VARCHAR(100),
    cognitive_load      NUMERIC(5,3) NOT NULL DEFAULT 1.000 CHECK (cognitive_load >= 0),
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lexicon_entries_type
    ON lexicon_entries (entry_type);
CREATE INDEX IF NOT EXISTS idx_lexicon_entries_inflection
    ON lexicon_entries (inflection_class);
CREATE INDEX IF NOT EXISTS idx_lexicon_entries_form
    ON lexicon_entries (arabic_form);

-- =========================================================
-- 3. TABLE: built_inventory — المبنيات
--    أدوات / ضمائر / أسماء إشارة / موصولات / شرط / استفهام /
--    أسماء أفعال / أفعال ماضية / أمر
-- =========================================================

CREATE TABLE IF NOT EXISTS built_inventory (
    id                  BIGSERIAL PRIMARY KEY,
    entry_id            BIGINT NOT NULL REFERENCES lexicon_entries(id) ON DELETE CASCADE,
    sub_type            entry_type_enum NOT NULL,
    -- متصل / منفصل للضمائر، حر / مقيد للأدوات
    attachment_type     VARCHAR(20) NOT NULL DEFAULT 'free'
                            CHECK (attachment_type IN ('free', 'attached', 'both')),
    -- وظيفة الربط / الإحالة (للموصولات وما شابهها)
    reference_function  VARCHAR(100),
    -- الشكل المبني الصرف (لا يتغير بالإعراب)
    fixed_form          VARCHAR(200) NOT NULL,
    -- موقع البناء (في محل رفع / نصب / جر / لا محل)
    syntactic_slot      VARCHAR(50),
    notes               TEXT,
    UNIQUE (entry_id)
);

CREATE INDEX IF NOT EXISTS idx_built_inventory_entry
    ON built_inventory (entry_id);
CREATE INDEX IF NOT EXISTS idx_built_inventory_subtype
    ON built_inventory (sub_type);

-- =========================================================
-- 4. TABLE: inflected_inventory — المعربات الخام
--    أسماء جامدة / جذور / مضارع / مشتقات
-- =========================================================

CREATE TABLE IF NOT EXISTS inflected_inventory (
    id                  BIGSERIAL PRIMARY KEY,
    entry_id            BIGINT NOT NULL REFERENCES lexicon_entries(id) ON DELETE CASCADE,
    -- ربط اختياري بالجذر الصرفي (من جدول roots في الطبقة الصوتية)
    root_id             BIGINT REFERENCES roots(id),
    -- ربط اختياري بالوزن الصرفي (من جدول patterns)
    pattern_id          BIGINT REFERENCES patterns(id),
    radical_count       INTEGER CHECK (radical_count IS NULL OR radical_count BETWEEN 2 AND 6),
    -- الصيغة المجردة قبل دخول الجوازم والنواصب والتصريف
    bare_form           VARCHAR(200) NOT NULL,
    gender_default      grammatical_gender_enum NOT NULL DEFAULT 'masculine',
    -- هل يقبل التنوين في النكرة؟
    accepts_tanween     BOOLEAN NOT NULL DEFAULT TRUE,
    notes               TEXT,
    UNIQUE (entry_id)
);

CREATE INDEX IF NOT EXISTS idx_inflected_inventory_entry
    ON inflected_inventory (entry_id);
CREATE INDEX IF NOT EXISTS idx_inflected_inventory_root
    ON inflected_inventory (root_id);
CREATE INDEX IF NOT EXISTS idx_inflected_inventory_pattern
    ON inflected_inventory (pattern_id);

-- =========================================================
-- 5. TABLE: exception_classes — الوحدات الخاصة
--    الوحدات التي تحتاج معالجة استثنائية
-- =========================================================

CREATE TABLE IF NOT EXISTS exception_classes (
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(60) NOT NULL UNIQUE,
    name_ar             VARCHAR(100) NOT NULL,
    exception_type      exception_class_enum NOT NULL,
    -- وصف السلوك الاستثنائي
    behavior_desc       TEXT NOT NULL,
    -- قاعدة التعرف (تعبير نمطي أو وصف رسمي)
    rule_tag            VARCHAR(200),
    -- درجة التعقيد الإعرابي [0..1]
    complexity_score    NUMERIC(4,3) NOT NULL DEFAULT 0.500
                            CHECK (complexity_score >= 0 AND complexity_score <= 1),
    notes               TEXT
);

CREATE INDEX IF NOT EXISTS idx_exception_classes_type
    ON exception_classes (exception_type);

-- =========================================================
-- 6. TABLE: lexicon_exception_map — ربط المدخل بصنف الاستثناء
-- =========================================================

CREATE TABLE IF NOT EXISTS lexicon_exception_map (
    id                  BIGSERIAL PRIMARY KEY,
    entry_id            BIGINT NOT NULL REFERENCES lexicon_entries(id) ON DELETE CASCADE,
    exception_class_id  BIGINT NOT NULL REFERENCES exception_classes(id) ON DELETE CASCADE,
    priority            INTEGER NOT NULL DEFAULT 1 CHECK (priority > 0),
    notes               TEXT,
    UNIQUE (entry_id, exception_class_id)
);

CREATE INDEX IF NOT EXISTS idx_lex_exc_map_entry
    ON lexicon_exception_map (entry_id);
CREATE INDEX IF NOT EXISTS idx_lex_exc_map_class
    ON lexicon_exception_map (exception_class_id);

-- =========================================================
-- 7. TABLE: operators — المشغّلات
--    حركات + الزوائد العشرة + الموقع + الوزن + السياق
-- =========================================================

CREATE TABLE IF NOT EXISTS operators (
    id                  BIGSERIAL PRIMARY KEY,
    code                VARCHAR(80) NOT NULL UNIQUE,
    name_ar             VARCHAR(100) NOT NULL,
    operator_type       operator_type_enum NOT NULL,
    -- أنواع المدخلات التي ينطبق عليها هذا المشغّل
    applies_to          entry_type_enum[],
    -- أثر المشغّل: قائمة من السمات المُولَّدة
    generates           VARCHAR(200)[],
    -- الصيغة الرسمية للقاعدة (نص أو تعبير)
    rule_formula        TEXT,
    -- الأولوية عند تعارض المشغّلات
    priority            INTEGER NOT NULL DEFAULT 10 CHECK (priority > 0),
    -- ربط اختياري بوحدة حركة من الطبقة الصوتية
    haraka_unit_id      BIGINT REFERENCES haraka_units(id),
    -- ربط اختياري بنوع زيادة من جدول augmentation_types
    augmentation_type_id BIGINT REFERENCES augmentation_types(id),
    notes               TEXT
);

CREATE INDEX IF NOT EXISTS idx_operators_type
    ON operators (operator_type);
CREATE INDEX IF NOT EXISTS idx_operators_applies
    ON operators USING GIN (applies_to);

-- =========================================================
-- 8. TABLE: operator_results — نتائج تطبيق المشغّلات
--    السمات المُولَّدة لكل مدخل بعد تطبيق المشغّلات
-- =========================================================

CREATE TABLE IF NOT EXISTS operator_results (
    id                  BIGSERIAL PRIMARY KEY,
    entry_id            BIGINT NOT NULL REFERENCES lexicon_entries(id) ON DELETE CASCADE,
    operator_id         BIGINT NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    definiteness        definiteness_enum        NOT NULL DEFAULT 'none',
    gender              grammatical_gender_enum  NOT NULL DEFAULT 'common',
    number              grammatical_number_enum  NOT NULL DEFAULT 'singular',
    case_role           case_role_enum           NOT NULL DEFAULT 'none',
    case_marker_kind    case_marker_kind_enum    NOT NULL DEFAULT 'none',
    tense               tense_enum               NOT NULL DEFAULT 'none',
    transitivity        transitivity_enum        NOT NULL DEFAULT 'none',
    -- الشكل السطحي المُولَّد
    surface_form        VARCHAR(300) NOT NULL,
    -- درجة الموثوقية [0..1]
    confidence          NUMERIC(4,3) NOT NULL DEFAULT 1.000
                            CHECK (confidence >= 0 AND confidence <= 1),
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (entry_id, operator_id, definiteness, gender, number, case_role, tense)
);

CREATE INDEX IF NOT EXISTS idx_operator_results_entry
    ON operator_results (entry_id);
CREATE INDEX IF NOT EXISTS idx_operator_results_surface
    ON operator_results (surface_form);
CREATE INDEX IF NOT EXISTS idx_operator_results_case
    ON operator_results (case_role);

-- =========================================================
-- 9. TABLE: final_analysis — جدول البحث الموحّد
--    EntryType + Pattern + Zawaid + Harakat + ExceptionClass
--    → FinalAnalysis
-- =========================================================

CREATE TABLE IF NOT EXISTS final_analysis (
    id                      BIGSERIAL PRIMARY KEY,
    -- مفاتيح الاستعلام
    entry_id                BIGINT NOT NULL REFERENCES lexicon_entries(id) ON DELETE CASCADE,
    entry_type              entry_type_enum       NOT NULL,
    pattern_id              BIGINT REFERENCES patterns(id),
    augmentation_type_id    BIGINT REFERENCES augmentation_types(id),
    haraka_unit_id          BIGINT REFERENCES haraka_units(id),
    exception_class_id      BIGINT REFERENCES exception_classes(id),
    -- المحاور الإعرابية
    definiteness            definiteness_enum         NOT NULL DEFAULT 'none',
    gender                  grammatical_gender_enum   NOT NULL DEFAULT 'common',
    number                  grammatical_number_enum   NOT NULL DEFAULT 'singular',
    case_role               case_role_enum            NOT NULL DEFAULT 'none',
    case_marker_kind        case_marker_kind_enum     NOT NULL DEFAULT 'none',
    tense                   tense_enum                NOT NULL DEFAULT 'none',
    transitivity            transitivity_enum         NOT NULL DEFAULT 'none',
    -- الشكل السطحي النهائي
    final_surface_form      VARCHAR(300) NOT NULL,
    -- أثر البناء / الإعراب
    bina_or_irab            VARCHAR(20) NOT NULL DEFAULT 'irab'
                                CHECK (bina_or_irab IN ('bina', 'irab')),
    -- أثر الوقف / الرسم (الطبقة السطحية الأخيرة)
    pause_form              VARCHAR(300),
    -- تتبع مسار التحليل
    analysis_trace          JSONB NOT NULL DEFAULT '{}'::JSONB,
    -- درجة الثقة الكلية [0..1]
    confidence              NUMERIC(4,3) NOT NULL DEFAULT 1.000
                                CHECK (confidence >= 0 AND confidence <= 1),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (
        entry_id,
        entry_type,
        COALESCE(pattern_id,            -1),
        COALESCE(augmentation_type_id,  -1),
        COALESCE(haraka_unit_id,        -1),
        COALESCE(exception_class_id,    -1),
        definiteness,
        gender,
        number,
        case_role,
        tense
    )
);

CREATE INDEX IF NOT EXISTS idx_final_analysis_entry
    ON final_analysis (entry_id);
CREATE INDEX IF NOT EXISTS idx_final_analysis_entry_type
    ON final_analysis (entry_type);
CREATE INDEX IF NOT EXISTS idx_final_analysis_surface
    ON final_analysis (final_surface_form);
CREATE INDEX IF NOT EXISTS idx_final_analysis_case
    ON final_analysis (case_role, case_marker_kind);
CREATE INDEX IF NOT EXISTS idx_final_analysis_exception
    ON final_analysis (exception_class_id);
CREATE INDEX IF NOT EXISTS idx_final_analysis_trace
    ON final_analysis USING GIN (analysis_trace);

-- =========================================================
-- 10. VIEW: lexicon_full_view — عرض موحّد للمعجم الكامل
-- =========================================================

CREATE OR REPLACE VIEW lexicon_full_view AS
SELECT
    le.id                   AS entry_id,
    le.code                 AS entry_code,
    le.arabic_form,
    le.entry_type,
    le.inflection_class,
    le.gender_default,
    le.semantic_class,
    -- من المبنيات
    bi.sub_type             AS built_sub_type,
    bi.attachment_type,
    bi.fixed_form,
    bi.reference_function,
    -- من المعربات
    ii.root_id,
    ii.pattern_id,
    ii.bare_form,
    ii.accepts_tanween,
    -- أصناف الاستثناء (مجمّعة)
    ARRAY_AGG(DISTINCT ec.exception_type ORDER BY ec.exception_type) FILTER (
        WHERE ec.exception_type IS NOT NULL
    )                       AS exception_types,
    ARRAY_AGG(DISTINCT ec.code ORDER BY ec.code) FILTER (
        WHERE ec.code IS NOT NULL
    )                       AS exception_codes
FROM lexicon_entries le
LEFT JOIN built_inventory     bi  ON bi.entry_id  = le.id
LEFT JOIN inflected_inventory ii  ON ii.entry_id  = le.id
LEFT JOIN lexicon_exception_map lem ON lem.entry_id = le.id
LEFT JOIN exception_classes   ec  ON ec.id        = lem.exception_class_id
GROUP BY
    le.id, le.code, le.arabic_form, le.entry_type,
    le.inflection_class, le.gender_default, le.semantic_class,
    bi.sub_type, bi.attachment_type, bi.fixed_form, bi.reference_function,
    ii.root_id, ii.pattern_id, ii.bare_form, ii.accepts_tanween;

COMMENT ON VIEW lexicon_full_view IS
    'عرض موحّد يجمع بين المعجم الخام والمبنيات والمعربات وأصناف الاستثناء.';

-- =========================================================
-- 11. FUNCTION: resolve_final_analysis
--     دالة البحث الموحّد: EntryType + Pattern + Zawaid +
--     Harakat + ExceptionClass → FinalAnalysis
-- =========================================================

CREATE OR REPLACE FUNCTION resolve_final_analysis(
    p_entry_id              BIGINT,
    p_pattern_id            BIGINT      DEFAULT NULL,
    p_augmentation_type_id  BIGINT      DEFAULT NULL,
    p_haraka_unit_id        BIGINT      DEFAULT NULL,
    p_exception_class_id    BIGINT      DEFAULT NULL,
    p_definiteness          definiteness_enum         DEFAULT 'none',
    p_gender                grammatical_gender_enum   DEFAULT 'common',
    p_number                grammatical_number_enum   DEFAULT 'singular',
    p_case_role             case_role_enum            DEFAULT 'none',
    p_tense                 tense_enum                DEFAULT 'none'
)
RETURNS TABLE (
    entry_id                BIGINT,
    entry_type              entry_type_enum,
    final_surface_form      VARCHAR(300),
    case_marker_kind        case_marker_kind_enum,
    bina_or_irab            VARCHAR(20),
    pause_form              VARCHAR(300),
    confidence              NUMERIC(4,3),
    analysis_trace          JSONB
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        fa.entry_id,
        fa.entry_type,
        fa.final_surface_form,
        fa.case_marker_kind,
        fa.bina_or_irab,
        fa.pause_form,
        fa.confidence,
        fa.analysis_trace
    FROM final_analysis fa
    WHERE fa.entry_id               = p_entry_id
      AND (p_pattern_id           IS NULL OR fa.pattern_id           = p_pattern_id)
      AND (p_augmentation_type_id IS NULL OR fa.augmentation_type_id = p_augmentation_type_id)
      AND (p_haraka_unit_id       IS NULL OR fa.haraka_unit_id       = p_haraka_unit_id)
      AND (p_exception_class_id   IS NULL OR fa.exception_class_id   = p_exception_class_id)
      AND fa.definiteness          = p_definiteness
      AND fa.gender                = p_gender
      AND fa.number                = p_number
      AND fa.case_role             = p_case_role
      AND fa.tense                 = p_tense
    ORDER BY fa.confidence DESC
    LIMIT 10;
$$;

COMMENT ON FUNCTION resolve_final_analysis IS
    'دالة البحث الموحّد في جدول final_analysis بحسب:
     EntryType + Pattern + Zawaid + Harakat + ExceptionClass → FinalAnalysis';

COMMIT;
