-- =========================================================
-- OFERTIS CHILE - RADAR ALTERNATIVO DATABASE SCHEMA
-- Persistencia de Supermercados Mayoristas y Canales Alternativos
-- =========================================================

-- 1. Tabla de Tiendas y Mercados Alternativos
CREATE TABLE IF NOT EXISTS alternative_stores (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    store_type VARCHAR(50) NOT NULL, -- 'CARNICERIA_DIRECTA', 'SUPERMERCADO_MAYORISTA', 'MERCADO_CONCENTRADOR', 'BODEGA_DESCUENTO', 'DISTRIBUIDORA_ALIMENTOS'
    type_label VARCHAR(100) NOT NULL,
    badge_color VARCHAR(20) DEFAULT 'blue',
    website VARCHAR(255) NOT NULL,
    description TEXT,
    coverage VARCHAR(255),
    highlight VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alt_stores_slug ON alternative_stores(slug);

-- 2. Tabla de Items / SKUs de Canales Alternativos
CREATE TABLE IF NOT EXISTS alternative_items (
    id SERIAL PRIMARY KEY,
    store_id INT NOT NULL REFERENCES alternative_stores(id) ON DELETE CASCADE,
    sku VARCHAR(150) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'carnes', 'despensa', 'frutas_verduras', 'lacteos_huevos'
    unit VARCHAR(100) NOT NULL, -- 'kg', 'L', 'unidad', 'bandeja', 'malla', 'fardo 10 kg'
    package_quantity NUMERIC(10,3) DEFAULT 1.000,
    package_unit VARCHAR(10) DEFAULT 'kg',
    current_price NUMERIC(12,2) NOT NULL, -- CLP
    unit_price_normalized NUMERIC(12,2) NOT NULL, -- CLP por kg o L
    benchmark_category_key VARCHAR(100),
    traditional_benchmark_price NUMERIC(12,2) NOT NULL,
    benchmark_label VARCHAR(150) NOT NULL,
    savings_clp NUMERIC(12,2) NOT NULL,
    savings_percentage NUMERIC(5,1) NOT NULL,
    deal_level VARCHAR(50) NOT NULL, -- 'SUPER_AHORRO', 'AHORRO_ALTO', 'AHORRO_MODERADO'
    deal_label VARCHAR(100) NOT NULL,
    is_wholesale BOOLEAN DEFAULT FALSE,
    purchase_url TEXT NOT NULL,
    recommendation_note TEXT,
    image_url TEXT,
    embedding vector(384),
    is_available BOOLEAN DEFAULT TRUE,
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(store_id, sku)
);

CREATE INDEX IF NOT EXISTS idx_alt_items_store ON alternative_items(store_id);
CREATE INDEX IF NOT EXISTS idx_alt_items_category ON alternative_items(category);
CREATE INDEX IF NOT EXISTS idx_alt_items_savings ON alternative_items(savings_percentage DESC);

-- Índice HNSW con similitud de coseno para búsqueda semántica vectorial
CREATE INDEX IF NOT EXISTS idx_alt_items_embedding_hnsw 
ON alternative_items USING hnsw (embedding vector_cosine_ops);

-- 3. Histórico de Precios de Canales Alternativos
CREATE TABLE IF NOT EXISTS alternative_price_records (
    id BIGSERIAL PRIMARY KEY,
    item_id INT NOT NULL REFERENCES alternative_items(id) ON DELETE CASCADE,
    price NUMERIC(12,2) NOT NULL,
    unit_price_normalized NUMERIC(12,2) NOT NULL,
    traditional_benchmark_price NUMERIC(12,2) NOT NULL,
    savings_percentage NUMERIC(5,1) NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alt_price_records_item_date 
ON alternative_price_records (item_id, recorded_at DESC);
