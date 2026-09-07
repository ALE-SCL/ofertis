-- =========================================================
-- OFERTIS CHILE - DATABASE INITIALIZATION & SCHEMA DDL
-- Multi-Agente, pgvector & Ontología de Canasta Básica
-- =========================================================

-- 1. Habilitar extensión vectorial pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Tabla de Supermercados Chilenos
CREATE TABLE IF NOT EXISTS supermarkets (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL, -- 'lider', 'jumbo', 'santaisabel', 'unimarc'
    name VARCHAR(100) NOT NULL,
    base_url VARCHAR(255) NOT NULL,
    color_hex VARCHAR(7) DEFAULT '#3B82F6', -- Color de marca para el UI
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Tabla de Productos Canónicos (Entidad abstracta normalizada)
CREATE TABLE IF NOT EXISTS canonical_products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL, -- ej: 'Lomo Liso Vacuno' o 'Arroz Grado 1'
    category VARCHAR(50) NOT NULL, -- 'carne_vacuno', 'carne_cerdo', 'carne_pollo', 'leche', 'arroz', 'fideos'
    subcategory VARCHAR(50), -- 'lomo_liso', 'entera', 'descremada', 'grado_1', 'spaghetti'
    brand VARCHAR(100), -- 'Tucapel', 'Colun', 'Carozzi', 'Agrosuper', 'Generica'
    standard_unit VARCHAR(10) NOT NULL, -- 'kg' o 'L'
    description TEXT,
    embedding vector(384), -- Vector denso generado con MiniLM-L12 multilingüe
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice HNSW con similitud de coseno para búsqueda semántica ultrarrápida
CREATE INDEX IF NOT EXISTS canonical_products_embedding_hnsw 
ON canonical_products USING hnsw (embedding vector_cosine_ops);

-- Índice para acelerar filtros de categoría
CREATE INDEX IF NOT EXISTS idx_canonical_category 
ON canonical_products (category);

-- 4. Tabla de Items Específicos por Supermercado (SKUs de tienda)
CREATE TABLE IF NOT EXISTS supermarket_items (
    id SERIAL PRIMARY KEY,
    canonical_id INT REFERENCES canonical_products(id) ON DELETE SET NULL,
    supermarket_id INT NOT NULL REFERENCES supermarkets(id) ON DELETE CASCADE,
    sku VARCHAR(100) NOT NULL,
    store_title VARCHAR(255) NOT NULL,
    brand_extracted VARCHAR(100),
    product_url TEXT NOT NULL,
    image_url TEXT,
    package_quantity NUMERIC(10,3) NOT NULL, -- ej: 0.400 para paquete de 400g, 1.000 para 1kg
    package_unit VARCHAR(10) NOT NULL, -- 'kg', 'g', 'L', 'ml'
    is_available BOOLEAN DEFAULT TRUE,
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(supermarket_id, sku)
);

CREATE INDEX IF NOT EXISTS idx_items_canonical 
ON supermarket_items(canonical_id);

-- 5. Histórico de Precios (Time-Series de precios por SKU)
CREATE TABLE IF NOT EXISTS price_records (
    id BIGSERIAL PRIMARY KEY,
    item_id INT NOT NULL REFERENCES supermarket_items(id) ON DELETE CASCADE,
    normal_price NUMERIC(12,2) NOT NULL, -- Precio lista en CLP
    offer_price NUMERIC(12,2), -- Precio con oferta o descuento en CLP
    unit_price_normalized NUMERIC(12,2) NOT NULL, -- Precio por kg o L en CLP
    is_offer BOOLEAN DEFAULT FALSE,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_price_records_item_date 
ON price_records (item_id, recorded_at DESC);

-- 6. Suscripciones de Alerta para Usuarios vía WhatsApp
CREATE TABLE IF NOT EXISTS user_alerts (
    id SERIAL PRIMARY KEY,
    user_phone VARCHAR(25) NOT NULL, -- Teléfono en formato E.164 (ej: +56912345678)
    user_name VARCHAR(100) DEFAULT 'Usuario',
    canonical_id INT NOT NULL REFERENCES canonical_products(id) ON DELETE CASCADE,
    target_unit_price NUMERIC(12,2) NOT NULL, -- Disparar si el precio/kg o precio/L es menor o igual
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_canonical 
ON user_alerts (canonical_id) WHERE is_active = TRUE;

-- 7. Log de Notificaciones de Alerta Enviadas
CREATE TABLE IF NOT EXISTS notification_logs (
    id BIGSERIAL PRIMARY KEY,
    alert_id INT REFERENCES user_alerts(id) ON DELETE SET NULL,
    recipient_phone VARCHAR(25) NOT NULL,
    message_content TEXT NOT NULL,
    provider VARCHAR(50) NOT NULL, -- 'mock', 'twilio_sandbox', 'meta_cloud'
    status VARCHAR(30) NOT NULL, -- 'sent', 'delivered', 'failed', 'simulated'
    dispatched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
