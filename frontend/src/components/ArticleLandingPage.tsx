import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  Share2,
  Calendar,
  Clock,
  ExternalLink,
  ShieldAlert,
  TrendingUp,
  TrendingDown,
  Compass,
  Sparkles,
  Search,
  Copy,
  Check,
  Instagram,
  ShoppingBag,
  CheckCircle2,
  ChevronRight,
  Info,
  Layers,
  ArrowRight
} from 'lucide-react';
import { SentinelaArticle } from '../types';

interface ArticleLandingPageProps {
  article: SentinelaArticle;
  articles: SentinelaArticle[];
  getImage: (article: SentinelaArticle | null | undefined) => string;
  onBack: () => void;
  onSelectArticle: (article: SentinelaArticle) => void;
  onOpenInstagramStory: (article: SentinelaArticle) => void;
  onSearchProduct?: (query: string) => void;
}

export const ArticleLandingPage: React.FC<ArticleLandingPageProps> = ({
  article,
  articles,
  getImage,
  onBack,
  onSelectArticle,
  onOpenInstagramStory,
  onSearchProduct
}) => {
  const [copied, setCopied] = useState(false);

  // URL canónica para compartir
  const currentUrl = typeof window !== 'undefined' ? window.location.href : '';

  // Actualizar el título de la página para SEO y previsualización en pestañas
  useEffect(() => {
    const originalTitle = document.title;
    document.title = `${article.title} | Blog Sentinela Ofertis`;
    window.scrollTo({ top: 0, behavior: 'smooth' });

    return () => {
      document.title = originalTitle;
    };
  }, [article]);

  const handleCopyLink = () => {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(currentUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const handleShareFacebook = () => {
    const fbUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(currentUrl)}`;
    window.open(fbUrl, '_blank', 'noopener,noreferrer,width=600,height=500');
  };

  const handleShareWhatsApp = () => {
    const text = `📢 *Alerta de Precios en Ofertis*: ${article.title}\n\nRevisa el informe completo y cuándo impactará en supermercados:\n${currentUrl}`;
    const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
    window.open(waUrl, '_blank', 'noopener,noreferrer');
  };

  const handleShareTwitter = () => {
    const text = `Alerta Sentinela @OfertisCL: ${article.title}`;
    const twUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(currentUrl)}`;
    window.open(twUrl, '_blank', 'noopener,noreferrer,width=600,height=500');
  };

  // Cálculo de ventana de alza / impacto
  const getPriceHikeWindow = (isoDate: string, minDays: number, maxDays: number) => {
    try {
      const pubDate = new Date(isoDate);
      if (isNaN(pubDate.getTime())) return null;

      const startDate = new Date(pubDate);
      startDate.setDate(startDate.getDate() + minDays);

      const endDate = new Date(pubDate);
      endDate.setDate(endDate.getDate() + maxDays);

      const months = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
      const dayStart = startDate.getDate();
      const monthStart = months[startDate.getMonth()];
      const yearStart = startDate.getFullYear();

      const dayEnd = endDate.getDate();
      const monthEnd = months[endDate.getMonth()];
      const yearEnd = endDate.getFullYear();

      let rangeText = '';
      if (yearStart === yearEnd) {
        if (monthStart === monthEnd) {
          rangeText = `${dayStart} al ${dayEnd} de ${monthStart} de ${yearStart}`;
        } else {
          rangeText = `${dayStart} de ${monthStart} al ${dayEnd} de ${monthEnd} de ${yearStart}`;
        }
      } else {
        rangeText = `${dayStart} de ${monthStart} de ${yearStart} al ${dayEnd} de ${monthEnd} de ${yearEnd}`;
      }

      return {
        startDate,
        endDate,
        rangeText
      };
    } catch {
      return null;
    }
  };

  const hikeWindow = getPriceHikeWindow(article.date, article.lag_days_min, article.lag_days_max);

  const formatPublicationDate = (isoDate: string) => {
    try {
      const d = new Date(isoDate);
      if (isNaN(d.getTime())) return isoDate;
      const months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
      const day = d.getDate();
      const month = months[d.getMonth()];
      const year = d.getFullYear();
      const hours = d.getHours().toString().padStart(2, '0');
      const mins = d.getMinutes().toString().padStart(2, '0');
      return `${day} de ${month} de ${year} a las ${hours}:${mins} hrs`;
    } catch {
      return isoDate;
    }
  };

  const isAlza = (article.trend_direction || 'ALZA').toUpperCase() === 'ALZA';
  const isBaja = (article.trend_direction || '').toUpperCase() === 'BAJA';

  // Artículos recomendados / relacionados (excluyendo el actual)
  const relatedArticles = articles
    .filter((a) => a.id !== article.id)
    .slice(0, 3);

  // Primer producto afectado para el CTA principal
  const primaryProduct = (article.affected_products && article.affected_products[0]) || 'canasta básica';

  return (
    <article className="max-w-4xl mx-auto space-y-8 animate-fade-in pb-16">
      {/* 1. Barra Superior de Navegación y Acciones */}
      <nav className="flex flex-wrap items-center justify-between gap-4 py-2 border-b border-stone-200 dark:border-stone-800">
        <button
          onClick={onBack}
          className="inline-flex items-center space-x-2 text-sm font-bold text-stone-700 hover:text-emerald-700 dark:text-stone-300 dark:hover:text-emerald-400 transition-colors cursor-pointer group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span>Volver al radar de alertas</span>
        </button>

        {/* Botones rápidos de compartir en el top */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleShareFacebook}
            className="p-2 rounded-xl bg-blue-50 text-blue-700 hover:bg-blue-100 dark:bg-blue-950/40 dark:text-blue-300 transition-colors cursor-pointer"
            title="Compartir en Facebook"
            aria-label="Compartir en Facebook"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
            </svg>
          </button>

          <button
            onClick={handleShareWhatsApp}
            className="p-2 rounded-xl bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-950/40 dark:text-emerald-300 transition-colors cursor-pointer"
            title="Compartir por WhatsApp"
            aria-label="Compartir por WhatsApp"
          >
            <Share2 className="w-4 h-4" />
          </button>

          <button
            onClick={handleCopyLink}
            className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              copied
                ? 'bg-emerald-600 text-white'
                : 'bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 hover:bg-stone-200 dark:hover:bg-stone-700'
            }`}
          >
            {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? '¡Enlace copiado!' : 'Copiar link'}</span>
          </button>

          <button
            onClick={() => onOpenInstagramStory(article)}
            className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-xl text-xs font-bold text-pink-600 bg-pink-50 hover:bg-pink-100 dark:bg-pink-950/40 dark:text-pink-300 transition-colors cursor-pointer"
          >
            <Instagram className="w-3.5 h-3.5" />
            <span>Story</span>
          </button>
        </div>
      </nav>

      {/* 2. Hero Header de la Landing Page */}
      <header className="space-y-4">
        {/* Breadcrumb temático */}
        <div className="flex flex-wrap items-center gap-2 text-xs font-bold text-stone-500 dark:text-stone-400">
          <span>Ofertis</span>
          <ChevronRight className="w-3 h-3" />
          <span className="text-emerald-800 dark:text-emerald-400">Blog Sentinela</span>
          <ChevronRight className="w-3 h-3" />
          <span className="bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 px-2.5 py-0.5 rounded-md">
            {article.category_label || article.category}
          </span>
        </div>

        {/* Insignia de Dirección de Tendencia */}
        <div className="flex flex-wrap items-center gap-3">
          <span
            className={`inline-flex items-center space-x-1.5 text-xs font-black px-3.5 py-1.5 rounded-full tracking-wider uppercase shadow-xs ${
              isAlza
                ? 'bg-red-100 text-red-800 border border-red-300 dark:bg-red-950/70 dark:text-red-300 dark:border-red-800'
                : isBaja
                ? 'bg-emerald-100 text-emerald-800 border border-emerald-300 dark:bg-emerald-950/70 dark:text-emerald-300 dark:border-emerald-800'
                : 'bg-amber-100 text-amber-800 border border-amber-300 dark:bg-amber-950/70 dark:text-amber-300 dark:border-amber-800'
            }`}
          >
            {isAlza ? (
              <TrendingUp className="w-4 h-4 text-red-600 dark:text-red-400" />
            ) : isBaja ? (
              <TrendingDown className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            ) : (
              <Compass className="w-4 h-4 text-amber-600 dark:text-amber-400" />
            )}
            <span>
              {isAlza
                ? 'Alerta Preventiva de Alza en Supermercados'
                : isBaja
                ? 'Oportunidad de Baja y Ahorro Inminente'
                : 'Tendencia en Cadena Alimentaria'}
            </span>
          </span>

          <span
            className={`text-xs font-extrabold px-3 py-1 rounded-lg ${
              article.severity === 'ALTA'
                ? 'bg-red-50 text-red-700 border border-red-200 dark:bg-red-950/40 dark:text-red-400 dark:border-red-800'
                : 'bg-stone-100 text-stone-700 border border-stone-200 dark:bg-stone-800 dark:text-stone-300'
            }`}
          >
            Severidad {article.severity}
          </span>

          <span className="text-xs text-stone-500 font-bold ml-auto">
            Boletín #{article.bulletin_id}
          </span>
        </div>

        {/* Titular Principal H1 */}
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-stone-900 dark:text-white tracking-tight leading-tight">
          {article.title}
        </h1>

        {/* Bajada o Subtítulo */}
        {article.headline && (
          <p className="text-lg sm:text-xl font-medium text-stone-600 dark:text-stone-300 leading-relaxed">
            {article.headline}
          </p>
        )}

        {/* Metadata de Publicación */}
        <div className="flex flex-wrap items-center gap-y-2 gap-x-4 pt-2 text-xs text-stone-600 dark:text-stone-400 border-t border-stone-100 dark:border-stone-800">
          <div className="flex items-center space-x-1.5">
            <Clock className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span>Publicado: <strong className="text-stone-900 dark:text-stone-200">{formatPublicationDate(article.date)}</strong></span>
          </div>

          <div className="flex items-center space-x-1.5">
            <ShieldAlert className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span>Auditoría: <strong className="text-stone-900 dark:text-stone-200">Agente Sentinela Ofertis</strong></span>
          </div>

          <div className="flex items-center space-x-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span>Certeza Causal: <strong className="text-stone-900 dark:text-stone-200">{Math.round(article.confidence_score * 100)}%</strong></span>
          </div>
        </div>
      </header>

      {/* 3. Fotografía Editorial de Alta Resolución */}
      <div className="relative rounded-3xl overflow-hidden shadow-xl border border-stone-200 dark:border-stone-800 bg-stone-100 aspect-16/9 sm:aspect-21/9 max-h-[460px]">
        <img
          src={getImage(article)}
          alt={article.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent pointer-events-none" />

        {/* Frase inferior en la foto */}
        <div className="absolute bottom-4 left-6 right-6 text-white flex flex-wrap items-center justify-between gap-2">
          <div className="text-xs sm:text-sm font-semibold text-stone-200 drop-shadow-md">
            Monitoreo oficial de precios y abastecimiento agroalimentario
          </div>
          <div className="text-xs bg-black/50 backdrop-blur-xs px-3 py-1 rounded-full text-stone-300 font-medium">
            Fuente: {article.source_name}
          </div>
        </div>
      </div>

      {/* 4. Ventana de Impacto en Góndola (Tarjeta destacada) */}
      <div className="bg-emerald-50 dark:bg-emerald-950/40 border-2 border-emerald-300 dark:border-emerald-800 rounded-3xl p-6 sm:p-8 shadow-sm space-y-3">
        <div className="flex items-center space-x-2 text-xs font-black uppercase tracking-wider text-emerald-900 dark:text-emerald-300">
          <Calendar className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          <span>Ventana Proyectada de Impacto en Supermercados:</span>
        </div>

        <div className="text-2xl sm:text-3xl font-black text-emerald-950 dark:text-white">
          {hikeWindow ? `Del ${hikeWindow.rangeText}` : `En ${article.lag_days_min} a ${article.lag_days_max} días`}
        </div>

        <p className="text-xs sm:text-sm text-stone-700 dark:text-stone-300 leading-relaxed font-medium">
          Calculado en un plazo de <strong>{article.lag_days_min} a {article.lag_days_max} días</strong> desde la emisión del informe,
          correspondiente al tiempo promedio de recambio de inventario entre mayoristas/distribuidores y las góndolas de retail.
        </p>
      </div>

      {/* 5. Mecanismo de Transmisión Económica */}
      <section className="space-y-4">
        <h2 className="text-xl sm:text-2xl font-black text-stone-900 dark:text-white flex items-center space-x-2">
          <Layers className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          <span>Diagnóstico y Mecanismo de Transmisión</span>
        </h2>

        <div className="bg-white dark:bg-stone-900 rounded-3xl p-6 sm:p-8 border border-stone-200 dark:border-stone-800 shadow-sm space-y-4 text-stone-800 dark:text-stone-200 leading-relaxed">
          <p className="text-base sm:text-lg font-medium">
            {article.transmission_mechanism}
          </p>

          <div className="pt-4 border-t border-stone-100 dark:border-stone-800 flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="text-stone-500 dark:text-stone-400">
              <span>Tipo de evento económico: </span>
              <strong className="text-stone-800 dark:text-stone-200 font-bold">{article.event_type}</strong>
            </div>

            {article.source_url && (
              <a
                href={article.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-1.5 text-emerald-700 dark:text-emerald-400 font-bold hover:underline"
              >
                <span>Ver documento o fuente primaria</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
          </div>
        </div>
      </section>

      {/* 6. CTA INTERACTIVO DE OFERTIS (Conversión de Tráfico) */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-orange-500 via-orange-600 to-amber-600 text-white p-6 sm:p-10 shadow-2xl space-y-6">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-white/10 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 space-y-2">
          <div className="inline-flex items-center space-x-1.5 bg-white/20 backdrop-blur-xs text-white text-xs font-black px-3.5 py-1 rounded-full uppercase tracking-wider">
            <ShoppingBag className="w-4 h-4" />
            <span>Comparador en Tiempo Real Ofertis</span>
          </div>

          <h3 className="text-2xl sm:text-3xl font-black text-white leading-tight">
            ¿Quieres saber cuánto cuesta hoy en Lider, Jumbo, Santa Isabel y Unimarc?
          </h3>

          <p className="text-sm sm:text-base text-orange-100 max-w-2xl font-medium">
            En Ofertis rastreamos los precios de góndola en tiempo real para que encuentres la tienda más conveniente antes de salir de casa.
          </p>
        </div>

        {/* Productos Afectados con Botones de Búsqueda Directa */}
        <div className="relative z-10 space-y-3">
          <div className="text-xs font-black uppercase tracking-wider text-orange-200">
            Compara estos productos directamente:
          </div>

          <div className="flex flex-wrap gap-2">
            {(article.affected_products || []).map((prod) => (
              <button
                key={prod}
                onClick={() => onSearchProduct && onSearchProduct(prod)}
                className="inline-flex items-center space-x-2 bg-white text-orange-950 hover:bg-orange-50 text-xs sm:text-sm font-extrabold px-4 py-2.5 rounded-2xl shadow-md transition-all hover:scale-105 cursor-pointer"
              >
                <Search className="w-4 h-4 text-orange-600" />
                <span>Comparar "{prod}"</span>
                <ArrowRight className="w-3.5 h-3.5 text-orange-400" />
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* 7. Recomendación para el Consumidor y Estrategia Familiar */}
      <section className="bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800 rounded-3xl p-6 sm:p-8 space-y-3">
        <div className="flex items-center space-x-2 text-sm font-black text-emerald-900 dark:text-emerald-300">
          <Sparkles className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          <span>Estrategia Recomendada al Consumidor Ciudadano</span>
        </div>

        <p className="text-sm sm:text-base text-stone-800 dark:text-stone-200 leading-relaxed font-medium">
          {(article.consumer_advice || '').replace('💡 Consejo Sentinela: ', '')}
        </p>
      </section>

      {/* 8. Botones Grandes de Compartir en Redes Sociales (Facebook, WhatsApp, X) */}
      <section className="bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-3xl p-6 sm:p-8 shadow-sm space-y-4">
        <div className="space-y-1">
          <h4 className="text-base font-black text-stone-900 dark:text-white">
            Comparte esta alerta con tu familia o vecinos
          </h4>
          <p className="text-xs sm:text-sm text-stone-500 dark:text-stone-400">
            Ayuda a que más personas planifiquen sus compras y cuiden su presupuesto mensual.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Facebook */}
          <button
            onClick={handleShareFacebook}
            className="flex items-center justify-center space-x-2 bg-[#1877F2] hover:bg-[#0c63d4] text-white font-bold text-xs py-3 px-4 rounded-2xl shadow-sm transition-all cursor-pointer"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
            </svg>
            <span>Compartir en Facebook</span>
          </button>

          {/* WhatsApp */}
          <button
            onClick={handleShareWhatsApp}
            className="flex items-center justify-center space-x-2 bg-[#25D366] hover:bg-[#20ba59] text-white font-bold text-xs py-3 px-4 rounded-2xl shadow-sm transition-all cursor-pointer"
          >
            <Share2 className="w-4 h-4" />
            <span>Enviar por WhatsApp</span>
          </button>

          {/* Copiar enlace */}
          <button
            onClick={handleCopyLink}
            className={`flex items-center justify-center space-x-2 border font-bold text-xs py-3 px-4 rounded-2xl transition-all cursor-pointer ${
              copied
                ? 'bg-emerald-600 text-white border-emerald-600'
                : 'bg-stone-100 dark:bg-stone-800 text-stone-800 dark:text-stone-200 border-stone-200 dark:border-stone-700 hover:bg-stone-200'
            }`}
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? '¡Enlace copiado!' : 'Copiar link directo'}</span>
          </button>
        </div>
      </section>

      {/* 9. Artículos Relacionados / Siguiente Lectura */}
      {relatedArticles.length > 0 && (
        <section className="space-y-4 pt-4 border-t border-stone-200 dark:border-stone-800">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-black text-stone-900 dark:text-white">
              Otras Alertas Recientes del Sentinela
            </h3>
            <button
              onClick={onBack}
              className="text-xs font-bold text-emerald-700 dark:text-emerald-400 hover:underline cursor-pointer"
            >
              Ver todas las alertas →
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {relatedArticles.map((rel) => {
              const relIsAlza = (rel.trend_direction || 'ALZA').toUpperCase() === 'ALZA';
              return (
                <div
                  key={rel.id}
                  onClick={() => onSelectArticle(rel)}
                  className="bg-white dark:bg-stone-900 rounded-2xl overflow-hidden border border-stone-200 dark:border-stone-800 hover:border-emerald-500 dark:hover:border-emerald-500 shadow-sm hover:shadow-md transition-all cursor-pointer flex flex-col group"
                >
                  <div className="h-28 w-full bg-stone-100 relative overflow-hidden">
                    <img
                      src={getImage(rel)}
                      alt={rel.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-2 left-2">
                      <span
                        className={`text-[10px] font-black px-2 py-0.5 rounded-md ${
                          relIsAlza ? 'bg-red-600 text-white' : 'bg-emerald-600 text-white'
                        }`}
                      >
                        {relIsAlza ? 'ALZA' : 'BAJA'}
                      </span>
                    </div>
                  </div>

                  <div className="p-4 flex-1 flex flex-col justify-between space-y-2">
                    <h4 className="text-xs font-black text-stone-900 dark:text-white line-clamp-2 leading-snug group-hover:text-emerald-700 dark:group-hover:text-emerald-400">
                      {rel.title}
                    </h4>
                    <div className="text-[11px] text-stone-500 dark:text-stone-400 font-medium">
                      Ventana: {rel.lag_days_min} a {rel.lag_days_max} días
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}
    </article>
  );
};
