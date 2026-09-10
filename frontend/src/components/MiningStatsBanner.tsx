import React from 'react';
import { MapPin, Coins, TrendingDown } from 'lucide-react';
import { MiningStats } from '../types';

interface MiningStatsBannerProps {
  stats: MiningStats | null;
}

export const MiningStatsBanner: React.FC<MiningStatsBannerProps> = ({ stats }) => {
  const skusCount = stats?.supermarket_skus_tracked || 5903;
  const productsCount = stats?.canonical_products_count || 2241;

  return (
    <div className="bg-gradient-to-r from-orange-50/90 via-amber-50/80 to-orange-50/90 text-slate-800 py-2.5 px-4 shadow-2xs border-b border-orange-200/60">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-orange-500 animate-ping"></div>
          <span className="font-bold text-orange-800">Precios actualizados de hoy:</span>
          <span className="text-slate-700">
            {stats ? (
              <>
                <strong className="text-orange-950 font-extrabold">{skusCount.toLocaleString('es-CL')}</strong> productos comparados en <strong className="text-orange-950 font-extrabold">{productsCount.toLocaleString('es-CL')}</strong> formatos de canasta familiar
              </>
            ) : (
              'Comprobando ofertas en tiempo real en los 4 grandes supermercados...'
            )}
          </span>
        </div>

        <div className="flex items-center space-x-4 text-slate-600 font-medium">
          <div className="flex items-center space-x-1.5">
            <Coins className="w-3.5 h-3.5 text-orange-600" />
            <span>Precios justos por <strong className="text-slate-800">kilo y litro</strong></span>
          </div>
          <div className="hidden sm:flex items-center space-x-1.5">
            <TrendingDown className="w-3.5 h-3.5 text-emerald-600" />
            <span>Ahorro real <strong className="text-slate-800">sin publicidad pagada</strong></span>
          </div>
          <div className="hidden md:flex items-center space-x-1.5">
            <MapPin className="w-3.5 h-3.5 text-orange-600" />
            <span>Cobertura <strong className="text-slate-800">Santiago y Regiones</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
};
