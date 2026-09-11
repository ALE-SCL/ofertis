import React from 'react';
import { Bell, Activity, Sun, Moon, TrendingUp } from 'lucide-react';
import logoImg from '../assets/logo_ofertis.jpg';

interface NavbarProps {
  onOpenMyAlerts: () => void;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
  activeTab?: 'retail' | 'radar' | 'alza-precios';
  onSelectTab?: (tab: 'retail' | 'radar' | 'alza-precios') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ 
  onOpenMyAlerts, 
  isDarkMode, 
  onToggleDarkMode,
  activeTab,
  onSelectTab
}) => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 dark:bg-stone-900/95 backdrop-blur-md border-b border-orange-100 dark:border-stone-800 shadow-xs transition-all">
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
            className="h-28 sm:h-36 md:h-40 w-auto object-contain transition-transform duration-200 group-hover:scale-[1.02] rounded-xl"
          />
        </div>

        {/* Supermercados monitoreados, Selector de Modo Oscuro & Botón de Alertas */}
        <div className="flex items-center space-x-2 sm:space-x-4">
          <div className="hidden lg:flex items-center space-x-2 text-xs sm:text-sm font-semibold text-stone-700 dark:text-stone-300 bg-orange-50/60 dark:bg-stone-800/80 px-4 py-2.5 rounded-2xl border border-orange-100/90 dark:border-stone-700 shadow-2xs">
            <Activity className="w-4 h-4 text-orange-500 animate-pulse" />
            <span className="text-stone-500 dark:text-stone-400">En vivo:</span>
            <span className="font-extrabold text-blue-600 dark:text-blue-400">Lider</span>
            <span className="text-orange-200 dark:text-stone-600">•</span>
            <span className="font-extrabold text-emerald-600 dark:text-emerald-400">Jumbo</span>
            <span className="text-orange-200 dark:text-stone-600">•</span>
            <span className="font-extrabold text-rose-600 dark:text-rose-400">Santa Isabel</span>
            <span className="text-orange-200 dark:text-stone-600">•</span>
            <span className="font-extrabold text-red-600 dark:text-red-400">Unimarc</span>
          </div>

          {/* Acceso Directo a Alza de Precios (Blog Sentinela) */}
          {onSelectTab && (
            <button
              onClick={() => onSelectTab('alza-precios')}
              className={`hidden md:flex items-center space-x-1.5 px-3.5 py-2.5 rounded-2xl text-xs font-black transition-all active:scale-95 cursor-pointer select-none ${
                activeTab === 'alza-precios'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/25'
                  : 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border border-emerald-200/80 dark:border-emerald-800/40 hover:bg-emerald-100 dark:hover:bg-emerald-900/40'
              }`}
              title="Ver el blog del Sentinela con auditoría de alza de precios"
            >
              <TrendingUp className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Alza de Precios</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-black ${
                activeTab === 'alza-precios' ? 'bg-emerald-800 text-white' : 'bg-emerald-600 text-white'
              }`}>Blog</span>
            </button>
          )}

          {/* Botón Selector de Tema Claro / Oscuro con Icono y Texto */}
          <button
            id="theme-toggle-btn"
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onToggleDarkMode();
            }}
            aria-label={isDarkMode ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
            title={isDarkMode ? 'Activar modo claro' : 'Activar modo oscuro'}
            className="flex items-center space-x-2 px-3 sm:px-4 py-2 sm:py-2.5 rounded-2xl bg-stone-100 dark:bg-stone-800 text-stone-800 dark:text-stone-100 border border-stone-200 dark:border-stone-700 hover:bg-stone-200 dark:hover:bg-stone-700 transition-all shadow-xs active:scale-95 cursor-pointer select-none"
          >
            {isDarkMode ? (
              <>
                <Sun className="w-4 h-4 text-amber-400" />
                <span className="text-xs sm:text-sm font-bold">Modo Claro</span>
              </>
            ) : (
              <>
                <Moon className="w-4 h-4 text-stone-700" />
                <span className="text-xs sm:text-sm font-bold">Modo Oscuro</span>
              </>
            )}
          </button>

          <button
            onClick={onOpenMyAlerts}
            className="flex items-center space-x-2 bg-white dark:bg-stone-800 hover:bg-orange-50 dark:hover:bg-stone-700 text-orange-700 dark:text-orange-400 border border-orange-200 dark:border-stone-700 hover:border-orange-300 dark:hover:border-stone-600 px-4 sm:px-5 py-2.5 sm:py-3 rounded-2xl text-xs sm:text-sm font-extrabold transition-all shadow-xs active:scale-95"
          >
            <Bell className="w-4 h-4 text-orange-500" />
            <span className="hidden xs:inline">Avisos WhatsApp</span>
            <span className="xs:hidden">Alertas</span>
          </button>
        </div>
      </div>
    </header>
  );
};
