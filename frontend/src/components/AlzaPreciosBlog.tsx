import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  ShieldAlert, 
  TrendingUp, 
  TrendingDown,
  Compass,
  ExternalLink, 
  Search, 
  Filter, 
  Calendar, 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  Info, 
  Sparkles, 
  FileText, 
  BookOpen, 
  ChevronRight,
  RefreshCw,
  X,
  Instagram,
  Download,
  Copy,
  Check,
} from 'lucide-react';
import { SentinelaArticle, SentinelaStats } from '../types';
import { API_BASE_URL } from '../config/api';
import { ArticleLandingPage } from './ArticleLandingPage';

export interface AlzaPreciosBlogProps {
  onSearchProduct?: (query: string) => void;
}

/**
 * Galerías temáticas curadas en alta resolución (Unsplash) por producto y factor económico.
 * Cada tema cuenta con múltiples variantes visuales de alta calidad para garantizar
 * que ninguna tarjeta ni entrada del blog repita la misma fotografía.
 */
const THEMATIC_IMAGE_POOLS: Record<string, string[]> = {
  // 1. Frutas, Hortalizas y Verduras Frescas (7 alternativas verificadas en alta resolución)
  frutas_y_verduras: [
    'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1000&q=80', // Ensaladas y hortalizas frescas de feria
    'https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=1000&q=80', // Frutas y cítricos frescos variados
    'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=1000&q=80', // Tomates rojos en huerto orgánico
    'https://images.unsplash.com/photo-1573246123716-6b1782bfc499?auto=format&fit=crop&w=1000&q=80', // Puesto de frutas y hortalizas de chacra
    'https://images.unsplash.com/photo-1566385101042-1a0aa0c1268c?auto=format&fit=crop&w=1000&q=80', // Verduras y hortalizas frescas de huerta
    'https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1000&q=80', // Canasta con vegetales y hortalizas
    'https://images.unsplash.com/photo-1519162808019-7de1683fa2ad?auto=format&fit=crop&w=1000&q=80', // Palta Hass cremosa abierta
  ],

  // 2. Carnes Rojas, Vacuno y Cortes Parrilleros (5 alternativas)
  carnes_vacuno: [
    'https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?auto=format&fit=crop&w=1000&q=80', // Cortes de vacuno premium y carnicería
    'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1000&q=80', // Carne al vacío y cortes parrilleros
    'https://images.unsplash.com/photo-1551028150-64b9f398f678?auto=format&fit=crop&w=1000&q=80', // Cortes selectos en tabla gourmet
    'https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=1000&q=80', // Carne de novillo fresca
    'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?auto=format&fit=crop&w=1000&q=80', // Asado y cortes tradicionales
  ],

  // 3. Pollo, Aves y Huevos de Granja (5 alternativas)
  pollo_huevos: [
    'https://images.unsplash.com/photo-1587593810167-a84920ea0781?auto=format&fit=crop&w=1000&q=80', // Carnes blancas y pollo en cocina
    'https://images.unsplash.com/photo-1516467508483-a7212febe31a?auto=format&fit=crop&w=1000&q=80', // Huevos de granja en nido rústico
    'https://images.unsplash.com/photo-1501200291289-c5a76c232e5f?auto=format&fit=crop&w=1000&q=80', // Huevos frescos seleccionados
    'https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=1000&q=80', // Bandeja de huevos de campo
    'https://images.unsplash.com/photo-1569058242253-92a9c755a0ec?auto=format&fit=crop&w=1000&q=80', // Presas de pollo fresco
  ],

  // 4. Granos, Harina, Masas y Panadería (5 alternativas)
  panaderia_y_harinas: [
    'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1000&q=80', // Harina y panadería artesanal
    'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=1000&q=80', // Espigas doradas de trigo y cosecha
    'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=1000&q=80', // Granos de arroz y cereales en sacos
    'https://images.unsplash.com/photo-1517433670267-08bbd4be890f?auto=format&fit=crop&w=1000&q=80', // Hogazas de pan recién horneadas
    'https://images.unsplash.com/photo-1608198093002-ad4e005484ec?auto=format&fit=crop&w=1000&q=80', // Panadería de masa madre
  ],

  // 5. Lácteos, Leche, Quesos y Mantequilla (5 alternativas)
  lacteos_derivados: [
    'https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=1000&q=80', // Botella de leche fresca de campo y vaso
    'https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=1000&q=80', // Quesos artesanales y derivados lácteos
    'https://images.unsplash.com/photo-1628088062854-d1870b4553da?auto=format&fit=crop&w=1000&q=80', // Mantequilla y quesos frescos
    'https://images.unsplash.com/photo-1528750997573-59b89d56f4f7?auto=format&fit=crop&w=1000&q=80', // Variedad de quesos de leche de vaca
    'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=1000&q=80', // Tabla de degustación de lácteos
  ],

  // 6. Tubérculos, Papas, Cebollas y Legumbres a Granel (5 alternativas)
  tuberculos_legumbres: [
    'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=1000&q=80', // Papas y hortalizas de tierra fértil
    'https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=1000&q=80', // Cebollas y ajos frescos
    'https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?auto=format&fit=crop&w=1000&q=80', // Lentejas, porotos y legumbres a granel
    'https://images.unsplash.com/photo-1594282486552-05b4d80fbb9f?auto=format&fit=crop&w=1000&q=80', // Canasta de papas cosechadas
    'https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=1000&q=80', // Pastas secas y fideos de despensa
  ],

  // 7. Pescados y Mariscos (5 alternativas)
  pescados_mariscos: [
    'https://images.unsplash.com/photo-1534483509719-3feaee7c30da?auto=format&fit=crop&w=1000&q=80', // Pescado fresco del litoral en hielo
    'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=1000&q=80', // Filetes de salmón fresco
    'https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1000&q=80', // Mariscos y frutos del mar
    'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=1000&q=80', // Pescado fresco de caleta
    'https://images.unsplash.com/photo-1509358271058-acd22cc93898?auto=format&fit=crop&w=1000&q=80', // Terminal pesquero y mariscos
  ],

  // 8. Aceites Vegetales y de Oliva (5 alternativas)
  aceites_grasas: [
    'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=1000&q=80', // Aceites vegetales y de oliva en botella
    'https://images.unsplash.com/photo-1589927986089-35812388d1f4?auto=format&fit=crop&w=1000&q=80', // Aceite de oliva y olivas maduras
    'https://images.unsplash.com/photo-1471193945509-9ad0617afabf?auto=format&fit=crop&w=1000&q=80', // Aceite vertido en almazara
    'https://images.unsplash.com/photo-1541832676-9b763b0239ab?auto=format&fit=crop&w=1000&q=80', // Aceite virgen en mesa rústica
    'https://images.unsplash.com/photo-1508746829417-e6f548d8d6ed?auto=format&fit=crop&w=1000&q=80', // Cosecha de olivas y prensado
  ],

  // 9. Análisis Canasta Básica, IPC y Ahorro Familiar (5 alternativas)
  analisis_canasta_basica: [
    'https://images.unsplash.com/photo-1578916171728-46686eac8d58?auto=format&fit=crop&w=1000&q=80', // Carrito de compras y pasillo surtido
    'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=1000&q=80', // Finanzas del hogar, boleta y calculadora
    'https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?auto=format&fit=crop&w=1000&q=80', // Monedas y ahorro familiar
    'https://images.unsplash.com/photo-1554224154-26032ffc0d07?auto=format&fit=crop&w=1000&q=80', // Contabilidad y planificación de compras
    'https://images.unsplash.com/photo-1588964895597-cfccd6e2dbf9?auto=format&fit=crop&w=1000&q=80', // Canasta de compras en supermercado
  ],

  // 10. Clima Agrícola, Riego y Logística (5 alternativas)
  clima_campo: [
    'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1000&q=80', // Valles agrícolas bajo el cielo
    'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1000&q=80', // Logística de distribución de alimentos
    'https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&w=1000&q=80', // Sistema de huerto y riego agrícola
    'https://images.unsplash.com/photo-1560493676-04071c5f467b?auto=format&fit=crop&w=1000&q=80', // Pradera y campos verdes
    'https://images.unsplash.com/photo-1595974482597-4b8da8879bc5?auto=format&fit=crop&w=1000&q=80', // Cosecha y embalaje de productos agrícolas
  ]
};

/**
 * Clasifica estrictamente un artículo para asignarle su galería fotográfica más idónea.
 * Prioriza la categoría oficial del artículo y palabras clave de productos.
 */
const getArticleThemeKey = (article: SentinelaArticle): string => {
  const cat = (article?.category || '').toLowerCase();
  const catLabel = (article?.category_label || '').toLowerCase();
  const title = (article?.title || '').toLowerCase();
  const headline = (article?.headline || '').toLowerCase();
  const mechanism = (article?.transmission_mechanism || '').toLowerCase();
  const products = (article?.affected_products || []).join(' ').toLowerCase();
  const fullText = `${cat} ${catLabel} ${title} ${headline} ${mechanism} ${products}`;

  // 1. Frutas, Hortalizas y Verduras (Garantiza que NUNCA se asigne leche a verduras)
  if (
    cat.includes('fruta') || 
    cat.includes('verdura') || 
    cat.includes('hortaliza') ||
    fullText.includes('tomate') || 
    fullText.includes('choclo') || 
    fullText.includes('lechuga') || 
    fullText.includes('zapallo') || 
    fullText.includes('pepino') || 
    fullText.includes('palta') || 
    fullText.includes('limón') || 
    fullText.includes('limon') || 
    fullText.includes('naranja') || 
    fullText.includes('manzana') || 
    fullText.includes('fruta') || 
    fullText.includes('hortaliza')
  ) {
    return 'frutas_y_verduras';
  }

  // 2. Pollo, Huevos y Aves
  if (
    cat.includes('avicola') || 
    cat.includes('pollo') || 
    cat.includes('huevo') ||
    fullText.includes('pollo') || 
    fullText.includes('huevo') || 
    fullText.includes('avícola') || 
    fullText.includes('avicola') || 
    fullText.includes('pechuga') || 
    fullText.includes('trutro')
  ) {
    return 'pollo_huevos';
  }

  // 3. Granos, Harina, Molienda y Panadería
  if (
    cat.includes('panaderia') || 
    cat.includes('molineria') || 
    cat.includes('grano') || 
    fullText.includes('harina') || 
    fullText.includes('trigo') || 
    fullText.includes('pan') || 
    fullText.includes('masas') || 
    fullText.includes('molienda') || 
    fullText.includes('cbot') || 
    fullText.includes('chicago') || 
    fullText.includes('maíz') || 
    fullText.includes('maiz') || 
    fullText.includes('soya') || 
    fullText.includes('soja')
  ) {
    return 'panaderia_y_harinas';
  }

  // 4. Carnes rojas, Vacuno, Novillo, Cerdo, Faena y Cortes parrilleros
  if (
    cat.includes('carne') || 
    cat.includes('vacuno') || 
    fullText.includes('vacuno') || 
    fullText.includes('carne') || 
    fullText.includes('cerdo') || 
    fullText.includes('novillo') || 
    fullText.includes('faena') || 
    fullText.includes('cañuelas') || 
    fullText.includes('huachalomo') || 
    fullText.includes('sobrecostilla') || 
    fullText.includes('abastero') || 
    fullText.includes('lomo')
  ) {
    return 'carnes_vacuno';
  }

  // 5. Lácteos, Leche, Quesos y Mantequilla
  if (
    cat.includes('lacteo') || 
    cat.includes('leche') || 
    fullText.includes('leche') || 
    fullText.includes('lácteo') || 
    fullText.includes('lacteo') || 
    fullText.includes('queso') || 
    fullText.includes('mantequilla') || 
    fullText.includes('yogur')
  ) {
    return 'lacteos_derivados';
  }

  // 6. Tubérculos, Papas, Cebollas y Legumbres a granel
  if (
    cat.includes('tuberculo') || 
    cat.includes('legumbre') || 
    fullText.includes('papa') || 
    fullText.includes('cebolla') || 
    fullText.includes('lenteja') || 
    fullText.includes('poroto') || 
    fullText.includes('garbanzo') || 
    fullText.includes('zanahoria') || 
    fullText.includes('fideo') || 
    fullText.includes('pasta') || 
    fullText.includes('arroz')
  ) {
    return 'tuberculos_legumbres';
  }

  // 7. Pescados y Mariscos
  if (
    cat.includes('pescado') || 
    cat.includes('marisco') || 
    fullText.includes('pescado') || 
    fullText.includes('jurel') || 
    fullText.includes('atún') || 
    fullText.includes('atun') || 
    fullText.includes('merluza') || 
    fullText.includes('salmón') || 
    fullText.includes('marisco')
  ) {
    return 'pescados_mariscos';
  }

  // 8. Aceites y Grasas
  if (
    cat.includes('aceite') || 
    fullText.includes('aceite') || 
    fullText.includes('maravilla') || 
    fullText.includes('oliva')
  ) {
    return 'aceites_grasas';
  }

  // 9. Clima, Riego y Logística Agropecuaria
  if (
    cat.includes('clima') || 
    fullText.includes('helada') || 
    fullText.includes('sequía') || 
    fullText.includes('riego') || 
    fullText.includes('campo')
  ) {
    return 'clima_campo';
  }

  // 10. Por defecto: Análisis de la Canasta Básica, Ahorro e IPC
  return 'analisis_canasta_basica';
};

/**
 * Construye un mapa inteligente que asigna a cada artículo una fotografía temática no repetida.
 * - Mantiene aislamiento estricto por categoría (una entrada de verduras NUNCA usará fotos de leche ni carnes).
 * - Cuenta con al menos 5 alternativas por tema.
 */
const buildArticleImageMap = (articlesList: SentinelaArticle[]): Map<string, string> => {
  const map = new Map<string, string>();
  const usedPerTheme: Record<string, Set<string>> = {};

  articlesList.forEach((art, idx) => {
    if (!art) return;
    const artKey = art.id || `art_${idx}`;
    const themeKey = getArticleThemeKey(art);
    const pool = THEMATIC_IMAGE_POOLS[themeKey] || THEMATIC_IMAGE_POOLS.frutas_y_verduras;

    if (!usedPerTheme[themeKey]) {
      usedPerTheme[themeKey] = new Set<string>();
    }
    const themeUsed = usedPerTheme[themeKey];

    // 1. Buscar una foto dentro de SU PROPIA CATEGORÍA que aún no se haya usado
    let selectedImg = pool.find((img) => !themeUsed.has(img));

    // 2. Si se agotaron las alternativas de esa categoría, rotar cíclicamente dentro de SU MISMA CATEGORÍA.
    // NUNCA cruzar de categoría.
    if (!selectedImg) {
      const cycleIndex = themeUsed.size % pool.length;
      selectedImg = pool[cycleIndex];
    }

    themeUsed.add(selectedImg);
    map.set(artKey, selectedImg);
  });

  return map;
};

interface DirectionMeta {
  badgeLabel: string;
  badgeBg: string;
  badgeText: string;
  badgeBorder: string;
  heroTag: string;
  heroTagBg: string;
  datesPrefix: string;
  datesTitle: string;
  productsTitle: string;
  mechanismTitle: string;
  adviceTitle: string;
  accentColor: string;
  type: 'ALZA' | 'BAJA' | 'TENDENCIA';
}

const getDirectionMeta = (direction?: string): DirectionMeta => {
  const dir = (direction || 'ALZA').toUpperCase();
  if (dir === 'BAJA') {
    return {
      badgeLabel: '🟢 Oportunidad de Baja',
      badgeBg: 'bg-emerald-50 dark:bg-emerald-950/50',
      badgeText: 'text-emerald-700 dark:text-emerald-300',
      badgeBorder: 'border-emerald-300 dark:border-emerald-700',
      heroTag: 'OPORTUNIDAD DE AHORRO',
      heroTagBg: 'bg-emerald-600',
      datesPrefix: 'Baja proyectada:',
      datesTitle: 'Rango estimado de baja / ahorro en góndolas:',
      productsTitle: 'Productos con oportunidad de baja de precio:',
      mechanismTitle: 'Mecanismo de Descompresión de Precios (Por qué bajará):',
      adviceTitle: 'Consejo de Ahorro Sentinela:',
      accentColor: 'text-emerald-600 dark:text-emerald-400',
      type: 'BAJA'
    };
  }
  if (dir === 'TENDENCIA') {
    return {
      badgeLabel: '🔵 Tema de Interés',
      badgeBg: 'bg-sky-50 dark:bg-sky-950/50',
      badgeText: 'text-sky-700 dark:text-sky-300',
      badgeBorder: 'border-sky-300 dark:border-sky-700',
      heroTag: 'GUÍA CIUDADANA Y TENDENCIA',
      heroTagBg: 'bg-sky-600',
      datesPrefix: 'Vigencia:',
      datesTitle: 'Vigencia de la recomendación y proyección:',
      productsTitle: 'Categorías y alimentos analizados:',
      mechanismTitle: 'Contexto Económico y Dinámica de Mercado:',
      adviceTitle: 'Recomendación Estratégica Sentinela:',
      accentColor: 'text-sky-600 dark:text-sky-400',
      type: 'TENDENCIA'
    };
  }
  return {
    badgeLabel: '🔴 Alza Proyectada',
    badgeBg: 'bg-red-50 dark:bg-red-950/50',
    badgeText: 'text-red-700 dark:text-red-300',
    badgeBorder: 'border-red-300 dark:border-red-700',
    heroTag: 'ALERTA DE ALZA',
    heroTagBg: 'bg-red-600',
    datesPrefix: 'Alza proyectada:',
    datesTitle: 'Rango proyectado de alza en góndolas:',
    productsTitle: 'Góndolas con riesgo inminente de alza:',
    mechanismTitle: 'Cadena de Transmisión Económica (Por qué subirá):',
    adviceTitle: 'Consejo Estratégico Sentinela:',
    accentColor: 'text-red-600 dark:text-red-400',
    type: 'ALZA'
  };
};

/**
 * Formatea la fecha y hora de publicación en español de Chile
 * Ejemplo: "07 de septiembre de 2026 a las 02:10 hrs"
 */
const formatPublicationDateTime = (dateStr: string): string => {
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    const day = d.getDate();
    const month = d.toLocaleDateString('es-CL', { month: 'long' });
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    return `${day} de ${month} de ${year} a las ${hours}:${minutes} hrs`;
  } catch {
    return dateStr;
  }
};

/**
 * Formato compacto de fecha y hora para cards
 * Ejemplo: "07 sep 2026, 02:10 hrs"
 */
const formatPublicationShort = (dateStr: string): string => {
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    const day = d.getDate();
    const month = d.toLocaleDateString('es-CL', { month: 'short' }).replace('.', '');
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    return `${day} ${month} ${year}, ${hours}:${minutes} hrs`;
  } catch {
    return dateStr;
  }
};

interface PriceHikeWindow {
  rangeText: string;
  shortRangeText: string;
}

/**
 * Calcula el rango proyectado de fechas en que el alza llegará a la góndola
 * en base a la fecha de publicación y los días de rezago mínimo y máximo.
 */
const getPriceHikeWindow = (dateStr: string, minDays: number, maxDays: number): PriceHikeWindow => {
  try {
    const base = new Date(dateStr);
    const minD = Math.max(1, minDays || 0);
    const maxD = Math.max(minD, maxDays || minD);

    const startDate = new Date(base.getTime() + minD * 24 * 60 * 60 * 1000);
    const endDate = new Date(base.getTime() + maxD * 24 * 60 * 60 * 1000);

    const startDay = startDate.getDate();
    const endDay = endDate.getDate();
    const startMonthLong = startDate.toLocaleDateString('es-CL', { month: 'long' });
    const endMonthLong = endDate.toLocaleDateString('es-CL', { month: 'long' });
    const startMonthShort = startDate.toLocaleDateString('es-CL', { month: 'short' }).replace('.', '');
    const endMonthShort = endDate.toLocaleDateString('es-CL', { month: 'short' }).replace('.', '');
    const startYear = startDate.getFullYear();
    const endYear = endDate.getFullYear();

    let rangeText = '';
    let shortRangeText = '';

    if (startYear === endYear) {
      if (startMonthLong === endMonthLong) {
        rangeText = `${startDay} al ${endDay} de ${startMonthLong} de ${startYear}`;
        shortRangeText = `${startDay} al ${endDay} ${startMonthShort}`;
      } else {
        rangeText = `${startDay} de ${startMonthLong} al ${endDay} de ${endMonthLong} de ${startYear}`;
        shortRangeText = `${startDay} ${startMonthShort} al ${endDay} ${endMonthShort}`;
      }
    } else {
      rangeText = `${startDay} de ${startMonthLong} de ${startYear} al ${endDay} de ${endMonthLong} de ${endYear}`;
      shortRangeText = `${startDay} ${startMonthShort} ${startYear} al ${endDay} ${endMonthShort} ${endYear}`;
    }

    return { rangeText, shortRangeText };
  } catch {
    return {
      rangeText: `En ${minDays} a ${maxDays} días`,
      shortRangeText: `${minDays}-${maxDays} días`
    };
  }
};

/**
 * Obtiene la imagen editorial oficial en formato 9:16 según el tema y dirección del artículo
 */
const getEditorialStoryImage = (art: SentinelaArticle): string => {
  const dir = (art.trend_direction || '').toUpperCase();
  const theme = getArticleThemeKey(art);
  if (dir === 'BAJA' || theme === 'frutas_y_verduras') {
    return '/instagram/story_baja_tomates.jpg';
  }
  if (dir === 'TENDENCIA' || theme === 'analisis_canasta_basica') {
    return '/instagram/story_ipc_canasta.jpg';
  }
  return '/instagram/story_alza_granos.jpg';
};

/**
 * Genera el copy/caption listo para publicar en Instagram con emojis y hashtags chilenos
 */
const generateInstagramCaption = (art: SentinelaArticle): string => {
  const dir = (art.trend_direction || 'ALZA').toUpperCase();
  const dirMeta = getDirectionMeta(art.trend_direction);
  const dirBadge = dir === 'BAJA' ? '🟢 OPORTUNIDAD DE AHORRO' : dir === 'TENDENCIA' ? '🔵 GUÍA Y TENDENCIA' : '🔴 ALERTA DE ALZA';
  const products = (art.affected_products || []).join(', ');
  const hikeWindow = getPriceHikeWindow(art.date, art.lag_days_min, art.lag_days_max);
  const adviceClean = (art.consumer_advice || 'Compara precios en comercios locales y supermercados antes de comprar.').replace('💡 Consejo Sentinela: ', '');

  return `🚨 ¡ALERTA SENTINELA OFERTIS! 🚨
${dirBadge}

📌 ${art.title}

🛒 Productos en seguimiento:
${products || 'Canasta básica familiar'}

📅 ${dirMeta.datesPrefix}: ${hikeWindow.rangeText} (${hikeWindow.shortRangeText})

💡 Consejo Sentinela para tu bolsillo:
${adviceClean}

🏢 Fuente monitoreada: ${art.source_name || 'ODEPA / INE'}
🔎 ¡Anticípate y ahorra hasta un 35% comparando en ofertis.vercel.app!

—
#Ofertis #Sentinela #AlertaDePrecios #AhorroChile #InflacionChile #SupermercadosChile #PreciosBajos #CanastaBasica #LoValledor #EconomiaFamiliar #Chile`;
};

/**
 * Genera y descarga un gráfico 1080x1920 en formato PNG para Instagram Story
 */
const downloadCanvasStory = (art: SentinelaArticle) => {
  const canvas = document.createElement('canvas');
  canvas.width = 1080;
  canvas.height = 1920;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const dir = (art.trend_direction || 'ALZA').toUpperCase();
  const isBaja = dir === 'BAJA';
  const isTendencia = dir === 'TENDENCIA';

  // 1. Fondo degradado 9:16
  const bgGrad = ctx.createLinearGradient(0, 0, 0, 1920);
  if (isBaja) {
    bgGrad.addColorStop(0, '#064e3b');
    bgGrad.addColorStop(0.35, '#022c22');
    bgGrad.addColorStop(1, '#050d0a');
  } else if (isTendencia) {
    bgGrad.addColorStop(0, '#1e3a8a');
    bgGrad.addColorStop(0.35, '#172554');
    bgGrad.addColorStop(1, '#030712');
  } else {
    bgGrad.addColorStop(0, '#7f1d1d');
    bgGrad.addColorStop(0.35, '#450a0a');
    bgGrad.addColorStop(1, '#0a0505');
  }
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, 1080, 1920);

  // Círculo ambiental
  ctx.fillStyle = isBaja ? 'rgba(16, 185, 129, 0.12)' : isTendencia ? 'rgba(59, 130, 246, 0.12)' : 'rgba(239, 68, 68, 0.12)';
  ctx.beginPath();
  ctx.arc(540, 360, 420, 0, Math.PI * 2);
  ctx.fill();

  // 2. Encabezado
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 36px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('🛡️ AGENTE SENTINELA · OFERTIS', 540, 120);

  // 3. Badge Superior
  const badgeText = isBaja ? '🟢 OPORTUNIDAD DE BAJA' : isTendencia ? '🔵 GUÍA CIUDADANA' : '🔴 ALERTA DE ALZA';
  ctx.fillStyle = isBaja ? '#10b981' : isTendencia ? '#3b82f6' : '#ef4444';
  ctx.beginPath();
  if (ctx.roundRect) {
    ctx.roundRect(540 - 240, 170, 480, 68, 34);
  } else {
    ctx.rect(540 - 240, 170, 480, 68);
  }
  ctx.fill();

  ctx.fillStyle = '#ffffff';
  ctx.font = '900 30px sans-serif';
  ctx.fillText(badgeText, 540, 215);

  // 4. Título Principal
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 52px sans-serif';
  ctx.textAlign = 'center';

  const titleWords = art.title.split(' ');
  let line = '';
  let y = 350;
  for (let n = 0; n < titleWords.length; n++) {
    const testLine = line + titleWords[n] + ' ';
    const metrics = ctx.measureText(testLine);
    if (metrics.width > 920 && n > 0) {
      ctx.fillText(line.trim(), 540, y);
      line = titleWords[n] + ' ';
      y += 66;
    } else {
      line = testLine;
    }
  }
  ctx.fillText(line.trim(), 540, y);

  // 5. Tarjeta de Productos
  const cardY = Math.max(y + 60, 640);
  ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.strokeStyle = isBaja ? 'rgba(16, 185, 129, 0.5)' : isTendencia ? 'rgba(59, 130, 246, 0.5)' : 'rgba(239, 68, 68, 0.5)';
  ctx.lineWidth = 3;
  if (ctx.roundRect) {
    ctx.beginPath();
    ctx.roundRect(80, cardY, 920, 320, 28);
    ctx.fill();
    ctx.stroke();
  } else {
    ctx.fillRect(80, cardY, 920, 320);
    ctx.strokeRect(80, cardY, 920, 320);
  }

  ctx.fillStyle = isBaja ? '#34d399' : isTendencia ? '#60a5fa' : '#f87171';
  ctx.font = 'bold 30px sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('🛒 PRODUCTOS EN SEGUIMIENTO:', 120, cardY + 60);

  ctx.fillStyle = '#f3f4f6';
  ctx.font = '500 32px sans-serif';
  const prods = (art.affected_products || []).slice(0, 4);
  prods.forEach((p, idx) => {
    ctx.fillText(`• ${p}`, 120, cardY + 120 + idx * 50);
  });

  // 6. Tarjeta de Fechas
  const datesY = cardY + 360;
  const hikeWindow = getPriceHikeWindow(art.date, art.lag_days_min, art.lag_days_max);
  const dirMeta = getDirectionMeta(art.trend_direction);
  ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
  if (ctx.roundRect) {
    ctx.beginPath();
    ctx.roundRect(80, datesY, 920, 180, 28);
    ctx.fill();
  }

  ctx.fillStyle = '#fbbf24';
  ctx.font = 'bold 28px sans-serif';
  ctx.fillText(`📅 ${dirMeta.datesTitle.toUpperCase()}`, 120, datesY + 60);

  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 36px sans-serif';
  ctx.fillText(`${hikeWindow.rangeText} (${hikeWindow.shortRangeText})`, 120, datesY + 120);

  // 7. Tarjeta de Consejo
  const tipY = datesY + 220;
  ctx.fillStyle = isBaja ? 'rgba(5, 150, 105, 0.3)' : isTendencia ? 'rgba(37, 99, 235, 0.3)' : 'rgba(220, 38, 38, 0.3)';
  ctx.strokeStyle = isBaja ? '#10b981' : isTendencia ? '#3b82f6' : '#ef4444';
  ctx.lineWidth = 2;
  if (ctx.roundRect) {
    ctx.beginPath();
    ctx.roundRect(80, tipY, 920, 300, 28);
    ctx.fill();
    ctx.stroke();
  }

  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 30px sans-serif';
  ctx.fillText('💡 CONSEJO ESTRATÉGICO OFERTIS:', 120, tipY + 60);

  ctx.fillStyle = '#e5e7eb';
  ctx.font = '400 28px sans-serif';
  const adviceWords = (art.consumer_advice || 'Compara precios antes de comprar.').replace('💡 Consejo Sentinela: ', '').split(' ');
  let tipLine = '';
  let tipCurY = tipY + 115;
  for (let n = 0; n < adviceWords.length; n++) {
    const testLine = tipLine + adviceWords[n] + ' ';
    const metrics = ctx.measureText(testLine);
    if (metrics.width > 840 && n > 0) {
      ctx.fillText(tipLine.trim(), 120, tipCurY);
      tipLine = adviceWords[n] + ' ';
      tipCurY += 46;
      if (tipCurY > tipY + 260) break;
    } else {
      tipLine = testLine;
    }
  }
  ctx.fillText(tipLine.trim(), 120, tipCurY);

  // 8. Footer
  ctx.textAlign = 'center';
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 44px sans-serif';
  ctx.fillText('🐾 ofertis.vercel.app', 540, 1800);

  ctx.fillStyle = '#9ca3af';
  ctx.font = '500 28px sans-serif';
  ctx.fillText('Descarga la App y anticípate a los precios', 540, 1850);

  const link = document.createElement('a');
  link.download = `ofertis_story_${art.id || 'noticia'}_9x16.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
};

export const AlzaPreciosBlog: React.FC<AlzaPreciosBlogProps> = ({ onSearchProduct }) => {
  const [articles, setArticles] = useState<SentinelaArticle[]>([]);
  const [stats, setStats] = useState<SentinelaStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDirection, setSelectedDirection] = useState<string>('todas');
  const [selectedCategory, setSelectedCategory] = useState('todas');
  const [selectedSeverity, setSelectedSeverity] = useState('todas');
  const [selectedArticle, setSelectedArticle] = useState<SentinelaArticle | null>(null);
  const [instagramArticle, setInstagramArticle] = useState<SentinelaArticle | null>(null);
  const [copiedCaption, setCopiedCaption] = useState(false);
  const [storyDesignMode, setStoryDesignMode] = useState<'editorial' | 'canvas'>('editorial');
  const [generatingNews, setGeneratingNews] = useState<boolean>(false);
  const [generationMessage, setGenerationMessage] = useState<string | null>(null);

  const handleGenerateNews = async () => {
    if (generatingNews) return;
    setGeneratingNews(true);
    setGenerationMessage('Ejecutando radar Sentinela y redacción con El Cronista...');
    try {
      await axios.post(`${API_BASE_URL}/sentinela/generate`);
      setGenerationMessage('¡Nuevas noticias redactadas y publicadas con éxito!');
      await fetchData();
      setTimeout(() => setGenerationMessage(null), 5000);
    } catch (err) {
      console.error('Error generando noticias bajo demanda:', err);
      setGenerationMessage('Aviso: Se intentó generar noticias pero ocurrió una demora o error.');
      setTimeout(() => setGenerationMessage(null), 5000);
    } finally {
      setGeneratingNews(false);
    }
  };

  // Navegación de Landing Page con sincronización de URL (?article=...)
  const handleSelectArticle = (art: SentinelaArticle | null) => {
    setSelectedArticle(art);
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href);
      if (art) {
        url.searchParams.set('tab', 'alza-precios');
        url.searchParams.set('article', art.id);
      } else {
        url.searchParams.delete('article');
        url.searchParams.delete('post');
      }
      window.history.pushState({ articleId: art?.id || null }, '', url.toString());
    }
  };

  // Mapa determinista de fotografías temáticas no repetidas para cada artículo
  const articleImageMap = React.useMemo(() => buildArticleImageMap(articles), [articles]);

  const getImage = (art: SentinelaArticle | null | undefined): string => {
    if (!art) return THEMATIC_IMAGE_POOLS.frutas_y_verduras[0];
    const themeKey = getArticleThemeKey(art);
    const pool = THEMATIC_IMAGE_POOLS[themeKey] || THEMATIC_IMAGE_POOLS.frutas_y_verduras;
    return (art.id && articleImageMap.get(art.id)) || pool[0];
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const [artRes, statRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/sentinela/articles`),
        axios.get(`${API_BASE_URL}/sentinela/stats`)
      ]);
      setArticles(artRes.data);
      setStats(statRes.data);
    } catch (err) {
      console.error('Error cargando artículos del Sentinela:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Detectar artículo en la URL (?article=...) al cargar la página o navegar con el historial
  useEffect(() => {
    const handleUrlArticleSync = () => {
      if (typeof window === 'undefined' || articles.length === 0) return;
      const params = new URLSearchParams(window.location.search);
      const articleId = params.get('article') || params.get('post');
      if (articleId) {
        const found = articles.find(
          (a) => a.id === articleId || a.id.toLowerCase() === articleId.toLowerCase()
        );
        if (found && (!selectedArticle || selectedArticle.id !== found.id)) {
          setSelectedArticle(found);
        }
      } else if (!articleId && selectedArticle) {
        setSelectedArticle(null);
      }
    };

    handleUrlArticleSync();
    window.addEventListener('popstate', handleUrlArticleSync);
    return () => window.removeEventListener('popstate', handleUrlArticleSync);
  }, [articles, selectedArticle]);

  // Conteos por dirección de tendencia
  const directionCounts = React.useMemo(() => {
    return {
      total: articles.length,
      alza: articles.filter((a) => (a.trend_direction || 'ALZA').toUpperCase() === 'ALZA').length,
      baja: articles.filter((a) => (a.trend_direction || '').toUpperCase() === 'BAJA').length,
      tendencia: articles.filter((a) => (a.trend_direction || '').toUpperCase() === 'TENDENCIA').length,
    };
  }, [articles]);

  // Extraer categorías únicas para los filtros
  const categories = React.useMemo(() => {
    const cats = new Map<string, string>();
    articles.forEach((a) => {
      if (a.category && a.category_label) {
        cats.set(a.category, a.category_label);
      }
    });
    return Array.from(cats.entries());
  }, [articles]);

  // Filtrado de artículos
  const filteredArticles = React.useMemo(() => {
    return articles.filter((art) => {
      const matchesSearch =
        !searchQuery.trim() ||
        (art.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (art.headline || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (art.transmission_mechanism || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (art.affected_products || []).some((p) => (p || '').toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesDir =
        selectedDirection === 'todas' ||
        (art.trend_direction || 'ALZA').toUpperCase() === selectedDirection.toUpperCase();

      const matchesCat =
        selectedCategory === 'todas' || art.category === selectedCategory;

      const matchesSev =
        selectedSeverity === 'todas' || art.severity.toUpperCase() === selectedSeverity.toUpperCase();

      return matchesSearch && matchesDir && matchesCat && matchesSev;
    });
  }, [articles, searchQuery, selectedDirection, selectedCategory, selectedSeverity]);

  // Artículo destacado: el primero de severidad ALTA, o el más reciente
  const featuredArticle = filteredArticles.find((a) => a.severity === 'ALTA') || filteredArticles[0];
  const featuredMeta = featuredArticle ? getDirectionMeta(featuredArticle.trend_direction) : null;
  const featuredHikeWindow = featuredArticle
    ? getPriceHikeWindow(featuredArticle.date, featuredArticle.lag_days_min, featuredArticle.lag_days_max)
    : null;
  const gridArticles = filteredArticles.filter((a) => a !== featuredArticle);

  // Renderizador del Modal de Instagram Stories (compartido entre blog y landing page)
  const renderInstagramModal = () => {
    if (!instagramArticle) return null;

    const exportArticle = instagramArticle;
    const exportThemeKey = getArticleThemeKey(exportArticle);
    const pool = THEMATIC_IMAGE_POOLS[exportThemeKey] || THEMATIC_IMAGE_POOLS.frutas_y_verduras;
    const exportImage = storyDesignMode === 'editorial'
      ? getEditorialStoryImage(exportArticle)
      : ((exportArticle.id && articleImageMap.get(exportArticle.id)) || pool[0]);
    const exportWindow = getPriceHikeWindow(exportArticle.date, exportArticle.lag_days_min, exportArticle.lag_days_max);

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-xs animate-fade-in overflow-y-auto">
        <div className="bg-white dark:bg-stone-900 rounded-3xl max-w-4xl w-full border border-stone-200 dark:border-stone-800 shadow-2xl overflow-hidden my-auto flex flex-col max-h-[95vh]">
          {/* Cabecera del Modal */}
          <div className="px-6 py-4 border-b border-stone-100 dark:border-stone-800 flex items-center justify-between bg-stone-50/70 dark:bg-stone-850/70 shrink-0">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-pink-500 via-rose-500 to-amber-500 flex items-center justify-center text-white shadow-md shadow-pink-500/25">
                <Instagram className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-black text-stone-900 dark:text-white flex items-center space-x-2">
                  <span>Generador de Publicaciones Instagram</span>
                  <span className="text-[11px] font-extrabold px-2 py-0.5 rounded-full bg-pink-100 dark:bg-pink-950/80 text-pink-700 dark:text-pink-300 border border-pink-200 dark:border-pink-800">
                    Formato 9:16 (Story / Reel)
                  </span>
                </h3>
                <p className="text-xs text-stone-500 dark:text-stone-400">
                  Diseños verticales optimizados listos para descargar y compartir.
                </p>
              </div>
            </div>

            <button
              onClick={() => setInstagramArticle(null)}
              className="p-2 rounded-full hover:bg-stone-200 dark:hover:bg-stone-800 text-stone-500 transition-colors cursor-pointer"
              aria-label="Cerrar modal"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Contenido en 2 columnas: Vista previa 9:16 + Opciones de Exportación */}
          <div className="p-6 overflow-y-auto grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            {/* Columna Izquierda: Mockup Smartphone 9:16 */}
            <div className="lg:col-span-6 flex flex-col items-center justify-center">
              {/* Selector de plantilla */}
              <div className="flex items-center space-x-2 mb-3 bg-stone-100 dark:bg-stone-800 p-1 rounded-2xl w-full max-w-[300px]">
                <button
                  onClick={() => setStoryDesignMode('editorial')}
                  className={`flex-1 py-1.5 px-3 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    storyDesignMode === 'editorial'
                      ? 'bg-white dark:bg-stone-700 text-stone-900 dark:text-white shadow-xs font-black'
                      : 'text-stone-500 hover:text-stone-900 dark:hover:text-white'
                  }`}
                >
                  🎨 Arte 3D Editorial
                </button>
                <button
                  onClick={() => setStoryDesignMode('canvas')}
                  className={`flex-1 py-1.5 px-3 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    storyDesignMode === 'canvas'
                      ? 'bg-white dark:bg-stone-700 text-stone-900 dark:text-white shadow-xs font-black'
                      : 'text-stone-500 hover:text-stone-900 dark:hover:text-white'
                  }`}
                >
                  ⚡ Directo HD
                </button>
              </div>

              {/* Marco del celular */}
              <div className="relative w-[280px] sm:w-[310px] aspect-9/16 rounded-[40px] p-3 bg-stone-950 shadow-2xl shadow-black/60 border-4 border-stone-800 shrink-0">
                {/* Bocina y cámara frontal simulada */}
                <div className="absolute top-4 left-1/2 -translate-x-1/2 w-24 h-4 bg-stone-900 rounded-full z-20 flex items-center justify-center">
                  <div className="w-2.5 h-2.5 rounded-full bg-stone-800 mr-2" />
                  <div className="w-8 h-1 rounded-full bg-stone-800" />
                </div>

                {/* Pantalla del celular con el diseño 9:16 */}
                <div className="relative w-full h-full rounded-[30px] overflow-hidden flex flex-col justify-between p-4 bg-stone-950 text-white select-none">
                  {/* Imagen de fondo con overlay */}
                  <img
                    src={exportImage}
                    alt={exportArticle.title}
                    className="absolute inset-0 w-full h-full object-cover opacity-35"
                  />
                  <div className="absolute inset-0 bg-gradient-to-b from-stone-950/80 via-stone-950/50 to-stone-950/95 pointer-events-none" />

                  {/* Header Story */}
                  <div className="relative z-10 pt-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="inline-flex items-center space-x-1.5 bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-[10px] font-black px-2.5 py-1 rounded-full backdrop-blur-xs">
                        <ShieldAlert className="w-3 h-3 text-emerald-400 animate-pulse" />
                        <span>EL SENTINELA • OFERTIS</span>
                      </div>
                      <span className="text-[9px] text-stone-400 font-bold">
                        {exportArticle.bulletin_id}
                      </span>
                    </div>

                    <div className="inline-block">
                      <span className={`text-[10px] font-black px-2.5 py-0.5 rounded-md uppercase tracking-wider ${
                        exportArticle.trend_direction === 'BAJA'
                          ? 'bg-emerald-500 text-white'
                          : 'bg-red-500 text-white'
                      }`}>
                        {exportArticle.trend_direction === 'BAJA' ? '📉 Oportunidad de Baja' : '📈 Alerta de Alza'}
                      </span>
                    </div>
                  </div>

                  {/* Centro Story: Titular y Explicación */}
                  <div className="relative z-10 space-y-3 my-auto py-2">
                    <h4 className="text-base sm:text-lg font-black leading-tight text-white line-clamp-4 drop-shadow-md">
                      {exportArticle.title}
                    </h4>

                    {/* Ventana de días */}
                    <div className="bg-emerald-950/70 border border-emerald-500/50 rounded-2xl p-2.5 text-center backdrop-blur-xs">
                      <div className="text-[9px] font-extrabold text-emerald-300 uppercase tracking-wider">
                        Ventana en Góndolas:
                      </div>
                      <div className="text-sm font-black text-white">
                        Del {exportWindow?.rangeText || `${exportArticle.lag_days_min} a ${exportArticle.lag_days_max} días`}
                      </div>
                    </div>

                    {/* Productos afectados */}
                    <div className="flex flex-wrap gap-1 justify-center">
                      {(exportArticle.affected_products || []).slice(0, 3).map((p) => (
                        <span
                          key={p}
                          className="bg-white/15 backdrop-blur-xs text-white text-[10px] font-bold px-2 py-0.5 rounded-md"
                        >
                          {p}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Footer Story: Call To Action */}
                  <div className="relative z-10 pb-2 space-y-2 border-t border-white/10 pt-2 text-center">
                    <div className="text-[10px] font-extrabold text-emerald-300">
                      {(exportArticle.consumer_advice || '').replace('💡 Consejo Sentinela: ', '').slice(0, 75)}...
                    </div>
                    <div className="bg-white text-stone-900 text-[10px] font-black py-1.5 px-3 rounded-xl shadow-md">
                      📲 Revisa el comparador en Ofertis
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Columna Derecha: Opciones y Botones de Descarga */}
            <div className="lg:col-span-6 space-y-5">
              <div className="space-y-2">
                <h4 className="text-sm font-black text-stone-900 dark:text-white flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-emerald-600" />
                  <span>Publicación Lista para Redes Sociales</span>
                </h4>
                <p className="text-xs text-stone-600 dark:text-stone-300 leading-relaxed">
                  Exporta esta gráfica en formato <strong>9:16 de alta resolución (1080x1920px)</strong> para publicarla en tus Historias de Instagram, Reels, estados de WhatsApp o TikTok.
                </p>
              </div>

              {/* Botones de Descarga */}
              <div className="space-y-3 pt-2">
                <button
                  onClick={() => downloadCanvasStory(exportArticle)}
                  className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-pink-600 via-rose-500 to-amber-500 hover:from-pink-700 hover:to-amber-600 text-white font-black py-3.5 px-6 rounded-2xl shadow-lg shadow-pink-500/25 text-sm transition-all cursor-pointer hover:scale-[1.01]"
                >
                  <Download className="w-4 h-4" />
                  <span>Descargar Imagen 9:16 (1080x1920 HD)</span>
                </button>

                <button
                  onClick={() => {
                    const caption = generateInstagramCaption(exportArticle);
                    navigator.clipboard.writeText(caption);
                    setCopiedCaption(true);
                    setTimeout(() => setCopiedCaption(false), 2500);
                  }}
                  className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-2xl text-xs font-bold transition-all border cursor-pointer ${
                    copiedCaption
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-300 dark:bg-emerald-950/60 dark:text-emerald-200'
                      : 'bg-stone-50 dark:bg-stone-850 hover:bg-stone-100 dark:hover:bg-stone-800 text-stone-700 dark:text-stone-300 border-stone-200 dark:border-stone-700'
                  }`}
                >
                  {copiedCaption ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                  <span>{copiedCaption ? '¡Texto del Post Copiado al Portapapeles!' : 'Copiar Texto / Pie de Foto para el Post'}</span>
                </button>
              </div>

              {/* Selector de otra alerta para exportar */}
              {articles.length > 1 && (
                <div className="pt-4 border-t border-stone-100 dark:border-stone-800 space-y-2">
                  <span className="text-xs font-extrabold text-stone-500 dark:text-stone-400 block">
                    Exportar otra alerta:
                  </span>
                  <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto p-1">
                    {articles.slice(0, 8).map((art, idx) => (
                      <button
                        key={art.id}
                        onClick={() => setInstagramArticle(art)}
                        className={`w-7 h-7 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                          instagramArticle.id === art.id
                            ? 'bg-pink-600 text-white font-black scale-110 shadow-xs'
                            : 'bg-stone-100 hover:bg-stone-200 dark:bg-stone-800 text-stone-600 dark:text-stone-400'
                        }`}
                      >
                        {idx + 1}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Si hay un artículo seleccionado (por clic o por parámetro URL ?article=...),
  // renderizamos la LANDING PAGE completa y dedicada
  if (selectedArticle) {
    return (
      <div className="space-y-8 animate-fade-in pb-12">
        <ArticleLandingPage
          article={selectedArticle}
          articles={articles}
          getImage={getImage}
          onBack={() => handleSelectArticle(null)}
          onSelectArticle={(art) => handleSelectArticle(art)}
          onOpenInstagramStory={(art) => setInstagramArticle(art)}
          onSearchProduct={onSearchProduct}
        />
        {renderInstagramModal()}
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Encabezado Principal del Blog */}
      <div className="relative rounded-3xl p-6 sm:p-10 bg-white dark:bg-stone-900 text-stone-900 dark:text-stone-100 shadow-xl overflow-hidden border-2 border-emerald-500/30">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 bg-emerald-100/50 dark:bg-emerald-900/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/4 -mb-10 w-72 h-72 bg-teal-100/40 dark:bg-teal-900/10 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 max-w-4xl space-y-4">
          <div className="inline-flex items-center space-x-2 bg-emerald-50 dark:bg-emerald-950/80 border border-emerald-300 dark:border-emerald-700 text-emerald-800 dark:text-emerald-300 px-4 py-1.5 rounded-full text-xs font-black tracking-wider shadow-xs">
            <ShieldAlert className="w-4 h-4 text-emerald-600 dark:text-emerald-400 animate-pulse" />
            <span>EL SENTINELA • RADAR PREVENTIVO DE ALZAS</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-emerald-950 dark:text-emerald-100 leading-tight">
            Alza de Precios: Informes del Sentinela
          </h1>

          <p className="text-stone-700 dark:text-stone-200 text-sm sm:text-base leading-relaxed max-w-3xl font-medium">
            Monitoreo preventivo y auditoría ciudadana de la canasta básica chilena.
            Publicamos automáticamente los informes analíticos del agente <strong className="text-emerald-800 dark:text-emerald-300 font-extrabold">Sentinela</strong>, con fecha y hora exacta de emisión y el <strong className="text-emerald-800 dark:text-emerald-300 font-extrabold">rango proyectado de fechas en que subirá el precio</strong> en góndolas.
          </p>

          <div className="bg-emerald-50/90 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/80 rounded-2xl p-4 text-xs text-stone-800 dark:text-emerald-100 flex items-start space-x-3 shadow-xs">
            <Info className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-black text-emerald-800 dark:text-emerald-300 block mb-0.5">
                Criterio Antiespeculación ("Cero Humo"):
              </span>
              Cada artículo se sustenta exclusivamente en hechos noticiosos y mediciones oficiales verificables
              (ODEPA del Ministerio de Agricultura, Banco Central de Chile, Dirección Meteorológica y FAO).
              Calculamos la ventana de alza en función del tiempo de reposición de inventario de las cadenas.
            </div>
          </div>

          {/* Barra de Acciones Globales */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={handleGenerateNews}
              disabled={generatingNews}
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-700 hover:from-emerald-700 hover:to-cyan-800 text-white text-xs font-black px-4 py-2.5 rounded-xl shadow-md shadow-emerald-600/25 transition-all cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
              title="Dispara el escaneo en vivo de Sentinela y la redacción de nuevos artículos con El Cronista"
            >
              <Sparkles className={`w-4 h-4 ${generatingNews ? 'animate-spin text-amber-300' : ''}`} />
              <span>{generatingNews ? 'Generando Noticias...' : '⚡ Generar Noticias'}</span>
            </button>
            <button
              onClick={() => setInstagramArticle(featuredArticle || articles[0])}
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-pink-600 via-rose-500 to-amber-500 hover:from-pink-700 hover:to-amber-600 text-white text-xs font-black px-4 py-2.5 rounded-xl shadow-md shadow-pink-500/25 transition-all cursor-pointer"
            >
              <Instagram className="w-4 h-4" />
              <span>Crear Publicación Instagram (9:16)</span>
            </button>
            <button
              onClick={fetchData}
              className="inline-flex items-center space-x-1.5 bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-950/60 dark:hover:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700 text-xs font-bold px-3 py-2 rounded-xl transition-all cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Actualizar Alertas</span>
            </button>
          </div>

          {/* Banner de Estado de Generación Bajo Demanda */}
          {generationMessage && (
            <div className="mt-3 p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/70 border border-emerald-300 dark:border-emerald-700 text-emerald-900 dark:text-emerald-200 text-xs flex items-center space-x-2 animate-fadeIn">
              <Sparkles className={`w-4 h-4 text-emerald-600 dark:text-emerald-400 ${generatingNews ? 'animate-spin' : ''}`} />
              <span className="font-semibold">{generationMessage}</span>
            </div>
          )}
        </div>
      </div>

      {/* Métricas y KPIs de Vigilancia */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
          <div className="bg-white dark:bg-stone-900 p-4 sm:p-5 rounded-2xl border border-emerald-100 dark:border-emerald-900/60 shadow-sm hover:border-emerald-300 transition-colors">
            <div className="flex items-center justify-between text-stone-600 dark:text-stone-400 text-xs font-bold mb-1">
              <span>Artículos Publicados</span>
              <FileText className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-2xl sm:text-3xl font-black text-emerald-700 dark:text-emerald-400">
              {stats.total_articles}
            </div>
            <div className="text-[11px] text-stone-500 dark:text-stone-400 mt-1 font-medium">Generados por el Sentinela</div>
          </div>

          <div className="bg-white dark:bg-stone-900 p-4 sm:p-5 rounded-2xl border border-emerald-100 dark:border-emerald-900/60 shadow-sm hover:border-emerald-300 transition-colors">
            <div className="flex items-center justify-between text-stone-600 dark:text-stone-400 text-xs font-bold mb-1">
              <span>Alertas Críticas</span>
              <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
            </div>
            <div className="text-2xl sm:text-3xl font-black text-red-600 dark:text-red-400">
              {stats.high_severity_count}
            </div>
            <div className="text-[11px] text-red-700 dark:text-red-300 mt-1 font-bold">Traspaso inminente (&lt; 15 días)</div>
          </div>

          <div className="bg-white dark:bg-stone-900 p-4 sm:p-5 rounded-2xl border border-emerald-100 dark:border-emerald-900/60 shadow-sm hover:border-emerald-300 transition-colors">
            <div className="flex items-center justify-between text-stone-600 dark:text-stone-400 text-xs font-bold mb-1">
              <span>Boletines Auditoría</span>
              <BookOpen className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-2xl sm:text-3xl font-black text-emerald-700 dark:text-emerald-400">
              {stats.total_bulletins}
            </div>
            <div className="text-[11px] text-stone-500 dark:text-stone-400 mt-1 font-medium">Monitoreo continuo 24/7</div>
          </div>

          <div className="bg-white dark:bg-stone-900 p-4 sm:p-5 rounded-2xl border border-emerald-100 dark:border-emerald-900/60 shadow-sm hover:border-emerald-300 transition-colors">
            <div className="flex items-center justify-between text-stone-600 dark:text-stone-400 text-xs font-bold mb-1">
              <span>Fuentes de Estado</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-2xl sm:text-3xl font-black text-emerald-600 dark:text-emerald-400">
              100%
            </div>
            <div className="text-[11px] text-stone-500 dark:text-stone-400 mt-1 font-medium">ODEPA, Banco Central, DMC</div>
          </div>
        </div>
      )}

      {/* Barra de Filtros y Búsqueda */}
      <div className="bg-white dark:bg-stone-900 p-4 sm:p-5 rounded-2xl border border-emerald-100 dark:border-emerald-900/60 shadow-sm space-y-4">
        {/* Pestañas Principales por Dirección de Tendencia */}
        <div className="flex flex-wrap items-center gap-2 pb-2 border-b border-stone-100 dark:border-stone-800">
          <button
            onClick={() => setSelectedDirection('todas')}
            className={`px-3.5 py-2 rounded-xl text-xs font-black transition-all flex items-center space-x-1.5 cursor-pointer ${
              selectedDirection === 'todas'
                ? 'bg-stone-900 dark:bg-stone-100 text-white dark:text-stone-900 shadow-sm'
                : 'bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 hover:bg-stone-200 dark:hover:bg-stone-750'
            }`}
          >
            <span>Todos los Informes</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-stone-700 dark:bg-stone-300 text-white dark:text-stone-900 font-bold">
              {directionCounts.total}
            </span>
          </button>

          <button
            onClick={() => setSelectedDirection('ALZA')}
            className={`px-3.5 py-2 rounded-xl text-xs font-black transition-all flex items-center space-x-1.5 cursor-pointer ${
              selectedDirection === 'ALZA'
                ? 'bg-red-600 text-white shadow-sm shadow-red-600/30'
                : 'bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-400 border border-red-200/80 dark:border-red-800/40 hover:bg-red-100'
            }`}
          >
            <TrendingUp className="w-3.5 h-3.5" />
            <span>🔴 Alzas Proyectadas</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-red-200 dark:bg-red-900 text-red-900 dark:text-red-100 font-bold">
              {directionCounts.alza}
            </span>
          </button>

          <button
            onClick={() => setSelectedDirection('BAJA')}
            className={`px-3.5 py-2 rounded-xl text-xs font-black transition-all flex items-center space-x-1.5 cursor-pointer ${
              selectedDirection === 'BAJA'
                ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-600/30'
                : 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200/80 dark:border-emerald-800/40 hover:bg-emerald-100'
            }`}
          >
            <TrendingDown className="w-3.5 h-3.5" />
            <span>🟢 Bajas y Oportunidades</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-200 dark:bg-emerald-900 text-emerald-900 dark:text-emerald-100 font-bold">
              {directionCounts.baja}
            </span>
          </button>

          <button
            onClick={() => setSelectedDirection('TENDENCIA')}
            className={`px-3.5 py-2 rounded-xl text-xs font-black transition-all flex items-center space-x-1.5 cursor-pointer ${
              selectedDirection === 'TENDENCIA'
                ? 'bg-sky-600 text-white shadow-sm shadow-sky-600/30'
                : 'bg-sky-50 dark:bg-sky-950/40 text-sky-700 dark:text-sky-300 border border-sky-200/80 dark:border-sky-800/40 hover:bg-sky-100'
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>🔵 Temas de Interés y Guías</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-sky-200 dark:bg-sky-900 text-sky-900 dark:text-sky-100 font-bold">
              {directionCounts.tendencia}
            </span>
          </button>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-emerald-600 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Buscar alertas por producto (ej: 'pollo', 'tomate', 'palta', 'harina', 'maíz')..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-stone-50 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 text-sm text-stone-900 dark:text-stone-100 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all font-medium"
            />
          </div>

          <button
            onClick={fetchData}
            disabled={loading}
            className="flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-950/60 dark:hover:bg-emerald-900/60 text-emerald-800 dark:text-emerald-200 border border-emerald-200 dark:border-emerald-800 font-bold text-xs transition-all shrink-0 cursor-pointer shadow-2xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Actualizar Informes</span>
          </button>
        </div>

        {/* Filtros de Severidad y Categorías */}
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-stone-100 dark:border-stone-800 text-xs">
          <span className="text-stone-500 font-bold mr-1 flex items-center space-x-1">
            <Filter className="w-3 h-3 text-emerald-600" />
            <span>Filtros:</span>
          </span>

          <button
            onClick={() => setSelectedSeverity('todas')}
            className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
              selectedSeverity === 'todas'
                ? 'bg-emerald-700 text-white shadow-xs'
                : 'bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 hover:bg-emerald-50 hover:text-emerald-800'
            }`}
          >
            Todas las Severidades
          </button>

          <button
            onClick={() => setSelectedSeverity('ALTA')}
            className={`px-3 py-1 rounded-lg font-bold flex items-center space-x-1 transition-all cursor-pointer ${
              selectedSeverity === 'ALTA'
                ? 'bg-red-600 text-white shadow-xs'
                : 'bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-400 border border-red-200/80 dark:border-red-800/40 hover:bg-red-100'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-red-500" />
            <span>Alerta Alta</span>
          </button>

          <button
            onClick={() => setSelectedSeverity('MEDIA')}
            className={`px-3 py-1 rounded-lg font-bold flex items-center space-x-1 transition-all cursor-pointer ${
              selectedSeverity === 'MEDIA'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border border-emerald-200/80 dark:border-emerald-800/40 hover:bg-emerald-100'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>Alerta Moderada</span>
          </button>

          {categories.map(([slug, label]) => (
            <button
              key={slug}
              onClick={() => setSelectedCategory(selectedCategory === slug ? 'todas' : slug)}
              className={`px-3 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                selectedCategory === slug
                  ? 'bg-emerald-600 text-white shadow-xs'
                  : 'bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 hover:bg-emerald-50 hover:text-emerald-800 dark:hover:bg-stone-750'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Estado de Carga */}
      {loading && articles.length === 0 && (
        <div className="bg-white dark:bg-stone-900 rounded-3xl p-12 text-center border border-emerald-100 dark:border-emerald-900 shadow-sm">
          <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin mx-auto mb-3" />
          <h3 className="text-base font-bold text-stone-800 dark:text-stone-200">
            Compilando boletines del Sentinela...
          </h3>
          <p className="text-xs text-stone-500 mt-1">
            Analizando causas de transmisión económica y fuentes oficiales chilenas.
          </p>
        </div>
      )}

      {/* Sin Resultados */}
      {!loading && filteredArticles.length === 0 && (
        <div className="bg-white dark:bg-stone-900 rounded-3xl p-12 text-center border border-emerald-100 dark:border-emerald-900 shadow-sm">
          <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto mb-3" />
          <h3 className="text-base font-bold text-stone-800 dark:text-stone-200">
            No se encontraron alertas para los filtros seleccionados
          </h3>
          <p className="text-xs text-stone-500 mt-1 mb-4">
            Prueba ajustando el término de búsqueda o seleccionando otra severidad.
          </p>
          <button
            onClick={() => {
              setSearchQuery('');
              setSelectedCategory('todas');
              setSelectedSeverity('todas');
            }}
            className="px-4 py-2 rounded-xl bg-emerald-600 text-white font-bold text-xs shadow-md shadow-emerald-600/20"
          >
            Limpiar Filtros
          </button>
        </div>
      )}

      {/* Artículo Destacado (Hero Article): Con Fecha, Hora y Rango de Fechas de Alza */}
      {!loading && featuredArticle && (
        <article className="relative rounded-3xl bg-white dark:bg-stone-900 border-2 border-emerald-500/60 shadow-xl overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-12 items-stretch">
            {/* Fotografía alusiva al tema */}
            <div className="lg:col-span-5 relative min-h-[280px] sm:min-h-[360px] overflow-hidden bg-stone-100">
              <img
                src={getImage(featuredArticle)}
                alt={featuredArticle.title}
                className="w-full h-full object-cover object-center"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/25 to-transparent lg:bg-gradient-to-r lg:from-transparent lg:to-black/40 pointer-events-none" />

              {/* Badges sobre la fotografía */}
              <div className="absolute top-4 left-4 flex flex-wrap gap-2 z-10">
                <span className={`inline-flex items-center space-x-1.5 ${featuredMeta?.heroTagBg || 'bg-red-600'} text-white text-[11px] font-black px-3 py-1 rounded-full uppercase tracking-wider shadow-lg backdrop-blur-xs`}>
                  <span className="w-2 h-2 rounded-full bg-white animate-ping" />
                  <span>{featuredMeta?.heroTag || 'ALERTA DESTACADA'}</span>
                </span>
                <span className="text-[11px] font-black bg-white/95 text-stone-900 px-3 py-1 rounded-full shadow-md backdrop-blur-xs">
                  {featuredArticle.category_label}
                </span>
              </div>

              {/* Rango de fechas sobre la foto */}
              <div className="absolute bottom-4 left-4 right-4 z-10">
                <div className="bg-stone-950/90 text-white backdrop-blur-md p-3 rounded-2xl shadow-xl border border-white/20 space-y-1">
                  <div className="flex items-center space-x-1.5 text-emerald-400 text-[11px] font-black uppercase tracking-wider">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{featuredMeta?.datesTitle || 'Rango estimado:'}</span>
                  </div>
                  <div className="text-xs sm:text-sm font-black text-white">
                    {featuredHikeWindow?.rangeText}
                  </div>
                  <div className="text-[10px] text-stone-300 flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-emerald-400" />
                    <span>Ventana de impacto: {featuredArticle.lag_days_min} a {featuredArticle.lag_days_max} días</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Contenido Editorial del Artículo */}
            <div className="lg:col-span-7 p-6 sm:p-8 flex flex-col justify-between space-y-4">
              <div className="space-y-3.5">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`text-[11px] font-black px-3 py-0.5 rounded-full ${
                    featuredArticle.severity === 'ALTA'
                      ? 'bg-red-100 text-red-800 border border-red-200'
                      : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                  }`}>
                    Severidad {featuredArticle.severity}
                  </span>

                  <span className={`text-[11px] font-black px-3 py-0.5 rounded-full border ${featuredMeta?.badgeBg} ${featuredMeta?.badgeText} ${featuredMeta?.badgeBorder}`}>
                    {featuredMeta?.badgeLabel}
                  </span>

                  <span className="text-[11px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 px-2.5 py-0.5 rounded-full">
                    Certeza Causal: {Math.round(featuredArticle.confidence_score * 100)}%
                  </span>
                </div>

                {/* Título y Titular Noticioso */}
                <div>
                  <h2 className="text-2xl sm:text-3xl font-black text-stone-900 dark:text-stone-50 leading-snug tracking-tight">
                    {featuredArticle.title}
                  </h2>

                  {/* Fecha y Hora Exacta de Publicación */}
                  <div className="mt-2.5 text-xs text-stone-600 dark:text-stone-300 flex flex-wrap items-center gap-x-3 gap-y-1 font-medium bg-stone-50 dark:bg-stone-800/60 px-3.5 py-2 rounded-xl border border-stone-200/80 dark:border-stone-700/80">
                    <div className="flex items-center space-x-1.5">
                      <Clock className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                      <span>Publicado el: <strong className="text-stone-900 dark:text-stone-100">{formatPublicationDateTime(featuredArticle.date)}</strong></span>
                    </div>
                    <span>•</span>
                    <span className="text-stone-500">Boletín {featuredArticle.bulletin_id}</span>
                  </div>
                </div>

                {/* Rango de Fechas (Callout Destacado) */}
                <div className="bg-emerald-50/90 dark:bg-emerald-950/40 rounded-2xl p-4 border-2 border-emerald-300 dark:border-emerald-800 space-y-1 shadow-2xs">
                  <div className="flex items-center space-x-2 text-xs font-black text-emerald-900 dark:text-emerald-300 uppercase tracking-wider">
                    <Calendar className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                    <span>{featuredMeta?.datesTitle || 'Rango de fechas proyectado:'}</span>
                  </div>
                  <div className="text-base sm:text-lg font-black text-emerald-950 dark:text-white flex flex-wrap items-center gap-2">
                    <span>Del {featuredHikeWindow?.rangeText}</span>
                    <span className="text-xs font-bold bg-emerald-200/70 dark:bg-emerald-900/80 text-emerald-900 dark:text-emerald-200 px-2.5 py-0.5 rounded-md">
                      En {featuredArticle.lag_days_min} a {featuredArticle.lag_days_max} días
                    </span>
                  </div>
                  <p className="text-xs text-emerald-800/90 dark:text-emerald-200/90 font-medium">
                    Ventana calculada según la rotación de existencias y abastecimiento mayorista en Chile.
                  </p>
                </div>

                {/* Productos involucrados */}
                <div>
                  <span className="text-[11px] uppercase tracking-wider font-extrabold text-stone-500 dark:text-stone-400 block mb-1.5">
                    {featuredMeta?.productsTitle || 'Góndolas con riesgo inminente de alza:'}
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {(featuredArticle.affected_products || []).map((prod) => (
                      <span
                        key={prod}
                        className="bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200 text-xs font-bold px-2.5 py-1 rounded-lg"
                      >
                        {prod}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Cadena de Transmisión Causal */}
                <div className="bg-stone-50 dark:bg-stone-800/80 rounded-2xl p-4 border border-stone-200 dark:border-stone-700 space-y-1.5">
                  <div className="flex items-center space-x-2 text-xs font-extrabold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
                    {featuredMeta?.type === 'BAJA' ? (
                      <TrendingDown className="w-4 h-4 text-emerald-600" />
                    ) : featuredMeta?.type === 'TENDENCIA' ? (
                      <Compass className="w-4 h-4 text-sky-600" />
                    ) : (
                      <TrendingUp className="w-4 h-4 text-red-600" />
                    )}
                    <span>{featuredMeta?.mechanismTitle || 'Cadena de Transmisión Económica:'}</span>
                  </div>
                  <p className="text-xs sm:text-sm text-stone-800 dark:text-stone-200 leading-relaxed font-normal">
                    {featuredArticle.transmission_mechanism}
                  </p>
                </div>

                {/* Consejo Sentinela */}
                <div className="bg-emerald-50/90 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800/80 rounded-2xl p-4 text-emerald-950 dark:text-emerald-100 text-xs sm:text-sm leading-relaxed flex items-start space-x-3">
                  <Sparkles className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-black text-emerald-800 dark:text-emerald-300 block mb-0.5">
                      {featuredMeta?.adviceTitle || 'Consejo Estratégico Sentinela:'}
                    </span>
                    {(featuredArticle.consumer_advice || '').replace('💡 Consejo Sentinela: ', '')}
                  </div>
                </div>
              </div>

              {/* Botones de acción */}
              <div className="pt-3 border-t border-stone-100 dark:border-stone-800 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <button
                  onClick={() => handleSelectArticle(featuredArticle)}
                  className="flex-1 flex items-center justify-center space-x-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-black py-2.5 px-4 rounded-xl text-xs transition-all shadow-md shadow-emerald-600/25 cursor-pointer"
                >
                  <span>Leer Informe Completo</span>
                  <ChevronRight className="w-4 h-4" />
                </button>

                <button
                  onClick={() => setInstagramArticle(featuredArticle)}
                  className="flex items-center justify-center space-x-1.5 bg-gradient-to-r from-pink-600 via-rose-500 to-amber-500 hover:from-pink-700 hover:to-amber-600 text-white font-black py-2.5 px-4 rounded-xl text-xs transition-all shadow-md shadow-pink-500/25 cursor-pointer"
                >
                  <Instagram className="w-4 h-4" />
                  <span>Story (9:16)</span>
                </button>

                {featuredArticle.source_url && (
                  <a
                    href={featuredArticle.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center space-x-1.5 bg-stone-100 hover:bg-stone-200 dark:bg-stone-800 dark:hover:bg-stone-750 text-stone-800 dark:text-stone-200 border border-stone-200 dark:border-stone-700 font-bold py-2.5 px-4 rounded-xl text-xs transition-all"
                  >
                    <span>Auditar Fuente Oficial</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            </div>
          </div>
        </article>
      )}

      {/* Grilla de Artículos Secundarios: Con Fecha, Hora y Rango de Fechas */}
      {!loading && gridArticles.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-black text-stone-900 dark:text-stone-100 tracking-tight flex items-center space-x-2">
              <span>Informes y Oportunidades Monitoreadas</span>
              <span className="text-xs font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
                {gridArticles.length}
              </span>
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {gridArticles.map((art) => {
              const isHigh = art.severity === 'ALTA';
              const articleImage = getImage(art);
              const artHikeWindow = getPriceHikeWindow(art.date, art.lag_days_min, art.lag_days_max);
              const artMeta = getDirectionMeta(art.trend_direction);

              return (
                <article
                  key={art.id}
                  className="bg-white dark:bg-stone-900 rounded-3xl border border-stone-200 dark:border-stone-800 shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between group hover:border-emerald-400 dark:hover:border-emerald-500 overflow-hidden"
                >
                  {/* Fotografía temática con etiquetas superpuestas */}
                  <div className="relative h-48 w-full overflow-hidden bg-stone-100">
                    <img
                      src={articleImage}
                      alt={art.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-transparent to-transparent pointer-events-none" />

                    {/* Badge de Categoría y Dirección */}
                    <div className="absolute top-3 left-3 right-3 flex items-center justify-between gap-1">
                      <span className="bg-stone-900/90 text-white text-[10px] font-black uppercase tracking-wider px-2.5 py-1 rounded-full shadow-md backdrop-blur-xs">
                        {art.category_label}
                      </span>

                      <span
                        className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-full font-black text-[10px] shadow-md ${
                          artMeta.type === 'BAJA'
                            ? 'bg-emerald-600 text-white'
                            : artMeta.type === 'TENDENCIA'
                            ? 'bg-sky-600 text-white'
                            : (isHigh ? 'bg-red-600 text-white' : 'bg-amber-600 text-white')
                        }`}
                      >
                        <span>{artMeta.badgeLabel}</span>
                      </span>
                    </div>

                    {/* Rango de Fechas en la base de la foto */}
                    <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between">
                      <span className="bg-white/95 dark:bg-stone-900/95 text-stone-900 dark:text-stone-100 text-[10px] font-black px-2.5 py-1 rounded-lg shadow-sm flex items-center space-x-1 border border-stone-200 dark:border-stone-700">
                        <Calendar className="w-3 h-3 text-emerald-600" />
                        <span>{artMeta.datesPrefix} <strong>{artHikeWindow.shortRangeText}</strong></span>
                      </span>

                      <span className="bg-stone-950/80 text-stone-200 text-[10px] font-bold px-2 py-0.5 rounded-md backdrop-blur-xs">
                        {art.lag_days_min} a {art.lag_days_max} días
                      </span>
                    </div>
                  </div>

                  {/* Cuerpo de la Tarjeta */}
                  <div className="p-5 flex-1 flex flex-col justify-between space-y-3">
                    <div className="space-y-2.5">
                      {/* Fecha y Hora de Publicación */}
                      <div className="text-[11px] text-stone-500 dark:text-stone-400 font-semibold flex items-center space-x-1.5">
                        <Clock className="w-3 h-3 text-emerald-600" />
                        <span>Publicado: {formatPublicationShort(art.date)}</span>
                      </div>

                      <h3 className="text-base font-black text-stone-900 dark:text-stone-100 group-hover:text-emerald-700 dark:group-hover:text-emerald-400 transition-colors line-clamp-2 leading-snug">
                        {art.title}
                      </h3>

                      {/* Rango Detallado */}
                      <div className="bg-stone-50 dark:bg-stone-800/60 p-2.5 rounded-xl border border-stone-200 dark:border-stone-700 text-xs space-y-0.5">
                        <div className="text-[10px] uppercase font-black text-stone-600 dark:text-stone-300 flex items-center space-x-1">
                          <Calendar className="w-3 h-3 text-emerald-600" />
                          <span>{artMeta.datesTitle}</span>
                        </div>
                        <div className="font-extrabold text-stone-950 dark:text-stone-100 text-xs">
                          Del {artHikeWindow.rangeText}
                        </div>
                        <div className="text-[10px] text-stone-500 dark:text-stone-400 font-medium">
                          Ventana de impacto: {art.lag_days_min} a {art.lag_days_max} días
                        </div>
                      </div>

                      {/* Fuente Oficial Verificada */}
                      <div className="bg-stone-50 dark:bg-stone-800/60 p-2.5 rounded-xl border border-stone-200 dark:border-stone-700 text-xs">
                        <span className="text-[10px] uppercase font-bold text-stone-500 dark:text-stone-400 block mb-0.5">
                          Fuente Verificada:
                        </span>
                        <span className="font-bold text-stone-800 dark:text-stone-200 line-clamp-1">
                          {art.source_name}
                        </span>
                      </div>

                      {/* Productos Involucrados */}
                      <div>
                        <span className="text-[10px] uppercase font-extrabold text-stone-500 dark:text-stone-400 block mb-1">
                          {artMeta.productsTitle}
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {(art.affected_products || []).slice(0, 3).map((p) => (
                            <span
                              key={p}
                              className="bg-stone-100 dark:bg-stone-800 text-stone-800 dark:text-stone-200 text-[10px] font-bold px-2 py-0.5 rounded-md"
                            >
                              {p}
                            </span>
                          ))}
                          {(art.affected_products || []).length > 3 && (
                            <span className="text-[10px] text-emerald-700 font-extrabold self-center">
                              +{(art.affected_products || []).length - 3} más
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Mecanismo de transmisión */}
                      <p className="text-xs text-stone-700 dark:text-stone-300 line-clamp-3 leading-relaxed font-normal">
                        {art.transmission_mechanism}
                      </p>
                    </div>

                    {/* Botón inferior verde esmeralda y botón Instagram */}
                    <div className="pt-3 border-t border-stone-100 dark:border-stone-800 flex items-center space-x-2">
                      <button
                        onClick={() => handleSelectArticle(art)}
                        className="flex-1 flex items-center justify-center space-x-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2.5 px-3 rounded-xl text-xs transition-all shadow-sm shadow-emerald-600/20 cursor-pointer"
                      >
                        <span>Leer Análisis</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setInstagramArticle(art);
                        }}
                        title="Generar Story para Instagram (9:16)"
                        className="p-2.5 rounded-xl bg-gradient-to-tr from-pink-500/15 via-rose-500/15 to-amber-500/15 hover:from-pink-500/25 hover:to-amber-500/25 text-pink-600 dark:text-pink-400 border border-pink-500/30 transition-all cursor-pointer shrink-0"
                      >
                        <Instagram className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      )}

      {/* Modal Creador y Exportador de Instagram Stories (9:16) */}
      {renderInstagramModal()}
    </div>
  );
};
