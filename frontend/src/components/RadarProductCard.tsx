import { Tag, ExternalLink, Flame } from 'lucide-react';
import { PriceOpportunity } from '../types/radar';

interface RadarProductCardProps {
  opportunity: PriceOpportunity;
  onViewComparison?: (opportunity: PriceOpportunity) => void;
}

const STORE_BADGE_STYLE: Record<string, { bg: string; text: string; border: string }> = {
  el_carnicero: { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
  dona_carne: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
  comercial_castro: { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' },
  acuenta: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  alvi: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  central_mayorista: { bg: 'bg-yellow-50', text: 'text-yellow-800', border: 'border-yellow-200' },
  la_oferta: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
  comercial_teba: { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200' },
  distribuidora_santiago: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  abu_gosh: { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' },
  lo_valledor: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  mayorista_10: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' }
};

export const RadarProductCard: React.FC<RadarProductCardProps> = ({
  opportunity,
  onViewComparison
}) => {
  const isSuper = opportunity.deal_level === 'SUPER_AHORRO';
  const isAlto = opportunity.deal_level === 'AHORRO_ALTO';
  const badgeColors = STORE_BADGE_STYLE[opportunity.store_id] || {
    bg: 'bg-slate-100',
    text: 'text-slate-800',
    border: 'border-slate-200'
  };

  return (
    <div className="bg-white rounded-2xl border border-stone-200/80 shadow-xs hover:shadow-lg hover:border-orange-300 transition-all duration-300 flex flex-col overflow-hidden group">
      {/* Imagen & Tag de Ahorro */}
      <div className="relative h-48 bg-white overflow-hidden flex items-center justify-center p-3 border-b border-stone-100">
        {opportunity.image_url ? (
          <img
            src={opportunity.image_url}
            alt={opportunity.product_name}
            className="h-full w-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        ) : (
          <div className="text-stone-400 text-sm font-medium">Sin imagen disponible</div>
        )}

        {/* Tag de Ahorro Porcentual */}
        <div
          className={`absolute top-2.5 right-2.5 text-white text-[11px] font-extrabold px-2.5 py-1 rounded-full shadow-md flex items-center space-x-1 ${
            isSuper
              ? 'bg-gradient-to-r from-orange-600 to-amber-500'
              : isAlto
              ? 'bg-gradient-to-r from-amber-600 to-orange-500'
              : 'bg-gradient-to-r from-stone-700 to-stone-900'
          }`}
        >
          {isSuper ? <Flame className="w-3 h-3" /> : <Tag className="w-3 h-3" />}
          <span>Ahorra {opportunity.savings_percentage}%</span>
        </div>

        {/* Categoría en esquina inferior izquierda */}
        <div className="absolute bottom-2.5 left-2.5">
          <span className="text-[10px] uppercase font-bold tracking-wider bg-stone-900/75 backdrop-blur-sm text-white px-2 py-0.5 rounded-md">
            {opportunity.category.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Contenido */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          {/* Fila Tienda y Presentación */}
          <div className="flex items-center justify-between text-xs text-stone-500 mb-1">
            <span className="font-bold text-stone-800">{opportunity.store_name}</span>
            <span className="bg-stone-100 text-stone-700 px-2 py-0.5 rounded-md font-medium text-[10px] border border-stone-200">
              {opportunity.unit}
            </span>
          </div>

          <h3 className="text-sm sm:text-base font-bold text-stone-900 line-clamp-2 mb-2 group-hover:text-orange-950 transition-colors">
            {opportunity.product_name}
          </h3>

          {/* Bloque de Precios con Formato Real (Estructura Unificada con Retail) */}
          <div className="bg-orange-50/40 rounded-xl p-3 border border-orange-100/70 mb-3">
            {/* Badge obligatorio: Precio más barato */}
            <div className="flex items-center justify-between mb-2">
              <span className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg font-black text-[11px] border shadow-2xs ${badgeColors.bg} ${badgeColors.text} ${badgeColors.border}`}>
                <span>★ Precio más barato: {opportunity.store_name.split(' (')[0]}</span>
              </span>
              {opportunity.savings_percentage > 0 && (
                <span className="text-[11px] font-bold text-orange-700 bg-orange-100/90 px-2 py-0.5 rounded-md">
                  -{opportunity.savings_percentage}%
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
                  <span>${Math.round(opportunity.alternative_price).toLocaleString('es-CL')}</span>
                  <span className="text-xs font-bold text-stone-700 bg-stone-100 px-2 py-0.5 rounded-md border border-stone-200/80">
                    {opportunity.unit}
                  </span>
                </div>
              </div>

              {opportunity.traditional_benchmark_price > opportunity.alternative_price && (
                <div className="text-right">
                  <span className="text-[10px] text-stone-400 block">Hasta</span>
                  <span className="text-xs text-stone-400 line-through font-medium">
                    ${Math.round(opportunity.traditional_benchmark_price).toLocaleString('es-CL')}
                  </span>
                </div>
              )}
            </div>

            {/* Precio Secundario de Referencia ($/kg o $/un) y Ahorro */}
            <div className="mt-2 flex items-center justify-between pt-2 border-t border-orange-100/70 text-xs">
              <span className="text-stone-500 font-medium">
                Ref. normalizada:
              </span>
              <span className="font-bold text-stone-700">
                ${Math.round(opportunity.unit_price_alternative).toLocaleString('es-CL')} / ref
              </span>
            </div>

            {opportunity.savings_clp > 0 && (
              <div className="mt-1.5 flex items-center justify-between text-xs pt-1 border-t border-orange-100/40">
                <span className="text-stone-600 font-medium">Ahorras en este bulto:</span>
                <span className="text-orange-700 font-extrabold">
                  ${Math.round(opportunity.savings_clp).toLocaleString('es-CL')}
                </span>
              </div>
            )}
          </div>

          {/* Nota / Recomendación de Compra Mayorista */}
          <p className="text-[11px] text-stone-600 italic bg-amber-50/50 p-2.5 rounded-lg border border-amber-100/70 mb-3 line-clamp-2 leading-relaxed">
            "{opportunity.recommendation_note}"
          </p>
        </div>

        {/* Acciones */}
        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-stone-100">
          <a
            href={opportunity.purchase_url}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex items-center justify-center space-x-1.5 bg-orange-600 hover:bg-orange-500 active:scale-95 text-white font-bold py-2.5 px-3 rounded-xl text-xs transition-all shadow-sm shadow-orange-500/20 text-center"
          >
            <span>Ver Tienda</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>

          <button
            type="button"
            onClick={() => onViewComparison?.(opportunity)}
            className="w-full flex items-center justify-center space-x-1 bg-white hover:bg-orange-50/80 active:scale-95 text-orange-800 border border-orange-200 hover:border-orange-300 font-bold py-2.5 px-3 rounded-xl text-xs transition-all text-center"
          >
            <span>Comparar</span>
          </button>
        </div>
      </div>
    </div>
  );
};
