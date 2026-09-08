import React, { useState, useEffect } from 'react';
import { Search, Filter, AlertCircle, ShoppingBag, RefreshCw, HeartHandshake } from 'lucide-react';
import axios from 'axios';
import { Navbar } from './components/Navbar';
import { MiningStatsBanner } from './components/MiningStatsBanner';
import { CategoryFilter } from './components/CategoryFilter';
import { ProductCard } from './components/ProductCard';
import { ProductDetailModal } from './components/ProductDetailModal';
import { AlertModal } from './components/AlertModal';
import { RadarAlternativoView } from './components/RadarAlternativoView';
import { ProductSearchResult, CategoryItem, MiningStats } from './types';
import { Target, Store } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export function App() {
  const [activeTab, setActiveTab] = useState<'retail' | 'radar'>('retail');
  const [query, setQuery] = useState('lomo');
  const [selectedCategory, setSelectedCategory] = useState('todos');
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [products, setProducts] = useState<ProductSearchResult[]>([]);
  const [stats, setStats] = useState<MiningStats | null>(null);
  const [loading, setLoading] = useState(false);

  // Estados de Modales
  const [selectedCanonicalId, setSelectedCanonicalId] = useState<number | null>(null);
  const [alertModalState, setAlertModalState] = useState<{
    isOpen: boolean;
    productName: string;
    canonicalId: number | null;
    currentBestPrice: number;
  }>({
    isOpen: false,
    productName: '',
    canonicalId: null,
    currentBestPrice: 0
  });

  // Cargar categorías y estadísticas iniciales
  useEffect(() => {
    const fetchInitialMetadata = async () => {
      try {
        const [catRes, statRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/products/categories`),
          axios.get(`${API_BASE_URL}/mining/stats`)
        ]);
        setCategories(catRes.data);
        setStats(statRes.data);
      } catch (err) {
        console.error('Error cargando metadata:', err);
      }
    };

    fetchInitialMetadata();
  }, []);

  // Ejecutar búsqueda semántica con pgvector
  const handleSearch = async (searchTerm: string, catSlug: string) => {
    if (!searchTerm.trim() && catSlug === 'todos') {
      searchTerm = 'leche'; // término inicial
    }

    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/products/search`, {
        params: {
          q: searchTerm.trim() || 'leche',
          category: catSlug !== 'todos' ? catSlug : undefined,
          limit: 20
        }
      });
      setProducts(res.data);
    } catch (err) {
      console.error('Error buscando productos:', err);
    } finally {
      setLoading(false);
    }
  };

  // Minería en Vivo On-Demand (consulta las 4 tiendas en tiempo real)
  const handleLiveRefresh = async () => {
    const term = query.trim() || 'leche';
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE_URL}/products/refresh-live`, null, {
        params: {
          q: term,
          category: selectedCategory !== 'todos' ? selectedCategory : undefined,
          limit: 4
        }
      });
      setProducts(res.data);
      // Actualizar estadísticas del banner
      const statRes = await axios.get(`${API_BASE_URL}/mining/stats`);
      setStats(statRes.data);
    } catch (err) {
      console.error('Error en minería en vivo:', err);
      // Fallback a búsqueda normal si falla
      handleSearch(query, selectedCategory);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch(query, selectedCategory);
  }, [selectedCategory]);

  const onSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(query, selectedCategory);
  };

  const handleOpenAlert = (product: ProductSearchResult) => {
    setAlertModalState({
      isOpen: true,
      productName: product.name,
      canonicalId: product.id,
      currentBestPrice: product.min_unit_price
    });
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-100">
      <Navbar onOpenMyAlerts={() => alert('Ingresa tu número en el botón de Alerta WhatsApp de cualquier producto para ver tus alertas.')} />
      <MiningStatsBanner stats={stats} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-6">
        {/* Navigation Tabs: Retail Tradicional vs Radar Alternativo */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 bg-white p-2 sm:p-2.5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab('retail')}
              className={`flex-1 sm:flex-none flex items-center justify-center space-x-2.5 px-5 py-2.5 rounded-xl font-bold text-sm transition-all ${
                activeTab === 'retail'
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Store className="w-4 h-4" />
              <span>Supermercados Retail</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                activeTab === 'retail' ? 'bg-blue-500 text-white' : 'bg-slate-200 text-slate-700'
              }`}>
                4 Cadenas
              </span>
            </button>

            <button
              onClick={() => setActiveTab('radar')}
              className={`flex-1 sm:flex-none flex items-center justify-center space-x-2.5 px-5 py-2.5 rounded-xl font-bold text-sm transition-all ${
                activeTab === 'radar'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/20'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Target className="w-4 h-4" />
              <span>Radar Alternativo</span>
              <span className="text-xs px-2 py-0.5 rounded-full font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                Hasta 65% Ahorro
              </span>
            </button>
          </div>

          <div className="text-xs text-slate-500 px-3 hidden md:block">
            {activeTab === 'retail' 
              ? 'Comparando Jumbo, Lider, Santa Isabel y Unimarc con normalización de unidad.'
              : 'Canales mayoristas, carnicerías directas y ferias con brecha real contra retail.'}
          </div>
        </div>

        {activeTab === 'retail' ? (
          <>
            {/* Hero & Buscador */}
            <div className="bg-white rounded-3xl p-6 sm:p-10 border border-slate-200 shadow-sm relative overflow-hidden">
              <div className="max-w-3xl">
                <div className="inline-flex items-center space-x-2 bg-rose-50 text-rose-700 px-3.5 py-1.5 rounded-full text-xs font-bold border border-rose-200 mb-3 shadow-xs">
                  <HeartHandshake className="w-4 h-4 text-rose-500" />
                  <span>Cero engaños: el comparador independiente que defiende tu presupuesto familiar</span>
                </div>

                <h1 className="text-2xl sm:text-4xl font-black text-slate-900 tracking-tight leading-tight">
                  Que no te cobren de más: encuentra el precio real por kilo y litro en <span className="text-blue-600">Lider</span>, <span className="text-emerald-600">Jumbo</span>, <span className="text-rose-600">Santa Isabel</span> y <span className="text-red-600">Unimarc</span>.
                </h1>

                <p className="text-sm sm:text-base text-slate-600 mt-2">
                  Estandarizamos todos los envases y formatos al mismo peso y volumen ($/kg y $/litro) para que descubras qué supermercado es más conveniente de verdad y tu plata rinda más a fin de mes.
                </p>

                {/* Input de Búsqueda */}
                <form onSubmit={onSearchSubmit} className="mt-6 flex flex-col sm:flex-row gap-3">
                  <div className="relative flex-1">
                    <Search className="w-5 h-5 text-slate-400 absolute left-4 top-3.5" />
                    <input
                      type="text"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="¿Qué necesitas comprar hoy? (ej: 'leche colun', 'lomo liso', 'posta negra', 'arroz grado 1', 'aceite', 'fideos')..."
                      className="w-full pl-12 pr-4 py-3.5 rounded-2xl bg-slate-50 border border-slate-300 text-sm font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all shadow-inner"
                    />
                  </div>

                  <button
                    type="submit"
                    className="bg-blue-600 hover:bg-blue-700 active:scale-95 text-white font-extrabold px-6 py-3.5 rounded-2xl text-sm transition-all shadow-md shadow-blue-500/20 flex items-center justify-center space-x-2"
                  >
                    <span>Buscar Mejor Precio</span>
                  </button>

                  <button
                    type="button"
                    onClick={handleLiveRefresh}
                    disabled={loading}
                    title="Consulta en tiempo real los precios oficiales de Jumbo, Santa Isabel, Unimarc y Lider"
                    className="bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white font-extrabold px-5 py-3.5 rounded-2xl text-sm transition-all shadow-md shadow-emerald-600/20 flex items-center justify-center space-x-2 disabled:opacity-50"
                  >
                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    <span>Comprobar Precios de Hoy</span>
                  </button>
                </form>

                {/* Sugerencias rápidas */}
                <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                  <span className="font-semibold">Sugerencias:</span>
                  {['Lomo Liso', 'Posta Negra', 'Pechuga Pollo', 'Leche Colun', 'Arroz Tucapel', 'Spaghetti'].map((tag) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => {
                        setQuery(tag);
                        handleSearch(tag, selectedCategory);
                      }}
                      className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-1 rounded-lg transition-colors font-medium"
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Filtro por Categorías */}
            {categories.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-xs font-bold text-slate-600 uppercase tracking-wider">
                  <Filter className="w-3.5 h-3.5 text-blue-600" />
                  <span>Filtrar por Categoría de Canasta:</span>
                </div>
                <CategoryFilter
                  categories={categories}
                  selectedCategory={selectedCategory}
                  onSelectCategory={(slug) => setSelectedCategory(slug)}
                />
              </div>
            )}

            {/* Grid de Resultados */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base sm:text-lg font-black text-slate-900 flex items-center space-x-2">
                  <ShoppingBag className="w-5 h-5 text-blue-600" />
                  <span>Resultados Comparados ({products.length})</span>
                </h2>
                <span className="text-xs font-semibold text-slate-500">
                  Precios calculados por $/kg y $/L
                </span>
              </div>

              {loading ? (
                <div className="py-20 text-center bg-white rounded-3xl border border-slate-200">
                  <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                  <p className="text-sm font-bold text-slate-700">Calculando similitud semántica con pgvector...</p>
                  <p className="text-xs text-slate-500 mt-1">Comparando precios en Jumbo, Lider, Santa Isabel y Unimarc</p>
                </div>
              ) : products.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                  {products.map((product) => (
                    <ProductCard
                      key={product.id}
                      product={product}
                      onViewComparison={(id) => setSelectedCanonicalId(id)}
                      onSetAlert={handleOpenAlert}
                    />
                  ))}
                </div>
              ) : (
                <div className="py-16 text-center bg-white rounded-3xl border border-slate-200 p-8 space-y-3">
                  <AlertCircle className="w-12 h-12 text-slate-400 mx-auto" />
                  <h3 className="text-base font-bold text-slate-800">No encontramos coincidencias directas</h3>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    Prueba buscando por términos generales como "carne", "leche", "arroz" o cambiando el filtro de categoría.
                  </p>
                </div>
              )}
            </div>
          </>
        ) : (
          <RadarAlternativoView />
        )}
      </main>

      {/* Modal de Detalle y Comparativa */}
      <ProductDetailModal
        canonicalId={selectedCanonicalId}
        onClose={() => setSelectedCanonicalId(null)}
        onSetAlert={(pName, cId, bPrice) => {
          setSelectedCanonicalId(null);
          setAlertModalState({
            isOpen: true,
            productName: pName,
            canonicalId: cId,
            currentBestPrice: bPrice
          });
        }}
      />

      {/* Modal de Alerta WhatsApp */}
      <AlertModal
        isOpen={alertModalState.isOpen}
        onClose={() => setAlertModalState((prev) => ({ ...prev, isOpen: false }))}
        productName={alertModalState.productName}
        canonicalId={alertModalState.canonicalId}
        currentBestPrice={alertModalState.currentBestPrice}
      />

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500 mt-12">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>🇨🇱 <strong>Ofertis Chile</strong> - Plataforma de Minería de Datos & Agentes IA</span>
          <span>PostgreSQL + pgvector • FastAPI • React + Vite</span>
        </div>
      </footer>
    </div>
  );
}
