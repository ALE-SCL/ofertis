import React from 'react';
import { MapPin } from 'lucide-react';
import { MiningStats } from '../types';

interface MiningStatsBannerProps {
  stats: MiningStats | null;
}

export const MiningStatsBanner: React.FC<MiningStatsBannerProps> = ({ stats }) => {
  const skusCount = stats?.supermarket_skus_tracked || 6069;
  const productsCount = stats?.canonical_products_count || 4894;

  return (
    <div className="bg-orange-50/50 dark:bg-stone-900/60 text-stone-700 dark:text-stone-300 py-2 px-4 border-b border-orange-100 dark:border-stone-800 transition-colors">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-orange-500 animate-ping"></span>
          <span className="font-bold text-orange-950 dark:text-orange-400">Precios de hoy:</span>
          <span className="text-stone-600 dark:text-stone-300">
            {stats ? (
              <>
                <strong className="text-stone-900 dark:text-white font-extrabold">{productsCount.toLocaleString('es-CL')}</strong> productos de la canasta comparados en <strong className="text-stone-900 dark:text-white font-extrabold">{skusCount.toLocaleString('es-CL')}</strong> ofertas de supermercados
              </>
            ) : (
              'Monitoreando ofertas en tiempo real...'
            )}
          </span>
        </div>

        <div className="flex items-center space-x-1.5 text-stone-500 dark:text-stone-400 font-medium">
          <MapPin className="w-3.5 h-3.5 text-orange-600 dark:text-orange-500" />
          <span>Cobertura <strong className="text-stone-700 dark:text-stone-200">Santiago y Regiones</strong></span>
        </div>
      </div>
    </div>
  );
};
