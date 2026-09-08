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
    <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 text-white py-2.5 px-4 shadow-inner border-b border-blue-900/50">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
          <span className="font-bold text-emerald-400">Precios actualizados de hoy:</span>
          <span className="text-slate-200">
            {stats ? (
              <>
                <strong className="text-white font-extrabold">{skusCount.toLocaleString('es-CL')}</strong> productos y formatos comparados en <strong className="text-white font-extrabold">{productsCount.toLocaleString('es-CL')}</strong> categorías de la canasta familiar
              </>
            ) : (
              'Comprobando ofertas en tiempo real en los 4 grandes supermercados...'
            )}
          </span>
        </div>

        <div className="flex items-center space-x-4 text-slate-300">
          <div className="flex items-center space-x-1.5">
            <Coins className="w-3.5 h-3.5 text-amber-400" />
            <span>Precios justos por <strong>kilo y litro</strong></span>
          </div>
          <div className="hidden sm:flex items-center space-x-1.5">
            <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
            <span>Ahorro real <strong>sin publicidad pagada</strong></span>
          </div>
          <div className="hidden md:flex items-center space-x-1.5">
            <MapPin className="w-3.5 h-3.5 text-rose-400" />
            <span>Cobertura <strong>Santiago y Regiones</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
};
