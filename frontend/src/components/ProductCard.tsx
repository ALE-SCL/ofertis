import React from 'react';
import { ArrowRight, Bell, Tag, CheckCircle2 } from 'lucide-react';
import { ProductSearchResult } from '../types';
import mascotImg from '../assets/mascot_ofertis.jpg';

interface ProductCardProps {
  product: ProductSearchResult;
  onViewComparison: (productId: number, format?: string) => void;
  onSetAlert: (product: ProductSearchResult) => void;
}

const SUPERMARKET_BADGE_STYLE: Record<string, string> = {
  lider: 'bg-blue-50 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-800',
  jumbo: 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
  santaisabel: 'bg-rose-50 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 border-rose-200 dark:border-rose-800',
  unimarc: 'bg-red-50 dark:bg-red-950/60 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800',
  alvi: 'bg-sky-50 dark:bg-sky-950/60 text-sky-800 dark:text-sky-300 border-sky-200 dark:border-sky-800',
  central_mayorista: 'bg-orange-50 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300 border-orange-200 dark:border-orange-800',
  mayorista10: 'bg-red-50 dark:bg-red-950/60 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800',
  acuenta: 'bg-yellow-50 dark:bg-yellow-950/60 text-yellow-800 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800',
  dona_carne: 'bg-amber-50 dark:bg-amber-950/60 text-amber-900 dark:text-amber-300 border-amber-200 dark:border-amber-800',
  el_carnicero: 'bg-rose-50 dark:bg-rose-950/60 text-rose-900 dark:text-rose-300 border-rose-200 dark:border-rose-800'
};

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  onViewComparison,
  onSetAlert
}) => {
  const savings = product.savings_percentage > 0
    ? product.savings_percentage
    : (product.max_unit_price > product.min_unit_price
        ? Math.round(((product.max_unit_price - product.min_unit_price) / product.max_unit_price) * 100)
        : 0);

  const hasMichi = savings >= 20;
  const badgeClass = SUPERMARKET_BADGE_STYLE[product.best_supermarket_slug] || 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
  const displayPackagePrice = product.best_package_price > 0 ? product.best_package_price : product.min_unit_price;

  return (
    <div
      id={`product-${product.id}`}
      className={`bg-white dark:bg-stone-900 rounded-2xl border transition-all duration-300 flex flex-col overflow-hidden group scroll-mt-24 ${
        hasMichi
          ? 'border-emerald-400 dark:border-emerald-600/80 shadow-md shadow-emerald-500/10 hover:shadow-xl hover:border-emerald-500'
          : 'border-stone-200/80 dark:border-stone-800 shadow-xs hover:shadow-lg hover:border-orange-300 dark:hover:border-orange-500'
      }`}
    >
      {/* Imagen & Tag de Ahorro */}
      <div className="relative h-48 bg-white dark:bg-stone-850 overflow-hidden flex items-center justify-center p-3 border-b border-stone-100 dark:border-stone-800">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="h-full w-full object-contain object-center group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        ) : (
          <div className="text-stone-400 dark:text-stone-500 text-sm font-medium">Sin imagen disponible</div>
        )}

        {/* Sello de Mascota Ofertis en verde para identificar las mayores ofertas */}
        {hasMichi && (
          <div className="absolute top-2.5 left-2.5 z-10 flex items-center space-x-1.5 bg-emerald-50/95 dark:bg-emerald-950/95 backdrop-blur-xs rounded-full p-1 pr-2.5 border border-emerald-300 dark:border-emerald-700 shadow-md group-hover:scale-105 transition-transform">
            <img
              src={mascotImg}
              alt="Michito Ofertis"
              className="w-6 h-6 rounded-full object-cover border-2 border-emerald-500 shadow-xs"
            />
            <span className="text-[10px] font-black text-emerald-800 dark:text-emerald-200 tracking-tight">
              Gran Oferta
            </span>
          </div>
        )}

        {savings > 5 && (
          <div
            className={`absolute top-2.5 right-2.5 text-white text-[11px] font-extrabold px-2.5 py-1 rounded-full shadow-md flex items-center space-x-1 ${
              hasMichi
                ? 'bg-gradient-to-r from-emerald-600 to-green-500 shadow-emerald-600/30'
                : 'bg-gradient-to-r from-orange-600 to-amber-500 shadow-orange-500/20'
            }`}
          >
            <Tag className="w-3 h-3" />
            <span>Ahorra {savings}%</span>
          </div>
        )}

        <div className="absolute bottom-2.5 left-2.5">
          <span className="text-[10px] uppercase font-bold tracking-wider bg-stone-900/80 dark:bg-stone-950/90 backdrop-blur-sm text-white px-2 py-0.5 rounded-md">
            {product.category.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Contenido */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-xs text-stone-500 dark:text-stone-400 mb-1">
            <span className="font-medium text-stone-600 dark:text-stone-300">{product.brand || 'Varias marcas'}</span>
            {product.subcategory && (
              <span className="bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 px-2 py-0.5 rounded-md font-medium text-[10px]">
                {product.subcategory.replace('_', ' ')}
              </span>
            )}
          </div>

          <h3
            className={`text-sm sm:text-base font-bold text-stone-900 dark:text-stone-100 line-clamp-2 mb-2 transition-colors ${
              hasMichi
                ? 'group-hover:text-emerald-600 dark:group-hover:text-emerald-400'
                : 'group-hover:text-orange-600 dark:group-hover:text-orange-400'
            }`}
          >
            {product.name}
          </h3>

          {/* Bloque de Precios con Formato Real */}
          <div
            className={`rounded-xl p-3 mb-3 border ${
              hasMichi
                ? 'bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-200/80 dark:border-emerald-800/50'
                : 'bg-orange-50/40 dark:bg-stone-800/60 border-orange-100/70 dark:border-stone-700/60'
            }`}
          >
            {/* Badge obligatorio: Precio más barato */}
            <div className="flex items-center justify-between mb-2">
              <span className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg font-black text-[11px] border shadow-2xs ${badgeClass}`}>
                <span>★ Precio más barato: {product.best_supermarket_name}</span>
              </span>
              {product.savings_amount > 0 && (
                <span
                  className={`text-[11px] font-bold px-2 py-0.5 rounded-md ${
                    hasMichi
                      ? 'text-emerald-800 dark:text-emerald-200 bg-emerald-100/90 dark:bg-emerald-900/60'
                      : 'text-orange-700 dark:text-orange-300 bg-orange-100/90 dark:bg-orange-950/70'
                  }`}
                >
                  -${Math.round(product.savings_amount).toLocaleString('es-CL')}
                </span>
              )}
            </div>

            {/* Precio Principal Grande del Formato Real */}
            <div className="flex items-baseline justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-stone-500 dark:text-stone-400 block mb-0.5">
                  Precio a pagar:
                </span>
                <div className="text-2xl sm:text-3xl font-black text-stone-900 dark:text-stone-100 tracking-tight flex items-baseline space-x-1.5">
                  <span className={hasMichi ? 'text-emerald-950 dark:text-emerald-100' : ''}>
                    ${Math.round(displayPackagePrice).toLocaleString('es-CL')}
                  </span>
                  <span className="text-xs font-bold text-stone-700 dark:text-stone-300 bg-stone-100 dark:bg-stone-700 px-2 py-0.5 rounded-md border border-stone-200/80 dark:border-stone-600">
                    {product.package_format}
                  </span>
                </div>
              </div>

              {product.highest_package_price > product.best_package_price && (
                <div className="text-right">
                  <span className="text-[10px] text-stone-400 dark:text-stone-500 block">Hasta</span>
                  <span className="text-xs text-stone-400 dark:text-stone-500 line-through font-medium">
                    ${Math.round(product.highest_package_price).toLocaleString('es-CL')}
                  </span>
                </div>
              )}
            </div>

            {/* Precio Secundario de Referencia ($/kg o $/L) */}
            <div
              className={`mt-2 flex items-center justify-between pt-2 border-t text-xs ${
                hasMichi
                  ? 'border-emerald-200/70 dark:border-emerald-800/40'
                  : 'border-orange-100/70 dark:border-stone-700/60'
              }`}
            >
              <span className="text-stone-500 dark:text-stone-400 font-medium">
                Ref. normalizada:
              </span>
              <span className="font-bold text-stone-700 dark:text-stone-200">
                ${Math.round(product.min_unit_price).toLocaleString('es-CL')} / {product.standard_unit}
              </span>
            </div>
          </div>

          {/* Supermercados que lo tienen disponible */}
          <div className="mb-4">
            <div className="text-[10px] font-semibold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1 flex items-center space-x-1">
              <CheckCircle2 className={`w-3 h-3 ${hasMichi ? 'text-emerald-600' : 'text-orange-600'}`} />
              <span>Comparado en {product.available_supermarkets.length} tiendas:</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {product.available_supermarkets.map((sup) => (
                <span
                  key={sup}
                  className="bg-stone-50 dark:bg-stone-800 text-stone-700 dark:text-stone-300 text-[10px] font-semibold px-2 py-0.5 rounded border border-stone-200/70 dark:border-stone-700"
                >
                  {sup}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Acciones */}
        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-stone-100 dark:border-stone-800">
          <button
            onClick={() => onViewComparison(product.id, product.package_format)}
            className={`w-full flex items-center justify-center space-x-1.5 active:scale-95 text-white font-bold py-2.5 px-3 rounded-xl text-xs transition-all shadow-sm ${
              hasMichi
                ? 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-500/25'
                : 'bg-orange-600 hover:bg-orange-500 shadow-orange-500/20'
            }`}
          >
            <span>Comparar</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => onSetAlert(product)}
            className={`w-full flex items-center justify-center space-x-1 bg-white dark:bg-stone-800 active:scale-95 font-bold py-2.5 px-3 rounded-xl text-xs transition-all border ${
              hasMichi
                ? 'text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-stone-700 hover:border-emerald-300 dark:hover:border-emerald-600 hover:bg-emerald-50/80 dark:hover:bg-stone-750'
                : 'text-orange-800 dark:text-orange-300 border-orange-200 dark:border-stone-700 hover:border-orange-300 dark:hover:border-stone-600 hover:bg-orange-50/80 dark:hover:bg-stone-700'
            }`}
          >
            <Bell className={`w-3.5 h-3.5 ${hasMichi ? 'text-emerald-600 dark:text-emerald-400' : 'text-orange-600 dark:text-orange-400'}`} />
            <span>Alerta WhatsApp</span>
          </button>
        </div>
      </div>
    </div>
  );
};
