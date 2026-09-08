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
  CheckCircle2
} from 'lucide-react';
import { PriceOpportunity, AlternativeStore, RadarKPIs } from '../types/radar';
import { radarService } from '../services/radarService';
import { RadarProductCard } from './RadarProductCard';

export function RadarAlternativoView() {
  const [opportunities, setOpportunities] = useState<PriceOpportunity[]>([]);
  const [stores, setStores] = useState<AlternativeStore[]>([]);
  const [kpis, setKpis] = useState<RadarKPIs | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('todos');
  const [query, setQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedComparisonOpp, setSelectedComparisonOpp] = useState<PriceOpportunity | null>(null);

  const loadData = async (cat: string, searchTerm: string) => {
    setLoading(true);
    try {
      const [oppsData, storesData, kpisData] = await Promise.all([
        radarService.getOpportunities(cat, searchTerm),
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
    loadData(selectedCategory, query);
  }, [selectedCategory]);

  const onSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData(selectedCategory, query);
  };

  const handleSuggestionClick = (term: string) => {
    setQuery(term);
    loadData(selectedCategory, term);
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
      <div className="bg-white rounded-3xl p-6 sm:p-10 border border-slate-200 shadow-sm relative overflow-hidden">
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full text-xs font-bold border border-emerald-200 mb-3">
            <Target className="w-3.5 h-3.5" />
            <span>Búsqueda en 12 Canales Alternativos & Mayoristas</span>
          </div>

          <h1 className="text-2xl sm:text-4xl font-black text-slate-900 tracking-tight leading-tight">
            Ahorra hasta un <span className="text-emerald-600">65%</span> en <span className="text-rose-600">Doña Carne</span>, <span className="text-blue-600">Alvi</span>, <span className="text-amber-600">Central Mayorista</span> y más.
          </h1>

          <p className="text-sm sm:text-base text-slate-600 mt-2">
            Comparamos en tiempo real carnicerías directas, supermercados mayoristas, bodegas y distribuidoras de alimentos (Alvi, Central Mayorista, Comercial Castro, La Oferta, Comercial Teba, Distribuidora Santiago, Abu-Gosh, El Carnicero, Lo Valledor y aCuenta).
          </p>

          {/* Formulario de Búsqueda */}
          <form onSubmit={onSearchSubmit} className="mt-6 flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-5 h-5 text-slate-400 absolute left-4 top-3.5" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Busca por corte, producto o tienda (ej: 'lomo liso', 'Doña Carne', 'Alvi', 'arroz', 'aceite', 'fideos')..."
                className="w-full pl-12 pr-4 py-3.5 rounded-2xl bg-slate-50 border border-slate-300 text-sm font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all shadow-inner"
              />
            </div>

            <button
              type="submit"
              className="bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white font-extrabold px-6 py-3.5 rounded-2xl text-sm transition-all shadow-md shadow-emerald-500/20 flex items-center justify-center space-x-2"
            >
              <span>Buscar</span>
            </button>
          </form>

          {/* Sugerencias Rápidas */}
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
            <span className="font-semibold">Sugerencias:</span>
            {['Doña Carne', 'Alvi', 'Central Mayorista', 'Castro', 'La Oferta', 'Comercial Teba', 'Lomo Liso', 'Papas Lo Valledor', 'Arroz Fardo', 'Aceite Caja'].map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => handleSuggestionClick(tag)}
                className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-1 rounded-lg transition-colors font-medium"
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
          <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Ahorro Promedio</span>
              <span className="rounded-xl bg-emerald-50 p-2 text-emerald-600">
                <Percent className="h-4 w-4" />
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-slate-900">{kpis.avg_savings_pct}%</span>
              <span className="text-xs font-semibold text-emerald-600">vs Retail</span>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Máximo Ahorro</span>
              <span className="rounded-xl bg-rose-50 p-2 text-rose-600">
                <Flame className="h-4 w-4" />
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-slate-900">{kpis.max_savings_pct}%</span>
              <span className="text-xs font-semibold text-rose-600">Lo Valledor</span>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Super Ahorros</span>
              <span className="rounded-xl bg-amber-50 p-2 text-amber-600">
                <Award className="h-4 w-4" />
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-slate-900">{kpis.super_deals_count}</span>
              <span className="text-xs font-semibold text-amber-600">&gt; 25% ahorro</span>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Canales Monitoreados</span>
              <span className="rounded-xl bg-teal-50 p-2 text-teal-600">
                <Store className="h-4 w-4" />
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-slate-900">{kpis.monitored_stores_count}</span>
              <span className="text-xs font-semibold text-teal-600">Tiendas / Hubs</span>
            </div>
          </div>
        </div>
      )}

      {/* Filtro por Categorías de Canales */}
      <div className="space-y-2">
        <div className="flex items-center space-x-2 text-xs font-bold text-slate-600 uppercase tracking-wider">
          <Target className="w-3.5 h-3.5 text-emerald-600" />
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
                    ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                    : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-slate-500'}`} />
                <span>{cat.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Encabezado y Resultados */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base sm:text-lg font-black text-slate-900 flex items-center space-x-2">
            <ShoppingBag className="w-5 h-5 text-emerald-600" />
            <span>Oportunidades Alternativas ({opportunities.length})</span>
          </h2>
          <span className="text-xs font-semibold text-slate-500">
            Comparado contra precios de Jumbo, Lider, Santa Isabel y Unimarc
          </span>
        </div>

        {/* Grilla con el mismo formato de cards que retail */}
        {loading ? (
          <div className="py-20 text-center bg-white rounded-3xl border border-slate-200">
            <div className="w-12 h-12 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm font-bold text-slate-700">Consultando precios en canales alternativos...</p>
            <p className="text-xs text-slate-500 mt-1">Calculando brechas contra el retail tradicional</p>
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
          <div className="py-16 text-center bg-white rounded-3xl border border-slate-200 p-8 space-y-3">
            <AlertCircle className="w-12 h-12 text-slate-400 mx-auto" />
            <h3 className="text-base font-bold text-slate-800">No encontramos oportunidades para tu búsqueda</h3>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              Prueba con términos como "lomo", "papas", "atun", "fideos" o seleccionando "Todas las Oportunidades".
            </p>
          </div>
        )}
      </div>

      {/* Directorio de Canales Monitoreados */}
      <div className="mt-10 pt-8 border-t border-slate-200">
        <h3 className="text-base font-bold text-slate-900 mb-3 flex items-center gap-2">
          <Store className="h-5 w-5 text-emerald-600" />
          <span>Canales Alternativos Integrados</span>
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stores.map((store) => (
            <div key={store.id} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm hover:border-emerald-500 transition-colors flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between">
                  <span className="inline-block rounded-md bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700 border border-emerald-200">
                    {store.type_label}
                  </span>
                  <a 
                    href={store.website} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-emerald-600"
                    title="Visitar sitio oficial"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>
                <h4 className="mt-2 text-sm font-bold text-slate-900">{store.name}</h4>
                <p className="mt-1 text-xs text-slate-600 leading-relaxed">{store.description}</p>
              </div>
              <div className="mt-3 flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50/70 rounded-md p-1.5 border border-emerald-100">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                <span>{store.highlight}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal de Comparativa de Oportunidad */}
      {selectedComparisonOpp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 relative">
            <div className="flex items-start justify-between mb-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-600">
                  Comparativa de Ahorro
                </span>
                <h3 className="text-lg font-extrabold text-slate-900 mt-0.5">
                  {selectedComparisonOpp.product_name}
                </h3>
              </div>
              <button
                onClick={() => setSelectedComparisonOpp(null)}
                className="text-slate-400 hover:text-slate-600 text-xl font-bold p-1"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3 p-4 bg-slate-50 rounded-2xl border border-slate-100">
                <div>
                  <span className="text-[11px] font-bold text-slate-500 uppercase block">Canal Alternativo</span>
                  <span className="text-xs font-semibold text-emerald-700 block">{selectedComparisonOpp.store_name}</span>
                  <span className="text-xl font-black text-slate-900 mt-1 block">
                    ${Math.round(selectedComparisonOpp.alternative_price).toLocaleString('es-CL')}
                  </span>
                  <span className="text-[10px] text-slate-500">({selectedComparisonOpp.unit})</span>
                </div>

                <div className="border-l border-slate-200 pl-3">
                  <span className="text-[11px] font-bold text-slate-500 uppercase block">Benchmark Retail</span>
                  <span className="text-xs font-semibold text-slate-600 block">{selectedComparisonOpp.benchmark_label}</span>
                  <span className="text-xl font-black text-slate-400 line-through mt-1 block">
                    ${Math.round(selectedComparisonOpp.traditional_benchmark_price).toLocaleString('es-CL')}
                  </span>
                  <span className="text-[10px] text-slate-500">4 Supermercados</span>
                </div>
              </div>

              <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 flex items-center justify-between">
                <span className="text-xs font-bold text-emerald-900">Ahorro total estimado:</span>
                <span className="text-base font-extrabold text-emerald-700">
                  -${Math.round(selectedComparisonOpp.savings_clp).toLocaleString('es-CL')} CLP ({selectedComparisonOpp.savings_percentage}%)
                </span>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100 italic">
                "{selectedComparisonOpp.recommendation_note}"
              </p>

              <div className="flex gap-3 pt-2">
                <a
                  href={selectedComparisonOpp.purchase_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold py-3 rounded-xl text-xs text-center flex items-center justify-center space-x-1.5 shadow-md shadow-emerald-500/20"
                >
                  <span>Ir a {selectedComparisonOpp.store_name.split(' ')[0]}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>

                <button
                  onClick={() => setSelectedComparisonOpp(null)}
                  className="px-5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold py-3 rounded-xl text-xs"
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
