import React, { useRef } from 'react';
import { Flame, ChevronLeft, ChevronRight, ArrowRight, Tag, Bell } from 'lucide-react';
import { ProductSearchResult } from '../types';

interface TopDealsCarouselProps {
  products: ProductSearchResult[];
  onViewComparison: (productId: number) => void;
  onSetAlert?: (product: ProductSearchResult) => void;
}

export const TopDealsCarousel: React.FC<TopDealsCarouselProps> = ({
  products,
  onViewComparison,
  onSetAlert
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Calcular porcentaje de ahorro y ordenar de mayor a menor
  const dealsWithDiscount = products
    .map((product) => {
      const discount = product.max_unit_price > product.min_unit_price
        ? Math.round(((product.max_unit_price - product.min_unit_price) / product.max_unit_price) * 100)
        : 0;
      return { ...product, discount };
    })
    .filter((p) => p.discount >= 10) // Mostrar productos con al menos 10% de diferencia
    .sort((a, b) => b.discount - a.discount)
    .slice(0, 12); // Top 12 mejores ofertas

  if (dealsWithDiscount.length === 0) {
    return null;
  }

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const offset = direction === 'left' ? -340 : 340;
      scrollRef.current.scrollBy({ left: offset, behavior: 'smooth' });
    }
  };

  return (
    <section className="bg-gradient-to-r from-orange-50/60 via-amber-50/40 to-orange-50/60 rounded-3xl p-5 sm:p-6 border border-orange-200/70 shadow-xs relative overflow-hidden">
      {/* Encabezado del Carrusel */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-orange-600 to-amber-500 flex items-center justify-center text-white shadow-md shadow-orange-500/20">
            <Flame className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-black text-stone-900 tracking-tight flex items-center space-x-2">
              <span>Ofertas Imperdibles: Mayor Porcentaje de Descuento</span>
            </h2>
            <p className="text-xs text-stone-500 font-medium">
              Productos con mayor brecha de precio calculada entre Lider, Jumbo, Santa Isabel y Unimarc
            </p>
          </div>
        </div>

        {/* Flechas de Navegación */}
        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => scroll('left')}
            aria-label="Anterior"
            className="w-8 h-8 rounded-full bg-white hover:bg-orange-50 text-stone-700 hover:text-orange-600 border border-stone-200 hover:border-orange-300 shadow-xs flex items-center justify-center transition-all active:scale-90"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => scroll('right')}
            aria-label="Siguiente"
            className="w-8 h-8 rounded-full bg-white hover:bg-orange-50 text-stone-700 hover:text-orange-600 border border-stone-200 hover:border-orange-300 shadow-xs flex items-center justify-center transition-all active:scale-90"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Carrusel Desplazable */}
      <div
        ref={scrollRef}
        className="flex space-x-4 overflow-x-auto pb-3 pt-1 scroll-smooth custom-scrollbar snap-x snap-mandatory"
      >
        {dealsWithDiscount.map((deal) => (
          <div
            key={`deal-${deal.id}`}
            className="w-64 sm:w-72 flex-shrink-0 snap-start bg-white rounded-2xl border border-stone-200/90 hover:border-orange-300 shadow-xs hover:shadow-lg transition-all duration-300 flex flex-col justify-between overflow-hidden group"
          >
            {/* Imagen del producto con badge de descuento */}
            <div className="relative h-40 bg-white overflow-hidden flex items-center justify-center p-3 border-b border-stone-100">
              {deal.image_url ? (
                <img
                  src={deal.image_url}
                  alt={deal.name}
                  className="h-full w-full object-contain object-center group-hover:scale-105 transition-transform duration-300"
                  loading="lazy"
                />
              ) : (
                <div className="text-stone-400 text-xs font-medium">Sin imagen</div>
              )}

              {/* Tag de Descuento destacado */}
              <div className="absolute top-2.5 right-2.5 bg-gradient-to-r from-orange-600 to-amber-500 text-white text-[11px] font-black px-2.5 py-1 rounded-full shadow-md flex items-center space-x-1">
                <Tag className="w-3 h-3" />
                <span>-{deal.discount}% Ahorro</span>
              </div>

              {/* Categoría */}
              <div className="absolute bottom-2 left-2">
                <span className="text-[9px] uppercase font-bold tracking-wider bg-stone-900/75 backdrop-blur-sm text-white px-2 py-0.5 rounded-md">
                  {deal.category.replace('_', ' ')}
                </span>
              </div>
            </div>

            {/* Detalles */}
            <div className="p-3.5 flex-1 flex flex-col justify-between">
              <div>
                <span className="text-[11px] text-stone-500 font-medium block mb-0.5">
                  {deal.brand || 'Varias marcas'}
                </span>

                <h3 className="text-xs sm:text-sm font-bold text-stone-900 line-clamp-2 mb-2.5 min-h-[2.5rem] group-hover:text-orange-950 transition-colors">
                  {deal.name}
                </h3>

                {/* Precios normalizados */}
                <div className="bg-orange-50/50 rounded-xl p-2.5 border border-orange-100/80 mb-3">
                  <div className="flex items-baseline justify-between">
                    <div>
                      <span className="text-[9px] font-bold uppercase tracking-wider text-orange-800">
                        Mejor Precio:
                      </span>
                      <div className="text-base sm:text-lg font-black text-stone-900">
                        ${Math.round(deal.min_unit_price).toLocaleString('es-CL')}
                        <span className="text-[11px] font-semibold text-stone-500 ml-0.5">
                          / {deal.standard_unit}
                        </span>
                      </div>
                    </div>

                    <div className="text-right">
                      <span className="text-[10px] text-stone-400 line-through block">
                        Hasta ${Math.round(deal.max_unit_price).toLocaleString('es-CL')}
                      </span>
                      <span className="text-[10px] font-extrabold text-orange-700 bg-orange-100/80 px-1.5 py-0.5 rounded">
                        -{deal.discount}%
                      </span>
                    </div>
                  </div>

                  <div className="mt-1.5 pt-1.5 border-t border-orange-100/60 text-[11px] flex items-center justify-between">
                    <span className="text-stone-500 font-medium">Más conveniente:</span>
                    <span className="font-bold text-stone-800">
                      {deal.best_supermarket_name}
                    </span>
                  </div>
                </div>
              </div>

              {/* Botones de acción */}
              <div className="grid grid-cols-2 gap-1.5 pt-1 border-t border-stone-100">
                <button
                  onClick={() => onViewComparison(deal.id)}
                  className="w-full flex items-center justify-center space-x-1 bg-orange-600 hover:bg-orange-500 active:scale-95 text-white font-bold py-2 px-2.5 rounded-xl text-xs transition-all shadow-xs"
                >
                  <span>Comparar</span>
                  <ArrowRight className="w-3 h-3" />
                </button>

                {onSetAlert ? (
                  <button
                    onClick={() => onSetAlert(deal)}
                    className="w-full flex items-center justify-center space-x-1 bg-white hover:bg-orange-50 text-orange-800 border border-orange-200 hover:border-orange-300 font-bold py-2 px-2 rounded-xl text-xs transition-all"
                  >
                    <Bell className="w-3 h-3 text-orange-600" />
                    <span>Alerta</span>
                  </button>
                ) : (
                  <button
                    onClick={() => onViewComparison(deal.id)}
                    className="w-full flex items-center justify-center space-x-1 bg-stone-100 hover:bg-stone-200 text-stone-700 font-bold py-2 px-2.5 rounded-xl text-xs transition-all"
                  >
                    <span>Ver detalle</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
