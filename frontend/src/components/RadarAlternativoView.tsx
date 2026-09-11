import React, { useState, useEffect } from 'react';
import { 
  Target, 
  Search, 
  Store, 
  Percent, 
  Flame, 
  Award, 
  ShoppingBag, 
  AlertCircle, 
  Layers, 
  Sparkles,
  ExternalLink,
  CheckCircle2,
  Coins
} from 'lucide-react';
import { PriceOpportunity, AlternativeStore, RadarKPIs } from '../types/radar';
import { radarService } from '../services/radarService';
import { RadarProductCard } from './RadarProductCard';

export function RadarAlternativoView() {
  const [opportunities, setOpportunities] = useState<PriceOpportunity[]>([]);
  const [stores, setStores] = useState<AlternativeStore[]>([]);
  const [kpis, setKpis] = useState<RadarKPIs | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('todos');
  const [selectedStore, setSelectedStore] = useState<string>('todas');
  const [query, setQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedComparisonOpp, setSelectedComparisonOpp] = useState<PriceOpportunity | null>(null);

  const loadData = async (cat: string, searchTerm: string, storeSlug: string = selectedStore) => {
    setLoading(true);
    try {
      const [oppsData, storesData, kpisData] = await Promise.all([
        radarService.getOpportunities(cat, searchTerm, storeSlug),
        radarService.getStores(),
        radarService.getKpis()
      ]);
      setOpportunities(oppsData);
      setStores(storesData);
      setKpis(kpisData);
    } catch (err) {
      console.error('Error cargando RadarAlternativo:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(selectedCategory, query, selectedStore);
  }, [selectedCategory, selectedStore]);

  const onSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData(selectedCategory, query, selectedStore);
  };

  const handleSuggestionClick = (term: string) => {
    setQuery(term);
    loadData(selectedCategory, term, selectedStore);
  };

  const categories = [
    { id: 'todos', label: 'Todos los Canales (12 Tiendas)', icon: Target },
    { id: 'carnes', label: 'Carnicerías Directas (El Carnicero, Doña Carne, Castro)', icon: Flame },
    { id: 'despensa', label: 'Mayoristas y Despensa (Alvi, Central, aCuenta, Teba, Santiago)', icon: ShoppingBag },
    { id: 'frutas_verduras', label: 'Frutas y Verduras (Lo Valledor)', icon: Layers },
    { id: 'lacteos_huevos', label: 'Huevos y Lácteos', icon: Sparkles },
  ];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Hero & Buscador de Radar Alternativo */}
      <div className="bg-white dark:bg-stone-900 rounded-3xl p-6 sm:p-8 border border-orange-100/80 dark:border-stone-800 shadow-xs relative overflow-hidden transition-colors">
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 bg-orange-50 dark:bg-orange-950/60 text-orange-900 dark:text-orange-300 px-3.5 py-1.5 rounded-full text-xs font-bold border border-orange-200/80 dark:border-orange-800 mb-3 shadow-xs">
            <Coins className="w-3.5 h-3.5 text-orange-600" />
            <span>Canales alternativos y distribuidores mayoristas</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-black text-stone-900 dark:text-stone-100 tracking-tight">
            Compara precios entre distribuidores y supermercados mayoristas
          </h1>

          <p className="text-sm sm:text-base text-stone-600 dark:text-stone-400 mt-2">
            Compara precios en tiempo real entre canales mayoristas, carnicerías directas y bodegas (Alvi, Central Mayorista, Mayorista 10, SuperBodega aCuenta, Doña Carne, El Carnicero y Lo Valledor).
          </p>

          {/* Formulario de Búsqueda */}
          <form onSubmit={onSearchSubmit} className="mt-6 flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-5 h-5 text-stone-400 absolute left-4 top-3.5" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Busca por corte, producto o tienda (ej: 'lomo liso', 'Doña Carne', 'Alvi', 'arroz', 'aceite', 'fideos')..."
                className="w-full pl-12 pr-4 py-3.5 rounded-2xl bg-stone-50 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 text-sm font-medium text-stone-900 dark:text-stone-100 placeholder-stone-400 dark:placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 focus:bg-white dark:focus:bg-stone-850 transition-all shadow-inner"
              />
            </div>

            <button
              type="submit"
              className="bg-orange-600 hover:bg-orange-500 active:scale-95 text-white font-extrabold px-6 py-3.5 rounded-2xl text-sm transition-all shadow-md shadow-orange-500/20 flex items-center justify-center space-x-2"
            >
              <span>Buscar Oportunidad</span>
            </button>
          </form>

          {/* Sugerencias Rápidas */}
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-stone-500 dark:text-stone-400">
            <span className="font-semibold">Sugerencias:</span>
            {['Doña Carne', 'Alvi', 'Central Mayorista', 'Castro', 'La Oferta', 'Comercial Teba', 'Lomo Liso', 'Papas Lo Valledor', 'Arroz Fardo', 'Aceite Caja'].map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => handleSuggestionClick(tag)}
                className="bg-stone-100 dark:bg-stone-800 hover:bg-orange-50 dark:hover:bg-stone-700 hover:text-orange-700 dark:hover:text-orange-300 border border-transparent dark:border-stone-700 text-stone-700 dark:text-stone-300 px-2.5 py-1 rounded-lg transition-all font-medium"
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tarjetas KPI de Métricas Clave */}
      {kpis && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="rounded-2xl border border-stone-200/80 dark:border-stone-800 bg-white dark:bg-stone-900 p-4 sm:p-5 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider">Ahorro Promedio</span>
              <span className="rounded-xl bg-orange-50 dark:bg-orange-950/60 p-2 text-orange-600 dark:text-orange-400">
                <Percent className="h-4 w-4" />
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-stone-900 dark:text-stone-100">{kpis.avg_savings_pct}%</span>
              <span className="text-xs font-semibold text-orange-600 dark:text-orange-400">vs Retail</span>
            </div>
          </div>

          <div className="rounded-2xl border border-stone-200/80 dark:border-stone-800 bg-white dark:bg-stone-900 p-4 sm:p-5 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider">Máximo Ahorro</span>
              <span className="rounded-xl bg-amber-50 dark:bg-amber-950/60 p-2 text-amber-600 dark:text-amber-400">
                <Flame className="h-4 w-4" />
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-stone-900 dark:text-stone-100">{kpis.max_savings_pct}%</span>
              <span className="text-xs font-semibold text-amber-600 dark:text-amber-400">Lo Valledor</span>
            </div>
          </div>

          <div className="rounded-2xl border border-stone-200/80 dark:border-stone-800 bg-white dark:bg-stone-900 p-4 sm:p-5 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider">Super Ahorros</span>
              <span className="rounded-xl bg-orange-50 dark:bg-orange-950/60 p-2 text-orange-600 dark:text-orange-400">
                <Award className="h-4 w-4" />
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-stone-900 dark:text-stone-100">{kpis.super_deals_count}</span>
              <span className="text-xs font-semibold text-orange-600 dark:text-orange-400">&gt; 25% ahorro</span>
            </div>
          </div>

          <div className="rounded-2xl border border-stone-200/80 dark:border-stone-800 bg-white dark:bg-stone-900 p-4 sm:p-5 shadow-xs">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider">Canales Monitoreados</span>
              <span className="rounded-xl bg-amber-50 dark:bg-amber-950/60 p-2 text-amber-700 dark:text-amber-400">
                <Store className="h-4 w-4" />
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-stone-900 dark:text-stone-100">{kpis.monitored_stores_count}</span>
              <span className="text-xs font-semibold text-amber-700 dark:text-amber-400">Tiendas / Hubs</span>
            </div>
          </div>
        </div>
      )}

      {/* Filtro por Tienda / Cadena Mayorista */}
      <div className="space-y-2">
        <div className="flex items-center space-x-2 text-xs font-bold text-stone-700 dark:text-stone-300 uppercase tracking-wider">
          <Store className="w-3.5 h-3.5 text-orange-600" />
          <span>Filtrar por Cadena / Distribuidor:</span>
        </div>
        <div className="flex items-center space-x-2 overflow-x-auto py-1 px-0.5 custom-scrollbar">
          <button
            onClick={() => setSelectedStore('todas')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all shadow-xs ${
              selectedStore === 'todas'
                ? 'bg-stone-900 dark:bg-orange-600 text-white shadow-sm scale-105'
                : 'bg-white dark:bg-stone-800 hover:bg-orange-50 dark:hover:bg-stone-700 text-stone-700 dark:text-stone-300 border border-stone-200 dark:border-stone-700 hover:border-orange-200 dark:hover:border-orange-500'
            }`}
          >
            Todas las Cadenas ({stores.length || 12})
          </button>
          {stores.map((s) => (
            <button
              key={s.id}
              onClick={() => setSelectedStore(s.id)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all shadow-xs ${
                selectedStore === s.id
                  ? 'bg-orange-600 text-white shadow-sm scale-105'
                  : 'bg-white dark:bg-stone-800 hover:bg-orange-50 dark:hover:bg-stone-700 text-stone-700 dark:text-stone-300 border border-stone-200 dark:border-stone-700 hover:border-orange-200 dark:hover:border-orange-500'
              }`}
            >
              {s.name.split('(')[0].trim()}
            </button>
          ))}
        </div>
      </div>

      {/* Filtro por Categorías de Canales */}
      <div className="space-y-2">
        <div className="flex items-center space-x-2 text-xs font-bold text-stone-700 dark:text-stone-300 uppercase tracking-wider">
          <Target className="w-3.5 h-3.5 text-orange-600" />
          <span>Filtrar por Categoría de Ahorro:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => {
            const Icon = cat.icon;
            const isActive = selectedCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
                  isActive
                    ? 'bg-orange-600 text-white shadow-md shadow-orange-500/20'
                    : 'bg-white dark:bg-stone-800 text-stone-700 dark:text-stone-300 border border-stone-200 dark:border-stone-700 hover:bg-stone-50 dark:hover:bg-stone-700'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-stone-500 dark:text-stone-400'}`} />
                <span>{cat.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Encabezado y Resultados */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base sm:text-lg font-black text-stone-900 dark:text-stone-100 flex items-center space-x-2">
            <ShoppingBag className="w-5 h-5 text-orange-600" />
            <span>Oportunidades Alternativas ({opportunities.length})</span>
          </h2>
          <span className="text-xs font-semibold text-stone-500 dark:text-stone-400">
            Comparado contra precios de Jumbo, Lider, Santa Isabel y Unimarc
          </span>
        </div>

        {/* Grilla con el mismo formato de cards que retail */}
        {loading ? (
          <div className="py-20 text-center bg-white dark:bg-stone-900 rounded-3xl border border-stone-200 dark:border-stone-800 shadow-xs">
            <div className="w-12 h-12 border-4 border-orange-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm font-bold text-stone-700 dark:text-stone-200">Consultando precios en canales alternativos...</p>
            <p className="text-xs text-stone-500 dark:text-stone-400 mt-1">Calculando brechas contra el retail tradicional</p>
          </div>
        ) : opportunities.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {opportunities.map((opp) => (
              <RadarProductCard
                key={opp.id}
                opportunity={opp}
                onViewComparison={(item) => setSelectedComparisonOpp(item)}
              />
            ))}
          </div>
        ) : (
          <div className="py-16 text-center bg-white dark:bg-stone-900 rounded-3xl border border-stone-200 dark:border-stone-800 p-8 space-y-3">
            <AlertCircle className="w-12 h-12 text-stone-400 mx-auto" />
            <h3 className="text-base font-bold text-stone-800 dark:text-stone-200">No encontramos oportunidades para tu búsqueda</h3>
            <p className="text-xs text-stone-500 dark:text-stone-400 max-w-md mx-auto">
              Prueba con términos como "lomo", "papas", "atun", "fideos" o seleccionando "Todas las Oportunidades".
            </p>
          </div>
        )}
      </div>

      {/* Directorio de Canales Monitoreados */}
      <div className="mt-10 pt-8 border-t border-stone-200 dark:border-stone-800">
        <h3 className="text-base font-bold text-stone-900 dark:text-stone-100 mb-3 flex items-center gap-2">
          <Store className="h-5 w-5 text-orange-600" />
          <span>Canales Alternativos Integrados</span>
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stores.map((store) => (
            <div key={store.id} className="rounded-2xl border border-stone-200/80 dark:border-stone-800 bg-white dark:bg-stone-900 p-4 shadow-xs hover:border-orange-300 dark:hover:border-orange-500 transition-colors flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between">
                  <span className="inline-block rounded-md bg-orange-50 dark:bg-orange-950/60 px-2 py-0.5 text-[10px] font-bold text-orange-800 dark:text-orange-300 border border-orange-200 dark:border-orange-800">
                    {store.type_label}
                  </span>
                  <a 
                    href={store.website} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="rounded-lg p-1 text-stone-400 hover:bg-stone-100 dark:hover:bg-stone-800 hover:text-orange-600 dark:hover:text-orange-400"
                    title="Visitar sitio oficial"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>
                <h4 className="mt-2 text-sm font-bold text-stone-900 dark:text-stone-100">{store.name}</h4>
                <p className="mt-1 text-xs text-stone-600 dark:text-stone-400 leading-relaxed">{store.description}</p>
              </div>
              <div className="mt-3 flex items-center gap-1 text-[11px] font-semibold text-orange-900 dark:text-orange-300 bg-orange-50/70 dark:bg-stone-800 rounded-md p-1.5 border border-orange-100 dark:border-stone-700">
                <CheckCircle2 className="h-3.5 w-3.5 text-orange-600 dark:text-orange-400 shrink-0" />
                <span>{store.highlight}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal de Comparativa de Oportunidad */}
      {selectedComparisonOpp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/50 dark:bg-black/80 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white dark:bg-stone-900 rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-stone-200 dark:border-stone-800 relative">
            <div className="flex items-start justify-between mb-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-orange-600 dark:text-orange-400">
                  Comparativa de Ahorro
                </span>
                <h3 className="text-lg font-extrabold text-stone-900 dark:text-stone-100 mt-0.5">
                  {selectedComparisonOpp.product_name}
                </h3>
              </div>
              <button
                onClick={() => setSelectedComparisonOpp(null)}
                className="text-stone-400 hover:text-stone-600 dark:hover:text-stone-200 text-xl font-bold p-1"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3 p-4 bg-stone-50 dark:bg-stone-850 rounded-2xl border border-stone-100 dark:border-stone-800">
                <div>
                  <span className="text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase block">Canal Alternativo</span>
                  <span className="text-xs font-semibold text-orange-700 dark:text-orange-400 block">{selectedComparisonOpp.store_name}</span>
                  <span className="text-xl font-black text-stone-900 dark:text-stone-100 mt-1 block">
                    ${Math.round(selectedComparisonOpp.alternative_price).toLocaleString('es-CL')}
                  </span>
                  <span className="text-[10px] text-stone-500 dark:text-stone-400">({selectedComparisonOpp.unit})</span>
                </div>

                <div className="border-l border-stone-200 dark:border-stone-700 pl-3">
                  <span className="text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase block">Benchmark Retail</span>
                  <span className="text-xs font-semibold text-stone-600 dark:text-stone-400 block">{selectedComparisonOpp.benchmark_label}</span>
                  <span className="text-xl font-black text-stone-400 dark:text-stone-500 line-through mt-1 block">
                    ${Math.round(selectedComparisonOpp.traditional_benchmark_price).toLocaleString('es-CL')}
                  </span>
                  <span className="text-[10px] text-stone-500 dark:text-stone-400">4 Supermercados</span>
                </div>
              </div>

              <div className="bg-orange-50 dark:bg-orange-950/60 border border-orange-200 dark:border-orange-800 rounded-2xl p-4 flex items-center justify-between">
                <span className="text-xs font-bold text-orange-950 dark:text-orange-200">Ahorro total estimado:</span>
                <span className="text-base font-extrabold text-orange-700 dark:text-orange-300">
                  -${Math.round(selectedComparisonOpp.savings_clp).toLocaleString('es-CL')} CLP ({selectedComparisonOpp.savings_percentage}%)
                </span>
              </div>

              <p className="text-xs text-stone-600 dark:text-stone-300 leading-relaxed bg-stone-50 dark:bg-stone-850 p-3 rounded-xl border border-stone-100 dark:border-stone-800 italic">
                "{selectedComparisonOpp.recommendation_note}"
              </p>

              <div className="flex gap-3 pt-2">
                <a
                  href={selectedComparisonOpp.purchase_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 bg-orange-600 hover:bg-orange-500 text-white font-extrabold py-3 rounded-xl text-xs text-center flex items-center justify-center space-x-1.5 shadow-md shadow-orange-500/20"
                >
                  <span>Ir a {selectedComparisonOpp.store_name.split(' ')[0]}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>

                <button
                  onClick={() => setSelectedComparisonOpp(null)}
                  className="px-5 bg-stone-100 dark:bg-stone-800 hover:bg-stone-200 dark:hover:bg-stone-700 text-stone-700 dark:text-stone-300 font-bold py-3 rounded-xl text-xs"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
