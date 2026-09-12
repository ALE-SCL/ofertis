import React, { useState, useEffect } from 'react';
import { Search, Filter, AlertCircle, ShoppingBag, RefreshCw } from 'lucide-react';
import axios from 'axios';
import { Navbar } from './components/Navbar';
import { MiningStatsBanner } from './components/MiningStatsBanner';
import { CategoryFilter } from './components/CategoryFilter';
import { ProductCard } from './components/ProductCard';
import { TopDealsCarousel } from './components/TopDealsCarousel';
import { ProductDetailModal } from './components/ProductDetailModal';
import { AlertModal } from './components/AlertModal';
import { RadarAlternativoView } from './components/RadarAlternativoView';
import { ProductSearchResult, CategoryItem, MiningStats } from './types';
import { Target, Store, TrendingUp } from 'lucide-react';
import { AlzaPreciosBlog } from './components/AlzaPreciosBlog';
import logoImg from './assets/logo_ofertis.jpg';
import michitoDetectiveImg from './assets/michito_ofertis_detective.jpg';
import { API_BASE_URL } from './config/api';

export function App() {
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('ofertis_theme');
      if (saved) return saved === 'dark';
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  });

  const toggleDarkMode = () => {
    setIsDarkMode((prev) => {
      const next = !prev;
      if (next) {
        document.documentElement.classList.add('dark');
        try { localStorage.setItem('ofertis_theme', 'dark'); } catch (_) {}
      } else {
        document.documentElement.classList.remove('dark');
        try { localStorage.setItem('ofertis_theme', 'light'); } catch (_) {}
      }
      return next;
    });
  };

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const [activeTab, setActiveTab] = useState<'retail' | 'radar' | 'alza-precios'>(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const tabParam = params.get('tab');
      if (params.get('article') || tabParam === 'alza-precios') {
        return 'alza-precios';
      }
      if (tabParam === 'radar') return 'radar';
    }
    return 'retail';
  });

  const handleTabChange = (tab: 'retail' | 'radar' | 'alza-precios') => {
    setActiveTab(tab);
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href);
      if (tab === 'retail') {
        url.searchParams.delete('tab');
        url.searchParams.delete('article');
      } else if (tab === 'radar') {
        url.searchParams.set('tab', 'radar');
        url.searchParams.delete('article');
      } else if (tab === 'alza-precios') {
        url.searchParams.set('tab', 'alza-precios');
      }
      window.history.pushState({}, '', url.toString());
    }
  };

  useEffect(() => {
    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      if (params.get('article') || params.get('tab') === 'alza-precios') {
        setActiveTab('alza-precios');
      } else if (params.get('tab') === 'radar') {
        setActiveTab('radar');
      } else {
        setActiveTab('retail');
      }
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const [query, setQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('todos');
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [products, setProducts] = useState<ProductSearchResult[]>([]);
  const [topDeals, setTopDeals] = useState<ProductSearchResult[]>([]);
  const [stats, setStats] = useState<MiningStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  // Estados de Modales
  const [selectedCanonicalId, setSelectedCanonicalId] = useState<number | null>(null);
  const [selectedFormat, setSelectedFormat] = useState<string | null>(null);
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

  // Cargar categorías, estadísticas y mejores ofertas por categoría
  useEffect(() => {
    const fetchInitialMetadata = async () => {
      try {
        const [catRes, statRes, dealsRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/products/categories`),
          axios.get(`${API_BASE_URL}/mining/stats`),
          axios.get(`${API_BASE_URL}/products/top-deals-by-category`)
        ]);
        setCategories(catRes.data);
        setStats(statRes.data);
        setTopDeals(dealsRes.data);
      } catch (err) {
        console.error('Error cargando metadata:', err);
      }
    };

    fetchInitialMetadata();
  }, []);

  // Ejecutar búsqueda o exploración del catálogo con paginación
  const handleSearch = async (searchTerm: string, catSlug: string, isAppend: boolean = false) => {
    if (isAppend) {
      setLoadingMore(true);
    } else {
      setLoading(true);
    }

    const currentOffset = isAppend ? offset + 36 : 0;

    try {
      const res = await axios.get(`${API_BASE_URL}/products/search`, {
        params: {
          q: searchTerm.trim() || undefined,
          category: catSlug !== 'todos' ? catSlug : undefined,
          limit: 36,
          offset: currentOffset
        },
        timeout: 20000
      });

      if (isAppend) {
        setProducts((prev) => [...prev, ...res.data]);
        setOffset(currentOffset);
      } else {
        setProducts(res.data);
        setOffset(0);
      }

      setHasMore(res.data.length === 36);
    } catch (err) {
      console.error('Error buscando productos:', err);
    } finally {
      setLoading(false);
      setLoadingMore(false);
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
      setHasMore(false);
      // Actualizar estadísticas del banner y carrusel de ofertas
      const [statRes, dealsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/mining/stats`),
        axios.get(`${API_BASE_URL}/products/top-deals-by-category`)
      ]);
      setStats(statRes.data);
      setTopDeals(dealsRes.data);
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
    <div className="min-h-screen flex flex-col bg-[#FAFAFA] dark:bg-stone-950 text-stone-900 dark:text-stone-100 transition-colors duration-200">
      <Navbar
        isDarkMode={isDarkMode}
        onToggleDarkMode={toggleDarkMode}
        onOpenMyAlerts={() => alert('Ingresa tu número en el botón de Alerta WhatsApp de cualquier producto para ver tus alertas.')}
        activeTab={activeTab}
        onSelectTab={handleTabChange}
      />
      <MiningStatsBanner stats={stats} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-6">
        {/* Navigation Tabs: Retail Tradicional vs Radar Alternativo vs Alza de Precios (Blog Sentinela) */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 bg-white dark:bg-stone-900 p-2 sm:p-2.5 rounded-2xl border border-stone-200/80 dark:border-stone-800 shadow-xs">
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => handleTabChange('retail')}
              className={`flex-1 sm:flex-none flex items-center justify-center space-x-2.5 px-5 py-2.5 rounded-xl font-bold text-sm transition-all ${
                activeTab === 'retail'
                  ? 'bg-orange-600 text-white shadow-md shadow-orange-500/20'
                  : 'text-stone-600 dark:text-stone-300 hover:text-stone-900 dark:hover:text-white hover:bg-stone-100 dark:hover:bg-stone-800'
              }`}
            >
              <Store className="w-4 h-4" />
              <span>Supermercados & Mayoristas</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                activeTab === 'retail' ? 'bg-orange-700 text-orange-100' : 'bg-stone-200 dark:bg-stone-800 text-stone-700 dark:text-stone-300'
              }`}>
                10 Cadenas
              </span>
            </button>

            <button
              onClick={() => handleTabChange('radar')}
              className={`flex-1 sm:flex-none flex items-center justify-center space-x-2.5 px-5 py-2.5 rounded-xl font-bold text-sm transition-all ${
                activeTab === 'radar'
                  ? 'bg-gradient-to-r from-orange-600 to-amber-600 text-white shadow-md shadow-orange-500/20'
                  : 'text-stone-600 dark:text-stone-300 hover:text-stone-900 dark:hover:text-white hover:bg-stone-100 dark:hover:bg-stone-800'
              }`}
            >
              <Target className="w-4 h-4" />
              <span>Radar Alternativo</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                activeTab === 'radar' ? 'bg-orange-700 text-white' : 'bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300 border border-orange-200 dark:border-orange-800'
              }`}>
                Hasta 65% Ahorro
              </span>
            </button>

            <button
              onClick={() => handleTabChange('alza-precios')}
              className={`flex-1 sm:flex-none flex items-center justify-center space-x-2.5 px-5 py-2.5 rounded-xl font-bold text-sm transition-all cursor-pointer ${
                activeTab === 'alza-precios'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/25'
                  : 'text-stone-600 dark:text-stone-300 hover:text-emerald-700 dark:hover:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/40'
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              <span>Alza de Precios</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                activeTab === 'alza-precios' ? 'bg-emerald-800 text-white' : 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
              }`}>
                Blog Sentinela
              </span>
            </button>
          </div>

          <div className="text-xs text-stone-500 dark:text-stone-400 px-3 hidden lg:block">
            {activeTab === 'retail' 
              ? 'Precios y ofertas en 10 cadenas y mayoristas de Chile' 
              : activeTab === 'radar'
              ? 'Canales mayoristas y ferias directas'
              : 'Auditoría preventiva de inflación con el Sentinela'}
          </div>
        </div>

        {activeTab === 'retail' ? (
          <>
            {/* Hero & Buscador con Michito Ofertis Detective al lado derecho */}
            <div className="bg-white dark:bg-stone-900 rounded-3xl p-6 sm:p-8 border border-orange-100/80 dark:border-stone-800 shadow-xs relative overflow-hidden">
              <div className="flex flex-col lg:flex-row items-center justify-between gap-6 lg:gap-8">
                {/* Columna Izquierda: Textos, Formulario de Búsqueda y Sugerencias */}
                <div className="flex-1 w-full max-w-3xl">
                  <h1 className="text-2xl sm:text-3xl font-black text-stone-900 dark:text-stone-100 tracking-tight">
                    Encuentra el precio más conveniente de tu canasta
                  </h1>

                  <p className="text-sm sm:text-base text-stone-600 dark:text-stone-400 mt-1.5">
                    Precios actualizados y normalizados por unidad ($/kg y $/L) para comparar el valor real entre envases y marcas.
                  </p>

                  {/* Input de Búsqueda */}
                  <form onSubmit={onSearchSubmit} className="mt-6 flex flex-col sm:flex-row gap-3">
                    <div className="relative flex-1">
                      <Search className="w-5 h-5 text-stone-400 absolute left-4 top-3.5" />
                      <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="¿Qué necesitas comprar hoy? (ej: 'leche colun', 'lomo liso', 'posta negra', 'arroz grado 1', 'aceite', 'fideos')..."
                        className="w-full pl-12 pr-4 py-3.5 rounded-2xl bg-stone-50 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 text-sm font-medium text-stone-900 dark:text-stone-100 placeholder-stone-400 dark:placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 focus:bg-white dark:focus:bg-stone-850 transition-all shadow-inner"
                      />
                    </div>

                    <button
                      type="submit"
                      className="bg-orange-600 hover:bg-orange-500 active:scale-95 text-white font-extrabold px-6 py-3.5 rounded-2xl text-sm transition-all shadow-md shadow-orange-500/20 flex items-center justify-center space-x-2"
                    >
                      <span>Buscar Mejor Precio</span>
                    </button>

                    <button
                      type="button"
                      onClick={handleLiveRefresh}
                      disabled={loading}
                      title="Consulta en tiempo real los precios oficiales de Jumbo, Santa Isabel, Unimarc y Lider"
                      className="bg-white dark:bg-stone-800 hover:bg-orange-50 dark:hover:bg-stone-700 active:scale-95 text-orange-700 dark:text-orange-400 border border-orange-200 dark:border-stone-700 hover:border-orange-300 dark:hover:border-stone-600 font-extrabold px-5 py-3.5 rounded-2xl text-sm transition-all shadow-xs flex items-center justify-center space-x-2 disabled:opacity-50"
                    >
                      <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                      <span>Comprobar Precios de Hoy</span>
                    </button>
                  </form>

                  {/* Sugerencias rápidas */}
                  <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-stone-500 dark:text-stone-400">
                    <span className="font-semibold">Sugerencias:</span>
                    {['Lomo Liso', 'Posta Negra', 'Pechuga Pollo', 'Leche Colun', 'Arroz Tucapel', 'Spaghetti'].map((tag) => (
                      <button
                        key={tag}
                        type="button"
                        onClick={() => {
                          setQuery(tag);
                          handleSearch(tag, selectedCategory);
                        }}
                        className="bg-stone-100 dark:bg-stone-800 hover:bg-orange-50 dark:hover:bg-stone-700 hover:text-orange-700 dark:hover:text-orange-300 border border-transparent dark:border-stone-700 text-stone-700 dark:text-stone-300 px-2.5 py-1 rounded-lg transition-all font-medium"
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Columna Derecha: Ilustración de Michito Ofertis */}
                <div className="shrink-0 flex flex-col items-center justify-center pt-2 lg:pt-0">
                  <div className="relative group">
                    <div className="absolute -inset-1.5 bg-gradient-to-r from-orange-400/30 via-amber-400/25 to-orange-500/30 rounded-3xl blur-md group-hover:opacity-100 transition duration-300"></div>
                    <div className="relative bg-white dark:bg-stone-850 p-2 sm:p-2.5 rounded-3xl border border-orange-200/90 dark:border-stone-700 shadow-md">
                      <img
                        src={michitoDetectiveImg}
                        alt="Michito Ofertis rastreando precios en góndola"
                        className="w-56 h-40 sm:w-64 sm:h-48 md:w-72 md:h-52 object-contain rounded-2xl group-hover:scale-105 transition-transform duration-300"
                      />
                      <div className="absolute -bottom-2.5 left-1/2 -translate-x-1/2 bg-gradient-to-r from-orange-600 to-amber-600 text-white text-[11px] font-black px-3.5 py-0.5 rounded-full shadow-md whitespace-nowrap flex items-center space-x-1.5 border border-orange-300/40">
                        <span>🔍 Rastreador en Vivo</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Carrusel con Mejores Ofertas y Mayor Porcentaje de Descuento (1 por Categoría) */}
            <TopDealsCarousel
              products={topDeals.length > 0 ? topDeals : products}
              onViewComparison={(id, fmt) => {
                setSelectedCanonicalId(id);
                setSelectedFormat(fmt || null);
              }}
            />

            {/* Filtro por Categorías */}
            {categories.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-xs font-bold text-stone-700 dark:text-stone-300 uppercase tracking-wider">
                  <Filter className="w-3.5 h-3.5 text-orange-600" />
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
                <h2 className="text-base sm:text-lg font-black text-stone-900 dark:text-stone-100 flex items-center space-x-2">
                  <ShoppingBag className="w-5 h-5 text-orange-600" />
                  <span>Resultados Comparados ({products.length})</span>
                </h2>
                <span className="text-xs font-semibold text-stone-500 dark:text-stone-400">
                  Precios por formato y valor de referencia
                </span>
              </div>

              {loading ? (
                <div className="py-20 text-center bg-white dark:bg-stone-900 rounded-3xl border border-stone-200 dark:border-stone-800 shadow-xs">
                  <div className="w-12 h-12 border-4 border-orange-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                  <p className="text-sm font-bold text-stone-700 dark:text-stone-200">Consultando catálogo y similitud semántica con pgvector...</p>
                  <p className="text-xs text-stone-500 dark:text-stone-400 mt-1">Comparando precios en Jumbo, Lider, Santa Isabel y Unimarc</p>
                  <p className="text-[11px] text-stone-400 dark:text-stone-500 mt-2 italic">Si el servidor en la nube estaba en reposo, puede demorar unos segundos en responder.</p>
                </div>
              ) : products.length > 0 ? (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                  {products.map((product) => (
                    <ProductCard
                      key={`${product.id}-${product.package_format}`}
                      product={product}
                      onViewComparison={(id, fmt) => {
                        setSelectedCanonicalId(id);
                        setSelectedFormat(fmt || null);
                      }}
                      onSetAlert={handleOpenAlert}
                    />
                  ))}
                </div>

                {hasMore && (
                  <div className="text-center pt-8 pb-4">
                    <button
                      onClick={() => handleSearch(query, selectedCategory, true)}
                      disabled={loadingMore}
                      className="inline-flex items-center space-x-2 bg-white dark:bg-stone-900 hover:bg-orange-50/70 dark:hover:bg-stone-800 text-stone-800 dark:text-stone-200 border border-stone-300 dark:border-stone-700 hover:border-orange-300 dark:hover:border-orange-500 font-bold px-7 py-3.5 rounded-2xl shadow-xs hover:shadow-md transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                    >
                      {loadingMore ? (
                        <>
                          <div className="w-4 h-4 border-2 border-orange-600 border-t-transparent rounded-full animate-spin"></div>
                          <span>Cargando más productos...</span>
                        </>
                      ) : (
                        <>
                          <span>Cargar más productos del catálogo</span>
                          <span className="text-xs text-orange-700 dark:text-orange-400 font-bold bg-orange-50 dark:bg-orange-950/60 border border-orange-200 dark:border-orange-800 px-2 py-0.5 rounded-full">
                            {products.length} mostrados
                          </span>
                        </>
                      )}
                    </button>
                  </div>
                )}
              </>
              ) : (
                <div className="py-16 text-center bg-white dark:bg-stone-900 rounded-3xl border border-stone-200 dark:border-stone-800 p-8 space-y-3">
                  <AlertCircle className="w-12 h-12 text-stone-400 mx-auto" />
                  <h3 className="text-base font-bold text-stone-800 dark:text-stone-200">No encontramos coincidencias directas</h3>
                  <p className="text-xs text-stone-500 dark:text-stone-400 max-w-md mx-auto">
                    Prueba buscando por términos generales como "carne", "leche", "arroz" o cambiando el filtro de categoría.
                  </p>
                </div>
              )}
            </div>
          </>
        ) : activeTab === 'radar' ? (
          <RadarAlternativoView />
        ) : (
          <AlzaPreciosBlog
            onSearchProduct={(searchQuery: string) => {
              handleTabChange('retail');
              setQuery(searchQuery);
              setSelectedCategory('todos');
              handleSearch(searchQuery, 'todos');
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
          />
        )}
      </main>

      {/* Modal de Detalle y Comparativa */}
      <ProductDetailModal
        canonicalId={selectedCanonicalId}
        format={selectedFormat}
        onClose={() => {
          setSelectedCanonicalId(null);
          setSelectedFormat(null);
        }}
        onSetAlert={(pName, cId, bPrice) => {
          setSelectedCanonicalId(null);
          setSelectedFormat(null);
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
      <footer className="bg-white dark:bg-stone-900 border-t border-stone-200 dark:border-stone-800 py-6 text-center text-xs text-stone-500 dark:text-stone-400 mt-12 transition-colors">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <img src={logoImg} alt="Ofertis" className="h-14 w-auto object-contain rounded-lg" />
            <span className="text-stone-600 dark:text-stone-300 font-medium">El buscador de ofertas que alimenta tu ahorro</span>
          </div>
          <span>PostgreSQL + pgvector • FastAPI • React + Vite</span>
        </div>
      </footer>

      {/* Asistente Flotante Michito Ofertis al lado derecho inferior */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          title="Buscar ofertas con Michito Ofertis"
          className="group relative flex items-center bg-white/95 dark:bg-stone-900/95 backdrop-blur-md p-1.5 pr-3.5 rounded-full border-2 border-orange-500 shadow-xl shadow-orange-500/25 hover:scale-105 active:scale-95 transition-all duration-300"
        >
          <img
            src={michitoDetectiveImg}
            alt="Michito Ofertis"
            className="w-10 h-10 rounded-full object-contain bg-white dark:bg-stone-800 p-0.5 border border-orange-200 dark:border-stone-700"
          />
          <div className="ml-2 text-left hidden sm:block">
            <div className="text-[10px] font-black text-orange-600 dark:text-orange-400 leading-tight">
              Michito Ofertis
            </div>
            <div className="text-[10px] font-bold text-stone-600 dark:text-stone-300 leading-tight">
              Subir al buscador 🔍
            </div>
          </div>
        </button>
      </div>
    </div>
  );
}
