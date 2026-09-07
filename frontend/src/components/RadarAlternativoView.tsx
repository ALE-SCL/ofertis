import React, { useState, useEffect } from 'react';
import { 
  Target, 
  TrendingDown, 
  Store, 
  ExternalLink, 
  CheckCircle2, 
  Sparkles, 
  Percent, 
  ShoppingBag, 
  Flame, 
  Award,
  Layers,
  ArrowRight
} from 'lucide-react';
import { PriceOpportunity, AlternativeStore, RadarKPIs } from '../types/radar';
import { radarService } from '../services/radarService';

export function RadarAlternativoView() {
  const [opportunities, setOpportunities] = useState<PriceOpportunity[]>([]);
  const [stores, setStores] = useState<AlternativeStore[]>([]);
  const [kpis, setKpis] = useState<RadarKPIs | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('todos');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadData(selectedCategory);
  }, [selectedCategory]);

  const loadData = async (category: string) => {
    setLoading(true);
    try {
      const [oppsData, storesData, kpisData] = await Promise.all([
        radarService.getOpportunities(category),
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

  const categories = [
    { id: 'todos', label: 'Todas las Oportunidades', icon: Target },
    { id: 'carnes', label: 'Carnes Directas (El Carnicero)', icon: Flame },
    { id: 'despensa', label: 'Abarrotes y Despensa (aCuenta)', icon: ShoppingBag },
    { id: 'frutas_verduras', label: 'Frutas y Verduras por Mayor (Lo Valledor)', icon: Layers },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Banner Principal de RadarAlternativo */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-emerald-800 via-teal-900 to-indigo-950 p-8 text-white shadow-xl">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full bg-emerald-500/20 px-4 py-1.5 text-xs font-semibold text-emerald-300 backdrop-blur-md border border-emerald-400/30 mb-4">
            <Target className="h-4 w-4" />
            <span>Módulo de Inteligencia de Ahorro Sin Simulación</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl text-white">
            🎯 Radar Alternativo: Canales Fuera del Retail Tradicional
          </h1>
          <p className="mt-3 text-emerald-100/90 text-sm sm:text-base leading-relaxed">
            Descubrimos y monitoreamos en vivo canales directos de compra en Chile: <span className="font-semibold text-white">carnicerías directas, bodegas discount y mercados mayoristas</span>, comparando cada precio contra los 4 grandes supermercados (Jumbo, Santa Isabel, Unimarc y Lider) para encontrar ahorros reales de hasta un 65%.
          </p>
        </div>

        {/* Efecto de radar decorativo de fondo */}
        <div className="absolute right-0 top-0 -mt-12 -mr-12 h-80 w-80 rounded-full border border-emerald-500/10 pointer-events-none" />
        <div className="absolute right-0 top-0 -mt-4 -mr-4 h-64 w-64 rounded-full border border-emerald-400/20 pointer-events-none" />
        <div className="absolute right-4 top-4 h-48 w-48 rounded-full border border-teal-300/30 pointer-events-none" />
      </div>

      {/* Tarjetas KPI de Métricas Clave */}
      {kpis && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Ahorro Promedio</span>
              <span className="rounded-lg bg-emerald-50 p-2 text-emerald-600">
                <Percent className="h-5 w-5" />
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-gray-900">{kpis.avg_savings_pct}%</span>
              <span className="text-xs font-semibold text-emerald-600">vs Retail</span>
            </div>
          </div>

          <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Máximo Ahorro</span>
              <span className="rounded-lg bg-rose-50 p-2 text-rose-600">
                <Flame className="h-5 w-5" />
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-gray-900">{kpis.max_savings_pct}%</span>
              <span className="text-xs font-semibold text-rose-600">Lo Valledor</span>
            </div>
          </div>

          <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Super Oportunidades</span>
              <span className="rounded-lg bg-amber-50 p-2 text-amber-600">
                <Award className="h-5 w-5" />
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-gray-900">{kpis.super_deals_count}</span>
              <span className="text-xs font-semibold text-amber-600">&gt; 25% ahorro</span>
            </div>
          </div>

          <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">Canales en Vivo</span>
              <span className="rounded-lg bg-teal-50 p-2 text-teal-600">
                <Store className="h-5 w-5" />
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-black text-gray-900">{kpis.monitored_stores_count}</span>
              <span className="text-xs font-semibold text-teal-600">Cadenas / Hubs</span>
            </div>
          </div>
        </div>
      )}

      {/* Fichas de Canales Alternativos Monitoreados */}
      <div>
        <h2 className="text-base font-bold text-gray-900 mb-3 flex items-center gap-2">
          <Store className="h-5 w-5 text-emerald-600" />
          Canales Alternativos Integrados
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {stores.map((store) => (
            <div key={store.id} className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:border-emerald-500 transition-colors">
              <div className="flex items-start justify-between">
                <div>
                  <span className="inline-block rounded-md bg-emerald-50 px-2 py-0.5 text-xs font-bold text-emerald-700">
                    {store.type_label}
                  </span>
                  <h3 className="mt-2 text-sm font-bold text-gray-900">{store.name}</h3>
                </div>
                <a 
                  href={store.website} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-emerald-600"
                  title="Visitar sitio oficial"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>
              <p className="mt-2 text-xs text-gray-600 leading-relaxed">{store.description}</p>
              <div className="mt-3 flex items-center gap-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50/70 rounded-md p-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                <span>{store.highlight}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selector de Categorías de Oportunidad */}
      <div className="flex flex-wrap gap-2 border-b border-gray-200 pb-4">
        {categories.map((cat) => {
          const Icon = cat.icon;
          const isActive = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold transition-all ${
                isActive
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                  : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
              }`}
            >
              <Icon className={`h-4 w-4 ${isActive ? 'text-white' : 'text-gray-500'}`} />
              <span>{cat.label}</span>
            </button>
          );
        })}
      </div>

      {/* Grilla de Oportunidades de Ahorro */}
      {loading ? (
        <div className="flex h-64 items-center justify-center rounded-2xl bg-white border border-gray-100">
          <div className="flex flex-col items-center gap-3">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-emerald-600 border-t-transparent" />
            <span className="text-xs font-medium text-gray-500">Escaneando brechas de precio en canales alternativos...</span>
          </div>
        </div>
      ) : opportunities.length === 0 ? (
        <div className="rounded-2xl border border-gray-200 bg-white p-12 text-center">
          <Target className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-base font-bold text-gray-900">No se encontraron productos en esta categoría</h3>
          <p className="mt-1 text-xs text-gray-500">Prueba seleccionando 'Todas las Oportunidades'.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {opportunities.map((opp) => {
            const isSuper = opp.deal_level === 'SUPER_AHORRO';
            const isAlto = opp.deal_level === 'AHORRO_ALTO';

            return (
              <div
                key={opp.id}
                className="group relative flex flex-col justify-between rounded-2xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-lg hover:border-emerald-500/60 transition-all"
              >
                <div>
                  {/* Badge de Nivel de Deal */}
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-extrabold ${
                        isSuper
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                          : isAlto
                          ? 'bg-amber-100 text-amber-800 border border-amber-300'
                          : 'bg-blue-100 text-blue-800 border border-blue-300'
                      }`}
                    >
                      {isSuper ? <Flame className="h-3 w-3 text-emerald-600" /> : <Sparkles className="h-3 w-3 text-amber-600" />}
                      <span>{opp.deal_label}</span>
                    </span>

                    <span className="text-[11px] font-semibold text-gray-500 uppercase">
                      {opp.unit}
                    </span>
                  </div>

                  {/* Nombre y Canal */}
                  <h3 className="text-base font-bold text-gray-900 group-hover:text-emerald-700 transition-colors">
                    {opp.product_name}
                  </h3>
                  <div className="mt-1 flex items-center gap-1.5 text-xs text-gray-600">
                    <Store className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                    <span className="font-semibold text-gray-800">{opp.store_name}</span>
                  </div>

                  {/* Comparativa Visual de Precios */}
                  <div className="mt-5 rounded-xl bg-gray-50 p-4 border border-gray-100">
                    <div className="flex items-baseline justify-between">
                      <div>
                        <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">Precio Alternativo</span>
                        <span className="text-2xl font-black text-emerald-600">
                          ${opp.alternative_price.toLocaleString('es-CL')}
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">Retail Tradicional</span>
                        <span className="text-base font-semibold text-gray-400 line-through">
                          ${opp.traditional_benchmark_price.toLocaleString('es-CL')}
                        </span>
                      </div>
                    </div>

                    {/* Barra de Ahorro y Spread */}
                    <div className="mt-3 pt-3 border-t border-gray-200/60 flex items-center justify-between text-xs">
                      <span className="font-bold text-gray-700">Ahorras en cada compra:</span>
                      <span className="font-black text-emerald-700 bg-emerald-100/70 px-2 py-0.5 rounded">
                        -${opp.savings_clp.toLocaleString('es-CL')} CLP ({opp.savings_percentage}%)
                      </span>
                    </div>
                  </div>

                  {/* Nota / Recomendación */}
                  <p className="mt-3 text-xs text-gray-600 leading-relaxed italic">
                    "{opp.recommendation_note}"
                  </p>
                </div>

                {/* Botón de Enlace Directo a la Tienda */}
                <div className="mt-6 pt-4 border-t border-gray-100">
                  <a
                    href={opp.purchase_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-gray-900 py-2.5 px-4 text-xs font-bold text-white shadow-sm hover:bg-emerald-600 hover:shadow-md transition-all"
                  >
                    <span>Ver y comprar en {opp.store_name.split(' ')[0]}</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
