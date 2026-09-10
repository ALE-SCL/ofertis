export interface SupermarketItemComparison {
  id: number;
  supermarket_id: number;
  supermarket_slug: 'lider' | 'jumbo' | 'santaisabel' | 'unimarc' | string;
  supermarket_name: string;
  supermarket_color: string;
  sku: string;
  store_title: string;
  product_url: string;
  image_url?: string;
  package_quantity: number;
  package_unit: string;
  package_format?: string;
  is_available: boolean;
  current_normal_price: number;
  current_offer_price?: number | null;
  current_package_price: number; // Precio real a pagar por el formato
  current_unit_price_normalized: number; // $/kg o $/L de referencia
  is_current_offer: boolean;
  is_cheapest?: boolean;
  last_updated: string;
}

export interface CanonicalProductDetail {
  id: number;
  name: string;
  category: string;
  subcategory?: string | null;
  brand?: string | null;
  standard_unit: string; // 'kg', 'L', 'un'
  package_format?: string;
  description?: string | null;
  best_package_price?: number | null;
  highest_package_price?: number | null;
  savings_amount?: number | null;
  savings_percentage?: number | null;
  best_price_per_unit?: number | null;
  best_supermarket_name?: string | null;
  best_supermarket_slug?: string | null;
  items: SupermarketItemComparison[];
}

export interface ProductSearchResult {
  id: number;
  name: string;
  category: string;
  subcategory?: string | null;
  brand?: string | null;
  package_format: string; // Formato real ej: '250 g', '500 cc', '12 un', '1 kg'
  standard_unit: string; // 'kg', 'L', 'un'
  best_package_price: number; // Precio real a pagar por el formato
  highest_package_price: number; // Precio en la tienda más cara
  savings_amount: number; // Ahorro en pesos
  savings_percentage: number; // % de ahorro
  min_unit_price: number; // $/kg o $/L de referencia
  max_unit_price: number;
  best_supermarket_slug: string;
  best_supermarket_name: string;
  available_supermarkets: string[];
  similarity_score?: number;
  image_url?: string;
}

export interface CategoryItem {
  slug: string;
  name: string;
  icon: string;
  count?: number;
}

export interface MiningStats {
  canonical_products_count: number;
  supermarket_skus_tracked: number;
  active_supermarkets: string[];
  commune_target: string;
}
