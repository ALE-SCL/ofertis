import React from 'react';
import { ShoppingCart, Bell, Activity } from 'lucide-react';

interface NavbarProps {
  onOpenMyAlerts: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenMyAlerts }) => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-orange-100 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo & Marca */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-orange-600 via-orange-500 to-amber-500 flex items-center justify-center text-white shadow-md shadow-orange-500/20">
            <ShoppingCart className="w-5 h-5" />
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xl sm:text-2xl font-black tracking-tight text-slate-900">
              Ofert<span className="text-orange-600">is</span>
            </span>
          </div>
        </div>

        {/* Supermercados monitoreados & Botón de Alertas */}
        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center space-x-2 text-xs font-medium text-slate-600 bg-orange-50/40 px-3.5 py-1.5 rounded-xl border border-orange-100/80">
            <Activity className="w-3.5 h-3.5 text-orange-500 animate-pulse" />
            <span className="font-semibold text-slate-700">Comparando en vivo:</span>
            <span className="font-bold text-blue-600">Lider</span>
            <span>•</span>
            <span className="font-bold text-emerald-600">Jumbo</span>
            <span>•</span>
            <span className="font-bold text-rose-600">Santa Isabel</span>
            <span>•</span>
            <span className="font-bold text-red-600">Unimarc</span>
          </div>

          <button
            onClick={onOpenMyAlerts}
            className="flex items-center space-x-2 bg-white hover:bg-orange-50/80 text-orange-700 border border-orange-200 hover:border-orange-300 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all shadow-xs active:scale-95"
          >
            <Bell className="w-4 h-4 text-orange-500" />
            <span>Avisos de Ofertas WhatsApp</span>
          </button>
        </div>
      </div>
    </header>
  );
};
