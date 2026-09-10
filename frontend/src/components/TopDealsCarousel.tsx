import React, { useRef } from 'react';
import { Flame, ChevronLeft, ChevronRight, Tag } from 'lucide-react';
import { ProductSearchResult } from '../types';

interface TopDealsCarouselProps {
  products: ProductSearchResult[];
  onViewComparison: (productId: number, format?: string) => void;
}

export const TopDealsCarousel: React.FC<TopDealsCarouselProps> = ({
  products,
  onViewComparison
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Calcular porcentaje de ahorro y ordenar de mayor a menor
  const dealsWithDiscount = products
    .map((product) => {
      const discount = product.savings_percentage > 0 
        ? product.savings_percentage 
        : (product.max_unit_price > product.min_unit_price
            ? Math.round(((product.max_unit_price - product.min_unit_price) / product.max_unit_price) * 100)
            : 0);
      return { ...product, discount };
    })
    .filter((p) => p.discount >= 10)
    .sort((a, b) => b.discount - a.discount)
    .slice(0, 14);

  if (dealsWithDiscount.length === 0) {
    return null;
  }

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const offset = direction === 'left' ? -300 : 300;
      scrollRef.current.scrollBy({ left: offset, behavior: 'smooth' });
    }
  };

  const handleCardClick = (e: React.MouseEvent, productId: number, format?: string) => {
    e.preventDefault();
    const cardElement = document.getElementById(`product-${productId}`);
    if (cardElement) {
      cardElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      cardElement.classList.add('ring-4', 'ring-orange-500');
      setTimeout(() => {
        cardElement.classList.remove('ring-4', 'ring-orange-500');
      }, 2500);
    }
    onViewComparison(productId, format);
  };

  return (
    <section className="relative rounded-3xl p-1 bg-gradient-to-r from-orange-500 via-amber-500 to-orange-600 shadow-lg shadow-orange-500/15 my-6">
      <div className="bg-gradient-to-b from-orange-50/50 via-white to-white rounded-[22px] p-5 sm:p-6">
        {/* Encabezado destacado del Carrusel */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2.5">
            <span className="w-9 h-9 rounded-2xl bg-orange-600 flex items-center justify-center text-white shadow-md shadow-orange-500/30">
              <Flame className="w-5 h-5 animate-pulse" />
            </span>
            <div>
              <h2 className="text-base sm:text-lg font-black text-stone-900 tracking-tight flex items-center space-x-2">
                <span>Mayor Porcentaje de Descuento</span>
                <span className="text-[11px] font-bold text-orange-700 bg-orange-100/90 px-2 py-0.5 rounded-full border border-orange-200 hidden sm:inline-block">
                  Carrusel de Oportunidades
                </span>
              </h2>
            </div>
          </div>

          {/* Flechas de Navegación de Alto Contraste */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => scroll('left')}
              aria-label="Ofertas anteriores"
              className="w-8 h-8 rounded-full bg-white hover:bg-orange-600 text-stone-700 hover:text-white border border-stone-200 hover:border-orange-600 shadow-sm flex items-center justify-center transition-all active:scale-90"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => scroll('right')}
              aria-label="Siguientes ofertas"
              className="w-8 h-8 rounded-full bg-white hover:bg-orange-600 text-stone-700 hover:text-white border border-stone-200 hover:border-orange-600 shadow-sm flex items-center justify-center transition-all active:scale-90"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Carrusel Desplazable con Tarjetas Minimalistas */}
        <div
          ref={scrollRef}
          className="flex space-x-3.5 overflow-x-auto pb-2 pt-1 scroll-smooth custom-scrollbar snap-x snap-mandatory"
        >
          {dealsWithDiscount.map((deal) => {
            const price = deal.best_package_price > 0 ? deal.best_package_price : deal.min_unit_price;
            return (
              <a
                key={`deal-${deal.id}-${deal.package_format}`}
                href={`#product-${deal.id}`}
                onClick={(e) => handleCardClick(e, deal.id, deal.package_format)}
                className="w-44 sm:w-52 flex-shrink-0 snap-start bg-white rounded-2xl border border-stone-200/90 hover:border-orange-500 shadow-xs hover:shadow-xl transition-all duration-300 p-3 flex flex-col justify-between group cursor-pointer text-center relative overflow-hidden"
                title={`Ver comparativa de ${deal.name}`}
              >
                {/* Badge destacado de Porcentaje de Descuento */}
                <div className="absolute top-2.5 right-2.5 z-10 bg-gradient-to-r from-orange-600 to-amber-500 text-white text-[11px] font-black px-2 py-0.5 rounded-full shadow-md flex items-center space-x-1">
                  <Tag className="w-3 h-3" />
                  <span>-{deal.discount}%</span>
                </div>

                {/* Foto del Producto */}
                <div className="relative h-32 w-full bg-white flex items-center justify-center p-2 mb-2">
                  {deal.image_url ? (
                    <img
                      src={deal.image_url}
                      alt={deal.name}
                      className="h-full w-full object-contain object-center group-hover:scale-110 transition-transform duration-300"
                      loading="lazy"
                    />
                  ) : (
                    <div className="text-stone-300 text-xs font-medium">Sin imagen</div>
                  )}
                </div>

                {/* Información mínima: Nombre, Formato y Precio */}
                <div className="pt-1 border-t border-stone-100 flex flex-col justify-end">
                  <h3 className="text-xs font-bold text-stone-800 line-clamp-1 group-hover:text-orange-600 transition-colors mb-0.5">
                    {deal.name}
                  </h3>

                  <span className="text-[10px] font-bold text-stone-500 mb-1">
                    {deal.package_format}
                  </span>

                  {/* Precio destacado */}
                  <div className="text-base sm:text-lg font-black text-stone-900 group-hover:text-orange-950">
                    ${Math.round(price).toLocaleString('es-CL')}
                  </div>
                </div>
              </a>
            );
          })}
        </div>
      </div>
    </section>
  );
};
