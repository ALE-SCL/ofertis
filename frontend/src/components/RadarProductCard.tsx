import { Tag, ExternalLink, Flame } from 'lucide-react';
import { PriceOpportunity } from '../types/radar';
import mascotImg from '../assets/mascot_ofertis.jpg';

interface RadarProductCardProps {
  opportunity: PriceOpportunity;
  onViewComparison?: (opportunity: PriceOpportunity) => void;
}

const STORE_BADGE_STYLE: Record<string, { bg: string; text: string; border: string }> = {
  el_carnicero: { bg: 'bg-rose-50 dark:bg-rose-950/60', text: 'text-rose-700 dark:text-rose-300', border: 'border-rose-200 dark:border-rose-800' },
  dona_carne: { bg: 'bg-red-50 dark:bg-red-950/60', text: 'text-red-700 dark:text-red-300', border: 'border-red-200 dark:border-red-800' },
  comercial_castro: { bg: 'bg-orange-50 dark:bg-orange-950/60', text: 'text-orange-700 dark:text-orange-300', border: 'border-orange-200 dark:border-orange-800' },
  acuenta: { bg: 'bg-amber-50 dark:bg-amber-950/60', text: 'text-amber-700 dark:text-amber-300', border: 'border-amber-200 dark:border-amber-800' },
  alvi: { bg: 'bg-blue-50 dark:bg-blue-950/60', text: 'text-blue-700 dark:text-blue-300', border: 'border-blue-200 dark:border-blue-800' },
  central_mayorista: { bg: 'bg-yellow-50 dark:bg-yellow-950/60', text: 'text-yellow-800 dark:text-yellow-300', border: 'border-yellow-200 dark:border-yellow-800' },
  la_oferta: { bg: 'bg-purple-50 dark:bg-purple-950/60', text: 'text-purple-700 dark:text-purple-300', border: 'border-purple-200 dark:border-purple-800' },
  comercial_teba: { bg: 'bg-teal-50 dark:bg-teal-950/60', text: 'text-teal-700 dark:text-teal-300', border: 'border-teal-200 dark:border-teal-800' },
  distribuidora_santiago: { bg: 'bg-emerald-50 dark:bg-emerald-950/60', text: 'text-emerald-700 dark:text-emerald-300', border: 'border-emerald-200 dark:border-emerald-800' },
  abu_gosh: { bg: 'bg-indigo-50 dark:bg-indigo-950/60', text: 'text-indigo-700 dark:text-indigo-300', border: 'border-indigo-200 dark:border-indigo-800' },
  lo_valledor: { bg: 'bg-emerald-50 dark:bg-emerald-950/60', text: 'text-emerald-700 dark:text-emerald-300', border: 'border-emerald-200 dark:border-emerald-800' },
  mayorista_10: { bg: 'bg-blue-50 dark:bg-blue-950/60', text: 'text-blue-700 dark:text-blue-300', border: 'border-blue-200 dark:border-blue-800' }
};

export const RadarProductCard: React.FC<RadarProductCardProps> = ({
  opportunity,
  onViewComparison
}) => {
  const isSuper = opportunity.deal_level === 'SUPER_AHORRO';
  const isAlto = opportunity.deal_level === 'AHORRO_ALTO';
  const hasMichi = opportunity.savings_percentage >= 20 || isSuper;
  const badgeColors = STORE_BADGE_STYLE[opportunity.store_id] || {
    bg: 'bg-slate-100 dark:bg-stone-800',
    text: 'text-slate-800 dark:text-stone-300',
    border: 'border-slate-200 dark:border-stone-700'
  };

  return (
    <div
      className={`bg-white dark:bg-stone-900 rounded-2xl border transition-all duration-300 flex flex-col overflow-hidden group ${
        hasMichi
          ? 'border-emerald-400 dark:border-emerald-600/80 shadow-md shadow-emerald-500/10 hover:shadow-xl hover:border-emerald-500'
          : 'border-stone-200/80 dark:border-stone-800 shadow-xs hover:shadow-lg hover:border-orange-300 dark:hover:border-orange-500'
      }`}
    >
      {/* Imagen & Tag de Ahorro */}
      <div className="relative h-48 bg-white dark:bg-stone-850 overflow-hidden flex items-center justify-center p-3 border-b border-stone-100 dark:border-stone-800">
        {opportunity.image_url ? (
          <img
            src={opportunity.image_url}
            alt={opportunity.product_name}
            className="h-full w-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        ) : (
          <div className="text-stone-400 dark:text-stone-500 text-sm font-medium">Sin imagen disponible</div>
        )}

        {/* Sello de Mascota Ofertis en verde en ofertas con mayor ahorro */}
        {hasMichi && (
          <div className="absolute top-2.5 left-2.5 z-10 flex items-center space-x-1.5 bg-emerald-50/95 dark:bg-emerald-950/95 backdrop-blur-xs rounded-full p-1 pr-2.5 border border-emerald-300 dark:border-emerald-700 shadow-md group-hover:scale-105 transition-transform">
            <img
              src={mascotImg}
              alt="Michito Ofertis"
              className="w-6 h-6 rounded-full object-cover border-2 border-emerald-500 shadow-xs"
            />
            <span className="text-[10px] font-black text-emerald-800 dark:text-emerald-200 tracking-tight">
              Súper Ahorro
            </span>
          </div>
        )}

        {/* Tag de Ahorro Porcentual */}
        <div
          className={`absolute top-2.5 right-2.5 text-white text-[11px] font-extrabold px-2.5 py-1 rounded-full shadow-md flex items-center space-x-1 ${
            hasMichi
              ? 'bg-gradient-to-r from-emerald-600 to-green-500 shadow-emerald-600/30'
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
          <span className="text-[10px] uppercase font-bold tracking-wider bg-stone-900/80 dark:bg-stone-950/90 backdrop-blur-sm text-white px-2 py-0.5 rounded-md">
            {opportunity.category.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Contenido */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          {/* Fila Tienda y Presentación */}
          <div className="flex items-center justify-between text-xs text-stone-500 dark:text-stone-400 mb-1">
            <span className="font-bold text-stone-800 dark:text-stone-200">{opportunity.store_name}</span>
            <span className="bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 px-2 py-0.5 rounded-md font-medium text-[10px] border border-stone-200 dark:border-stone-700">
              {opportunity.unit}
            </span>
          </div>

          <h3
            className={`text-sm sm:text-base font-bold text-stone-900 dark:text-stone-100 line-clamp-2 mb-2 transition-colors ${
              hasMichi
                ? 'group-hover:text-emerald-600 dark:group-hover:text-emerald-400'
                : 'group-hover:text-orange-600 dark:group-hover:text-orange-400'
            }`}
          >
            {opportunity.product_name}
          </h3>

          {/* Bloque de Precios con Formato Real (Estructura Unificada con Retail) */}
          <div
            className={`rounded-xl p-3 mb-3 border ${
              hasMichi
                ? 'bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-200/80 dark:border-emerald-800/50'
                : 'bg-orange-50/40 dark:bg-stone-800/60 border-orange-100/70 dark:border-stone-700/60'
            }`}
          >
            {/* Badge obligatorio: Precio más barato */}
            <div className="flex items-center justify-between mb-2">
              <span className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg font-black text-[11px] border shadow-2xs ${badgeColors.bg} ${badgeColors.text} ${badgeColors.border}`}>
                <span>★ Precio más barato: {opportunity.store_name.split(' (')[0]}</span>
              </span>
              {opportunity.savings_percentage > 0 && (
                <span
                  className={`text-[11px] font-bold px-2 py-0.5 rounded-md ${
                    hasMichi
                      ? 'text-emerald-800 dark:text-emerald-200 bg-emerald-100/90 dark:bg-emerald-900/60'
                      : 'text-orange-700 dark:text-orange-300 bg-orange-100/90 dark:bg-orange-950/70'
                  }`}
                >
                  -{opportunity.savings_percentage}%
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
                    ${Math.round(opportunity.alternative_price).toLocaleString('es-CL')}
                  </span>
                  <span className="text-xs font-bold text-stone-700 dark:text-stone-300 bg-stone-100 dark:bg-stone-700 px-2 py-0.5 rounded-md border border-stone-200/80 dark:border-stone-600">
                    {opportunity.unit}
                  </span>
                </div>
              </div>

              {opportunity.traditional_benchmark_price > opportunity.alternative_price && (
                <div className="text-right">
                  <span className="text-[10px] text-stone-400 dark:text-stone-500 block">Hasta</span>
                  <span className="text-xs text-stone-400 dark:text-stone-500 line-through font-medium">
                    ${Math.round(opportunity.traditional_benchmark_price).toLocaleString('es-CL')}
                  </span>
                </div>
              )}
            </div>

            {/* Precio Secundario de Referencia ($/kg o $/un) y Ahorro */}
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
                ${Math.round(opportunity.unit_price_alternative).toLocaleString('es-CL')} / ref
              </span>
            </div>

            {opportunity.savings_clp > 0 && (
              <div
                className={`mt-1.5 flex items-center justify-between text-xs pt-1 border-t ${
                  hasMichi
                    ? 'border-emerald-200/40 dark:border-emerald-800/40'
                    : 'border-orange-100/40 dark:border-stone-700/40'
                }`}
              >
                <span className="text-stone-600 dark:text-stone-300 font-medium">Ahorras en este bulto:</span>
                <span className={`font-extrabold ${hasMichi ? 'text-emerald-700 dark:text-emerald-400' : 'text-orange-700 dark:text-orange-400'}`}>
                  ${Math.round(opportunity.savings_clp).toLocaleString('es-CL')}
                </span>
              </div>
            )}
          </div>

          {/* Nota / Recomendación de Compra Mayorista */}
          <p className="text-[11px] text-stone-600 dark:text-stone-300 italic bg-amber-50/50 dark:bg-stone-800 p-2.5 rounded-lg border border-amber-100/70 dark:border-stone-700 mb-3 line-clamp-2 leading-relaxed">
            "{opportunity.recommendation_note}"
          </p>
        </div>

        {/* Acciones */}
        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-stone-100 dark:border-stone-800">
          <a
            href={opportunity.purchase_url}
            target="_blank"
            rel="noopener noreferrer"
            className={`w-full flex items-center justify-center space-x-1.5 active:scale-95 text-white font-bold py-2.5 px-3 rounded-xl text-xs transition-all shadow-sm text-center ${
              hasMichi
                ? 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-500/25'
                : 'bg-orange-600 hover:bg-orange-500 shadow-orange-500/20'
            }`}
          >
            <span>Ver Tienda</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>

          <button
            type="button"
            onClick={() => onViewComparison?.(opportunity)}
            className={`w-full flex items-center justify-center space-x-1 bg-white dark:bg-stone-800 active:scale-95 font-bold py-2.5 px-3 rounded-xl text-xs transition-all text-center border ${
              hasMichi
                ? 'text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-stone-700 hover:border-emerald-300 dark:hover:border-emerald-600 hover:bg-emerald-50/80 dark:hover:bg-stone-750'
                : 'text-orange-800 dark:text-orange-300 border-orange-200 dark:border-stone-700 hover:border-orange-300 dark:hover:border-stone-600 hover:bg-orange-50/80 dark:hover:bg-stone-700'
            }`}
          >
            <span>Comparar</span>
          </button>
        </div>
      </div>
    </div>
  );
};
