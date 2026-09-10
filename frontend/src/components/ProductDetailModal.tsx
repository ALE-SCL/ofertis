import React, { useEffect, useState } from 'react';
import { X, ExternalLink, TrendingDown, Bell } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import { CanonicalProductDetail } from '../types';

interface ProductDetailModalProps {
  canonicalId: number | null;
  format?: string | null;
  onClose: () => void;
  onSetAlert: (productName: string, canonicalId: number, currentBestPrice: number) => void;
}

export const ProductDetailModal: React.FC<ProductDetailModalProps> = ({
  canonicalId,
  format,
  onClose,
  onSetAlert
}) => {
  const [product, setProduct] = useState<CanonicalProductDetail | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!canonicalId) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const queryFmt = format ? `?format=${encodeURIComponent(format)}` : '';
        const [detailRes, histRes] = await Promise.all([
          axios.get(`http://localhost:8000/api/v1/products/${canonicalId}${queryFmt}`),
          axios.get(`http://localhost:8000/api/v1/products/${canonicalId}/history`)
        ]);
        setProduct(detailRes.data);
        setHistory(histRes.data);
      } catch (err) {
        console.error('Error fetching detail:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [canonicalId, format]);

  if (!canonicalId) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-stone-900/60 backdrop-blur-sm flex items-center justify-center p-3 sm:p-6 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden border border-stone-200">
        {/* Header Modal */}
        <div className="px-6 py-4 border-b border-stone-200 flex items-center justify-between bg-stone-50">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold uppercase tracking-wider text-orange-800 bg-orange-50 px-2 py-0.5 rounded border border-orange-200">
                {product?.category.replace('_', ' ')}
              </span>
              {product?.package_format && (
                <span className="text-xs font-bold text-stone-700 bg-stone-200/80 px-2 py-0.5 rounded">
                  Formato: {product.package_format}
                </span>
              )}
              {product?.brand && (
                <span className="text-xs text-stone-500 font-medium">Marca: {product.brand}</span>
              )}
            </div>
            <h2 className="text-lg sm:text-xl font-black text-stone-900 mt-1">
              {product?.name || 'Cargando comparativa...'}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="w-9 h-9 rounded-full bg-stone-200/70 hover:bg-stone-300 flex items-center justify-center text-stone-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto custom-scrollbar flex-1 space-y-6">
          {loading ? (
            <div className="py-16 text-center">
              <div className="w-10 h-10 border-4 border-orange-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              <p className="text-sm font-semibold text-stone-500">Consultando bases de datos de Jumbo, Santa Isabel, Unimarc y Lider...</p>
            </div>
          ) : product ? (
            <>
              {/* Resumen del Mejor Precio */}
              <div className="bg-gradient-to-r from-orange-600 via-orange-500 to-amber-500 text-white rounded-2xl p-5 shadow-md flex flex-wrap items-center justify-between gap-4">
                <div>
                  <span className="text-xs font-black uppercase tracking-wider bg-white/20 px-3 py-1 rounded-full">
                    ★ Precio más barato: {product.best_supermarket_name}
                  </span>
                  <div className="text-2xl sm:text-3xl font-black mt-2 flex items-baseline space-x-2">
                    <span>${Math.round(product.best_package_price || product.best_price_per_unit || 0).toLocaleString('es-CL')}</span>
                    {product.package_format && (
                      <span className="text-sm font-bold bg-white/20 px-2.5 py-0.5 rounded-lg">
                        {product.package_format}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-orange-100 mt-1 flex flex-wrap items-center gap-3">
                    <span>Ref. unitaria: ${Math.round(product.best_price_per_unit || 0).toLocaleString('es-CL')} / {product.standard_unit}</span>
                    {product.savings_amount && product.savings_amount > 0 && (
                      <span className="bg-emerald-600 text-white font-extrabold px-2 py-0.5 rounded">
                        Ahorras ${Math.round(product.savings_amount).toLocaleString('es-CL')} ({product.savings_percentage}%)
                      </span>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => onSetAlert(product.name, product.id, Number(product.best_package_price || product.best_price_per_unit || 0))}
                  className="flex items-center space-x-2 bg-white text-orange-950 hover:bg-orange-50 active:scale-95 font-black px-4 py-2.5 rounded-xl shadow-md transition-all text-sm"
                >
                  <Bell className="w-4 h-4 text-orange-600" />
                  <span>Activar Alerta WhatsApp</span>
                </button>
              </div>

              {/* Tabla Comparativa de Supermercados */}
              <div>
                <h3 className="text-sm font-extrabold text-stone-900 uppercase tracking-wider mb-3 flex items-center space-x-1.5">
                  <span>Comparativa Directa para este Formato ({product.package_format || 'Estándar'})</span>
                  <span className="text-xs font-normal text-stone-500">(Ordenado del más barato al más caro)</span>
                </h3>

                <div className="overflow-x-auto rounded-2xl border border-stone-200">
                  <table className="w-full text-left text-sm text-stone-600">
                    <thead className="bg-stone-100 text-xs font-bold text-stone-700 uppercase tracking-wider border-b border-stone-200">
                      <tr>
                        <th className="py-3 px-4">Supermercado</th>
                        <th className="py-3 px-4">Formato / Descripción</th>
                        <th className="py-3 px-4 text-orange-950 font-black">Precio a Pagar</th>
                        <th className="py-3 px-4">Ref. /{product.standard_unit}</th>
                        <th className="py-3 px-4 text-center">Ir a Tienda</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-stone-100">
                      {product.items.map((item) => {
                        const isCheapest = item.is_cheapest;
                        return (
                          <tr key={item.id} className={isCheapest ? 'bg-orange-50/60 font-semibold' : 'hover:bg-stone-50'}>
                            <td className="py-3.5 px-4 flex items-center space-x-2">
                              <span
                                className="w-3 h-3 rounded-full flex-shrink-0"
                                style={{ backgroundColor: item.supermarket_color }}
                              ></span>
                              <span className="font-bold text-stone-900">{item.supermarket_name}</span>
                              {isCheapest && (
                                <span className="bg-orange-600 text-white text-[10px] font-black px-2 py-0.5 rounded-full">
                                  ★ PRECIO MÁS BARATO
                                </span>
                              )}
                            </td>
                            <td className="py-3.5 px-4 text-xs font-medium text-stone-700">
                              {item.store_title} ({item.package_format || `${item.package_quantity} ${item.package_unit}`})
                            </td>
                            <td className="py-3.5 px-4">
                              <div className="text-base font-black text-stone-900">
                                ${Math.round(item.current_package_price).toLocaleString('es-CL')}
                              </div>
                              {item.current_offer_price && item.current_normal_price > item.current_offer_price && (
                                <div className="text-[10px] text-stone-400 line-through">
                                  Normal: ${Math.round(item.current_normal_price).toLocaleString('es-CL')}
                                </div>
                              )}
                            </td>
                            <td className="py-3.5 px-4 text-stone-600 font-medium text-xs">
                              ${Math.round(item.current_unit_price_normalized).toLocaleString('es-CL')} /{product.standard_unit}
                            </td>
                            <td className="py-3.5 px-4 text-center">
                              <a
                                href={item.product_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center space-x-1 text-orange-600 hover:text-orange-700 text-xs font-bold"
                              >
                                <span>Comprar</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Gráfico de Evolución Histórica de Precios */}
              {history.length > 0 && (
                <div className="bg-stone-50 rounded-2xl p-5 border border-stone-200">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="text-sm font-black text-stone-900 uppercase tracking-wider flex items-center space-x-1.5">
                        <TrendingDown className="w-4 h-4 text-orange-600" />
                        <span>Histórico de Precios por {product.standard_unit} (CLP)</span>
                      </h4>
                      <p className="text-xs text-stone-500">Detección de inflación y fluctuación de ofertas</p>
                    </div>
                  </div>

                  <div className="h-60 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={history}>
                        <XAxis dataKey="date" stroke="#a8a29e" fontSize={11} />
                        <YAxis stroke="#a8a29e" fontSize={11} domain={['auto', 'auto']} tickFormatter={(v) => `$${v}`} />
                        <Tooltip
                          formatter={(value: any) => [`$${Math.round(Number(value)).toLocaleString('es-CL')} CLP`, 'Precio']}
                          contentStyle={{ backgroundColor: '#1c1917', borderRadius: '12px', border: 'none', color: '#fff' }}
                        />
                        <Line
                          type="monotone"
                          dataKey="price_per_unit"
                          stroke="#ea580c"
                          strokeWidth={3}
                          dot={{ r: 4, fill: '#ea580c' }}
                          name="Precio Normalizado"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="py-12 text-center text-stone-500">No se encontraron detalles del producto.</div>
          )}
        </div>
      </div>
    </div>
  );
};
