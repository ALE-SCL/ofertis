import React from 'react';
import { ArrowRight, Bell, Tag, CheckCircle2 } from 'lucide-react';
import { ProductSearchResult } from '../types';

interface ProductCardProps {
  product: ProductSearchResult;
  onViewComparison: (productId: number, format?: string) => void;
  onSetAlert: (product: ProductSearchResult) => void;
}

const SUPERMARKET_BADGE_STYLE: Record<string, string> = {
  lider: 'bg-blue-50 text-blue-800 border-blue-200',
  jumbo: 'bg-emerald-50 text-emerald-800 border-emerald-200',
  santaisabel: 'bg-rose-50 text-rose-800 border-rose-200',
  unimarc: 'bg-red-50 text-red-800 border-red-200'
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

  const badgeClass = SUPERMARKET_BADGE_STYLE[product.best_supermarket_slug] || 'bg-orange-50 text-orange-800 border-orange-200';
  const displayPackagePrice = product.best_package_price > 0 ? product.best_package_price : product.min_unit_price;

  return (
    <div
      id={`product-${product.id}`}
      className="bg-white rounded-2xl border border-stone-200/80 shadow-xs hover:shadow-lg hover:border-orange-300 transition-all duration-300 flex flex-col overflow-hidden group scroll-mt-24"
    >
      {/* Imagen & Tag de Ahorro */}
      <div className="relative h-48 bg-white overflow-hidden flex items-center justify-center p-3 border-b border-stone-100">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="h-full w-full object-contain object-center group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        ) : (
          <div className="text-stone-400 text-sm font-medium">Sin imagen disponible</div>
        )}

        {savings > 5 && (
          <div className="absolute top-2.5 right-2.5 bg-gradient-to-r from-orange-600 to-amber-500 text-white text-[11px] font-extrabold px-2.5 py-1 rounded-full shadow-md flex items-center space-x-1">
            <Tag className="w-3 h-3" />
            <span>Ahorra {savings}%</span>
          </div>
        )}

        <div className="absolute bottom-2.5 left-2.5">
          <span className="text-[10px] uppercase font-bold tracking-wider bg-stone-900/75 backdrop-blur-sm text-white px-2 py-0.5 rounded-md">
            {product.category.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Contenido */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-xs text-stone-500 mb-1">
            <span className="font-medium text-stone-600">{product.brand || 'Varias marcas'}</span>
            {product.subcategory && (
              <span className="bg-stone-100 text-stone-700 px-2 py-0.5 rounded-md font-medium text-[10px]">
                {product.subcategory.replace('_', ' ')}
              </span>
            )}
          </div>

          <h3 className="text-sm sm:text-base font-bold text-stone-900 line-clamp-2 mb-2 group-hover:text-orange-950 transition-colors">
            {product.name}
          </h3>

          {/* Bloque de Precios con Formato Real */}
          <div className="bg-orange-50/40 rounded-xl p-3 border border-orange-100/70 mb-3">
            {/* Badge obligatorio: Precio más barato */}
            <div className="flex items-center justify-between mb-2">
              <span className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg font-black text-[11px] border shadow-2xs ${badgeClass}`}>
                <span>★ Precio más barato: {product.best_supermarket_name}</span>
              </span>
              {product.savings_amount > 0 && (
                <span className="text-[11px] font-bold text-orange-700 bg-orange-100/90 px-2 py-0.5 rounded-md">
                  -${Math.round(product.savings_amount).toLocaleString('es-CL')}
                </span>
              )}
            </div>

            {/* Precio Principal Grande del Formato Real */}
            <div className="flex items-baseline justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-stone-500 block mb-0.5">
                  Precio a pagar:
                </span>
                <div className="text-2xl sm:text-3xl font-black text-stone-900 tracking-tight flex items-baseline space-x-1.5">
                  <span>${Math.round(displayPackagePrice).toLocaleString('es-CL')}</span>
                  <span className="text-xs font-bold text-stone-700 bg-stone-100 px-2 py-0.5 rounded-md border border-stone-200/80">
                    {product.package_format}
                  </span>
                </div>
              </div>

              {product.highest_package_price > product.best_package_price && (
                <div className="text-right">
                  <span className="text-[10px] text-stone-400 block">Hasta</span>
                  <span className="text-xs text-stone-400 line-through font-medium">
                    ${Math.round(product.highest_package_price).toLocaleString('es-CL')}
                  </span>
                </div>
              )}
            </div>

            {/* Precio Secundario de Referencia ($/kg o $/L) */}
            <div className="mt-2 flex items-center justify-between pt-2 border-t border-orange-100/70 text-xs">
              <span className="text-stone-500 font-medium">
                Ref. normalizada:
              </span>
              <span className="font-bold text-stone-700">
                ${Math.round(product.min_unit_price).toLocaleString('es-CL')} / {product.standard_unit}
              </span>
            </div>
          </div>

          {/* Supermercados que lo tienen disponible */}
          <div className="mb-4">
            <div className="text-[10px] font-semibold text-stone-500 uppercase tracking-wider mb-1 flex items-center space-x-1">
              <CheckCircle2 className="w-3 h-3 text-orange-600" />
              <span>Comparado en {product.available_supermarkets.length} tiendas:</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {product.available_supermarkets.map((sup) => (
                <span
                  key={sup}
                  className="bg-stone-50 text-stone-700 text-[10px] font-semibold px-2 py-0.5 rounded border border-stone-200/70"
                >
                  {sup}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Acciones */}
        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-stone-100">
          <button
            onClick={() => onViewComparison(product.id, product.package_format)}
            className="w-full flex items-center justify-center space-x-1.5 bg-orange-600 hover:bg-orange-500 active:scale-95 text-white font-bold py-2.5 px-3 rounded-xl text-xs transition-all shadow-sm shadow-orange-500/20"
          >
            <span>Comparar</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => onSetAlert(product)}
            className="w-full flex items-center justify-center space-x-1 bg-white hover:bg-orange-50/80 active:scale-95 text-orange-800 border border-orange-200 hover:border-orange-300 font-bold py-2.5 px-3 rounded-xl text-xs transition-all"
          >
            <Bell className="w-3.5 h-3.5 text-orange-600" />
            <span>Alerta WhatsApp</span>
          </button>
        </div>
      </div>
    </div>
  );
};
