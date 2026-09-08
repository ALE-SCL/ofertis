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
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 flex flex-col overflow-hidden group">
      {/* Imagen & Tag de Ahorro */}
      <div className="relative h-44 bg-slate-100 overflow-hidden flex items-center justify-center p-2">
        {opportunity.image_url ? (
          <img
            src={opportunity.image_url}
            alt={opportunity.product_name}
            className="h-full w-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        ) : (
          <div className="text-slate-400 text-sm font-medium">Sin imagen disponible</div>
        )}

        {/* Tag de Ahorro Porcentual */}
        <div
          className={`absolute top-2 right-2 text-white text-[11px] font-extrabold px-2.5 py-1 rounded-full shadow-md flex items-center space-x-1 ${
            isSuper
              ? 'bg-gradient-to-r from-emerald-600 to-teal-600'
              : isAlto
              ? 'bg-gradient-to-r from-amber-600 to-orange-600'
              : 'bg-gradient-to-r from-blue-600 to-indigo-600'
          }`}
        >
          {isSuper ? <Flame className="w-3 h-3" /> : <Tag className="w-3 h-3" />}
          <span>Ahorra {opportunity.savings_percentage}%</span>
        </div>

        {/* Categoría en esquina inferior izquierda */}
        <div className="absolute bottom-2 left-2">
          <span className="text-[10px] uppercase font-black tracking-wider bg-slate-900/80 backdrop-blur-sm text-white px-2 py-0.5 rounded-md">
            {opportunity.category.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Contenido */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          {/* Fila Tienda y Presentación */}
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-bold text-slate-700">{opportunity.store_name}</span>
            <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded-md font-medium text-[10px] border border-slate-200">
              {opportunity.unit}
            </span>
          </div>

          {/* Nombre del Producto */}
          <h3 className="text-sm sm:text-base font-bold text-slate-900 line-clamp-2 mb-3">
            {opportunity.product_name}
          </h3>

          {/* Precios Normalizados y Comparativa */}
          <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 mb-3">
            <div className="flex items-baseline justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700">
                  Precio Alternativo:
                </span>
                <div className="text-lg sm:text-xl font-black text-slate-900">
                  ${Math.round(opportunity.alternative_price).toLocaleString('es-CL')}
                  <span className="text-xs font-semibold text-slate-500 ml-1">
                    / {opportunity.unit}
                  </span>
                </div>
              </div>

              {opportunity.traditional_benchmark_price > opportunity.alternative_price && (
                <div className="text-right">
                  <span className="text-[10px] text-slate-400 line-through block">
                    Retail: ${Math.round(opportunity.traditional_benchmark_price).toLocaleString('es-CL')}
                  </span>
                  <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100/80 px-1.5 py-0.5 rounded">
                    -{opportunity.savings_percentage}%
                  </span>
                </div>
              )}
            </div>

            {/* Canal y ahorro en pesos */}
            <div className="mt-2 flex items-center justify-between pt-2 border-t border-slate-200/60 text-xs">
              <span className="text-slate-500 font-medium">Canal más económico:</span>
              <span className={`px-2 py-0.5 rounded-md font-bold text-[11px] border ${badgeColors.bg} ${badgeColors.text} ${badgeColors.border}`}>
                {opportunity.store_name.split(' ')[0]}
              </span>
            </div>

            <div className="mt-1.5 flex items-center justify-between text-xs pt-1">
              <span className="text-slate-600 font-semibold">Ahorras en tu compra:</span>
              <span className="text-emerald-700 font-black">
                -${Math.round(opportunity.savings_clp).toLocaleString('es-CL')} CLP
              </span>
            </div>
          </div>

          {/* Nota / Recomendación de Compra */}
          <p className="text-[11px] text-slate-600 italic bg-emerald-50/50 p-2 rounded-lg border border-emerald-100/60 mb-3 line-clamp-2 leading-relaxed">
            "{opportunity.recommendation_note}"
          </p>
        </div>

        {/* Acciones idénticas a ProductCard */}
        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100">
          <a
            href={opportunity.purchase_url}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex items-center justify-center space-x-1.5 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white font-bold py-2 px-3 rounded-xl text-xs transition-all shadow-sm shadow-emerald-500/10 text-center"
          >
            <span>Ver Tienda</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>

          <button
            type="button"
            onClick={() => onViewComparison?.(opportunity)}
            className="w-full flex items-center justify-center space-x-1 bg-slate-100 hover:bg-slate-200 active:scale-95 text-slate-700 border border-slate-200 font-bold py-2 px-3 rounded-xl text-xs transition-all text-center"
          >
            <span>Comparar</span>
          </button>
        </div>
      </div>
    </div>
  );
};
