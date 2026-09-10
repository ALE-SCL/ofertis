import React from 'react';
import { Bell, Activity } from 'lucide-react';
import logoImg from '../assets/logo_ofertis.jpg';

interface NavbarProps {
  onOpenMyAlerts: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenMyAlerts }) => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-orange-100 shadow-xs transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 sm:py-3 min-h-[7rem] sm:min-h-[8.5rem] md:min-h-[9.5rem] flex items-center justify-between">
        {/* Logo Oficial Grande (+100% de tamaño) */}
        <div 
          className="flex items-center cursor-pointer group py-1"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          title="Ofertis - Ir al inicio"
        >
          <img
            src={logoImg}
            alt="Ofertis - El buscador de ofertas que alimenta tu ahorro"
            className="h-28 sm:h-36 md:h-40 w-auto object-contain transition-transform duration-200 group-hover:scale-[1.02]"
          />
        </div>

        {/* Supermercados monitoreados & Botón de Alertas */}
        <div className="flex items-center space-x-3 sm:space-x-4">
          <div className="hidden lg:flex items-center space-x-2 text-xs sm:text-sm font-semibold text-stone-700 bg-orange-50/60 px-4 py-2.5 rounded-2xl border border-orange-100/90 shadow-2xs">
            <Activity className="w-4 h-4 text-orange-500 animate-pulse" />
            <span className="text-stone-500">En vivo:</span>
            <span className="font-extrabold text-blue-600">Lider</span>
            <span className="text-orange-200">•</span>
            <span className="font-extrabold text-emerald-600">Jumbo</span>
            <span className="text-orange-200">•</span>
            <span className="font-extrabold text-rose-600">Santa Isabel</span>
            <span className="text-orange-200">•</span>
            <span className="font-extrabold text-red-600">Unimarc</span>
          </div>

          <button
            onClick={onOpenMyAlerts}
            className="flex items-center space-x-2 bg-white hover:bg-orange-50 text-orange-700 border border-orange-200 hover:border-orange-300 px-5 py-3 rounded-2xl text-xs sm:text-sm font-extrabold transition-all shadow-xs active:scale-95"
          >
            <Bell className="w-4 h-4 text-orange-500" />
            <span>Avisos WhatsApp</span>
          </button>
        </div>
      </div>
    </header>
  );
};
