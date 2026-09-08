export interface AlternativeStore {
  id: string;
  name: string;
  type: string;
  type_label: string;
  badge_color: string;
  website: string;
  description: string;
  coverage: string;
  highlight: string;
}

export interface PriceOpportunity {
  id: string;
  product_name: string;
  category: 'carnes' | 'despensa' | 'frutas_verduras' | 'lacteos_huevos' | string;
  store_id: string;
  store_name: string;
  store_type: string;
  unit: string;
  alternative_price: number;
  unit_price_alternative: number;
  traditional_benchmark_price: number;
  benchmark_label: string;
  savings_clp: number;
  savings_percentage: number;
  deal_level: 'SUPER_AHORRO' | 'AHORRO_ALTO' | 'AHORRO_MODERADO';
  deal_label: string;
  is_wholesale: boolean;
  purchase_url: string;
  recommendation_note: string;
  image_url?: string;
}

export interface RadarKPIs {
  total_deals: number;
  avg_savings_pct: number;
  max_savings_pct: number;
  super_deals_count: number;
  monitored_stores_count: number;
}
