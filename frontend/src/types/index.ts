export interface SupermarketItemComparison {
  id: number;
  supermarket_id: number;
  supermarket_slug: 'lider' | 'jumbo' | 'santaisabel' | 'unimarc';
  supermarket_name: string;
  supermarket_color: string;
  sku: string;
  store_title: string;
  product_url: string;
  image_url?: string;
  package_quantity: number;
  package_unit: string;
  is_available: boolean;
  current_normal_price: number;
  current_offer_price?: number | null;
  current_unit_price_normalized: number; // $/kg o $/L
  is_current_offer: boolean;
  last_updated: string;
}

export interface CanonicalProductDetail {
  id: number;
  name: string;
  category: string;
  subcategory?: string | null;
  brand?: string | null;
  standard_unit: string; // 'kg' o 'L'
  description?: string | null;
  best_price_per_unit?: number | null;
  best_supermarket_name?: string | null;
  items: SupermarketItemComparison[];
}

export interface ProductSearchResult {
  id: number;
  name: string;
  category: string;
  subcategory?: string | null;
  brand?: string | null;
  standard_unit: string;
  min_unit_price: number;
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
}

export interface MiningStats {
  canonical_products_count: number;
  supermarket_skus_tracked: number;
  active_supermarkets: string[];
  commune_target: string;
}
