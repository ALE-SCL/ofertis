import React from 'react';
import { ShoppingCart, Bell, Sparkles, Activity } from 'lucide-react';

interface NavbarProps {
  onOpenMyAlerts: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenMyAlerts }) => {
  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo & Marca */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <ShoppingCart className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-black tracking-tight text-slate-900">
                Ofert<span className="text-blue-600">is</span>
              </span>
              <span className="text-xs bg-red-100 text-red-700 font-semibold px-2 py-0.5 rounded-full border border-red-200 flex items-center space-x-1">
                <span>🇨🇱 Chile</span>
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">
              Comparador Multi-Agente & pgvector para Canasta Básica
            </p>
          </div>
        </div>

        {/* Supermercados monitoreados & Botón de Alertas */}
        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center space-x-2 text-xs font-medium text-slate-600 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
            <Activity className="w-3.5 h-3.5 text-emerald-500 animate-pulse" />
            <span>Monitoreando:</span>
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
            className="flex items-center space-x-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-300 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all shadow-sm active:scale-95"
          >
            <Bell className="w-4 h-4 text-emerald-600" />
            <span>Mis Alertas WhatsApp</span>
          </button>
        </div>
      </div>
    </header>
  );
};
