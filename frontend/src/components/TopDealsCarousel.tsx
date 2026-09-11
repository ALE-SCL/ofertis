import React, { useRef } from 'react';
import { Flame, ChevronLeft, ChevronRight, Tag } from 'lucide-react';
import { ProductSearchResult } from '../types';
import mascotImg from '../assets/mascot_ofertis.jpg';

interface TopDealsCarouselProps {
  products: ProductSearchResult[];
  onViewComparison: (productId: number, format?: string) => void;
}

const CATEGORY_NAMES: Record<string, string> = {
  carne_vacuno: 'Carnes Vacuno',
  carne_pollo: 'Pollo y Aves',
  carne_cerdo: 'Carnes Cerdo',
  lacteos: 'Lácteos y Quesos',
  leche: 'Leches',
  despensa: 'Abarrotes y Despensa',
  fideos: 'Pastas y Fideos',
  arroz: 'Arroz y Legumbres',
  frutas_verduras: 'Frutas y Verduras',
  bebidas: 'Bebidas y Licores',
  limpieza: 'Limpieza y Aseo',
  panaderia: 'Panadería y Masas',
  fiambreria: 'Fiambrería y Cecinas',
  cuidado_personal: 'Cuidado Personal',
  mascotas: 'Mascotas',
};

export const TopDealsCarousel: React.FC<TopDealsCarouselProps> = ({
  products,
  onViewComparison
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Seleccionar exactamente 1 solo producto con el mayor descuento por cada categoría
  const dealsWithDiscount = React.useMemo(() => {
    const withDiscount = products.map((product) => {
      const discount = product.savings_percentage > 0 
        ? product.savings_percentage 
        : (product.max_unit_price > product.min_unit_price
            ? Math.round(((product.max_unit_price - product.min_unit_price) / product.max_unit_price) * 100)
            : 0);
      return { ...product, discount };
    });

    const bestByCategory = new Map<string, typeof withDiscount[0]>();
    for (const item of withDiscount) {
      if (item.discount <= 0) continue;
      const categoryKey = item.category || 'general';
      const existing = bestByCategory.get(categoryKey);
      if (!existing || item.discount > existing.discount) {
        bestByCategory.set(categoryKey, item);
      }
    }

    return Array.from(bestByCategory.values())
      .sort((a, b) => b.discount - a.discount);
  }, [products]);

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
      cardElement.classList.add('ring-4', 'ring-emerald-500');
      setTimeout(() => {
        cardElement.classList.remove('ring-4', 'ring-emerald-500');
      }, 2500);
    }
    onViewComparison(productId, format);
  };

  return (
    <section className="relative rounded-3xl p-1 bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 shadow-lg shadow-emerald-600/20 my-6">
      <div className="bg-gradient-to-b from-emerald-50/40 via-white to-white dark:from-stone-900 dark:via-stone-900 dark:to-stone-900 rounded-[22px] p-5 sm:p-6 transition-colors">
        {/* Encabezado destacado del Carrusel */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <img
                src={mascotImg}
                alt="Michito Ofertis"
                className="w-11 h-11 rounded-2xl object-cover border-2 border-emerald-500 shadow-md shadow-emerald-500/30"
              />
              <span className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-600 flex items-center justify-center text-white text-[10px] shadow-sm">
                <Flame className="w-2.5 h-2.5 animate-pulse" />
              </span>
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-black text-stone-900 dark:text-stone-100 tracking-tight flex items-center space-x-2">
                <span>Mayor Descuento por Categoría</span>
                <span className="text-[11px] font-bold text-emerald-800 dark:text-emerald-300 bg-emerald-100/90 dark:bg-emerald-950/70 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800 hidden sm:inline-block">
                  1 Oferta Estrella por Categoría
                </span>
              </h2>
            </div>
          </div>

          {/* Flechas de Navegación de Alto Contraste */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => scroll('left')}
              aria-label="Ofertas anteriores"
              className="w-8 h-8 rounded-full bg-white dark:bg-stone-800 hover:bg-emerald-600 dark:hover:bg-emerald-600 text-stone-700 dark:text-stone-200 hover:text-white dark:hover:text-white border border-stone-200 dark:border-stone-700 hover:border-emerald-600 dark:hover:border-emerald-600 shadow-sm flex items-center justify-center transition-all active:scale-90"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => scroll('right')}
              aria-label="Siguientes ofertas"
              className="w-8 h-8 rounded-full bg-white dark:bg-stone-800 hover:bg-emerald-600 dark:hover:bg-emerald-600 text-stone-700 dark:text-stone-200 hover:text-white dark:hover:text-white border border-stone-200 dark:border-stone-700 hover:border-emerald-600 dark:hover:border-emerald-600 shadow-sm flex items-center justify-center transition-all active:scale-90"
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
                className="w-44 sm:w-52 flex-shrink-0 snap-start bg-white dark:bg-stone-800/90 rounded-2xl border border-emerald-200/90 dark:border-stone-700/80 hover:border-emerald-500 dark:hover:border-emerald-400 shadow-xs hover:shadow-xl hover:shadow-emerald-500/10 transition-all duration-300 p-3 flex flex-col justify-between group cursor-pointer text-center relative overflow-hidden"
                title={`Ver comparativa de ${deal.name}`}
              >
                {/* Mascota Michito Ofertis en verde para las mejores ofertas */}
                <div className="absolute top-2.5 left-2.5 z-10 flex items-center space-x-1 bg-emerald-50/95 dark:bg-emerald-950/95 backdrop-blur-xs rounded-full p-0.5 pr-2 border border-emerald-300 dark:border-emerald-700 shadow-xs group-hover:scale-105 transition-transform">
                  <img
                    src={mascotImg}
                    alt="Michito Ofertis"
                    className="w-5 h-5 rounded-full object-cover border border-emerald-500"
                  />
                  <span className="text-[9px] font-black text-emerald-800 dark:text-emerald-200">
                    Ofertis
                  </span>
                </div>

                {/* Badge destacado de Porcentaje de Descuento en Verde */}
                <div className="absolute top-2.5 right-2.5 z-10 bg-gradient-to-r from-emerald-600 to-green-500 text-white text-[11px] font-black px-2 py-0.5 rounded-full shadow-md shadow-emerald-600/30 flex items-center space-x-1">
                  <Tag className="w-3 h-3" />
                  <span>-{deal.discount}%</span>
                </div>

                {/* Foto del Producto */}
                <div className="relative h-32 w-full bg-white dark:bg-stone-850 flex items-center justify-center p-2 mb-2 rounded-xl">
                  {deal.image_url ? (
                    <img
                      src={deal.image_url}
                      alt={deal.name}
                      className="h-full w-full object-contain object-center group-hover:scale-110 transition-transform duration-300"
                      loading="lazy"
                    />
                  ) : (
                    <div className="text-stone-300 dark:text-stone-600 text-xs font-medium">Sin imagen</div>
                  )}
                </div>

                {/* Información: Categoría, Nombre, Formato y Precio */}
                <div className="pt-1 border-t border-stone-100 dark:border-stone-750 flex flex-col justify-end">
                  <span className="text-[9px] uppercase font-black tracking-wider text-emerald-700 dark:text-emerald-400 block mb-0.5 truncate">
                    {CATEGORY_NAMES[deal.category] || deal.category.replace(/_/g, ' ')}
                  </span>

                  <h3 className="text-xs font-bold text-stone-800 dark:text-stone-200 line-clamp-1 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors mb-0.5">
                    {deal.name}
                  </h3>

                  <div className="flex items-center justify-center space-x-1.5 text-[10px] text-stone-500 dark:text-stone-400 mb-1">
                    <span className="font-bold">{deal.package_format}</span>
                    <span>•</span>
                    <span className="text-emerald-600 dark:text-emerald-400 font-semibold truncate max-w-[90px]">
                      {deal.best_supermarket_name.replace(/\s*\([^)]*\)/, '')}
                    </span>
                  </div>

                  {/* Precio destacado */}
                  <div className="text-base sm:text-lg font-black text-emerald-950 dark:text-emerald-100 group-hover:text-emerald-600 dark:group-hover:text-emerald-400">
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
