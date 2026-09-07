import React from 'react';
import { Database, MapPin, Cpu, ShieldCheck } from 'lucide-react';
import { MiningStats } from '../types';

interface MiningStatsBannerProps {
  stats: MiningStats | null;
}

export const MiningStatsBanner: React.FC<MiningStatsBannerProps> = ({ stats }) => {
  return (
    <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white py-3 px-4 shadow-inner border-b border-indigo-900/50">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
          <span className="font-semibold text-emerald-400">Motor de Minería Activo:</span>
          <span className="text-slate-300">
            {stats ? `${stats.canonical_products_count} productos canónicos normalizados | ${stats.supermarket_skus_tracked} SKUs en monitoreo` : 'Conectando con PostgreSQL + pgvector...'}
          </span>
        </div>

        <div className="flex items-center space-x-4 text-slate-300">
          <div className="flex items-center space-x-1.5">
            <MapPin className="w-3.5 h-3.5 text-amber-400" />
            <span>Zona Base: <strong>Santiago Centro / Providencia</strong></span>
          </div>
          <div className="hidden sm:flex items-center space-x-1.5">
            <Database className="w-3.5 h-3.5 text-cyan-400" />
            <span>pgvector <strong>HNSW 384d</strong></span>
          </div>
          <div className="hidden md:flex items-center space-x-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Norma Chilena <strong>NCh 1424</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
};
