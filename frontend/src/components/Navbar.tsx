import React from 'react';
import { Bell, Activity } from 'lucide-react';
import logoImg from '../assets/logo_ofertis.jpg';

interface NavbarProps {
  onOpenMyAlerts: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenMyAlerts }) => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-orange-100 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo & Marca Oficial */}
        <div 
          className="flex items-center space-x-3 cursor-pointer group"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          title="Ofertis - Ir al inicio"
        >
          <img
            src={logoImg}
            alt="Ofertis - El buscador de ofertas que alimenta tu ahorro"
            className="h-10 sm:h-12 w-auto object-contain transition-transform group-hover:scale-[1.02]"
          />
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
