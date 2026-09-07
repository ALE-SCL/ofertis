import React, { useEffect, useState } from 'react';
import { X, ExternalLink, TrendingDown, Bell, CheckCircle, Store } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import axios from 'axios';
import { CanonicalProductDetail, SupermarketItemComparison } from '../types';

interface ProductDetailModalProps {
  canonicalId: number | null;
  onClose: () => void;
  onSetAlert: (productName: string, canonicalId: number, currentBestPrice: number) => void;
}

export const ProductDetailModal: React.FC<ProductDetailModalProps> = ({
  canonicalId,
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
        const [detailRes, histRes] = await Promise.all([
          axios.get(`http://localhost:8000/api/v1/products/${canonicalId}`),
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
  }, [canonicalId]);

  if (!canonicalId) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-3 sm:p-6 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden border border-slate-200">
        {/* Header Modal */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                {product?.category.replace('_', ' ')}
              </span>
              {product?.brand && (
                <span className="text-xs text-slate-500 font-medium">Marca: {product.brand}</span>
              )}
            </div>
            <h2 className="text-lg sm:text-xl font-black text-slate-900 mt-1">
              {product?.name || 'Cargando comparativa...'}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="w-9 h-9 rounded-full bg-slate-200/70 hover:bg-slate-300 flex items-center justify-center text-slate-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto custom-scrollbar flex-1 space-y-6">
          {loading ? (
            <div className="py-16 text-center">
              <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              <p className="text-sm font-semibold text-slate-500">Consultando bases de datos de Jumbo, Santa Isabel, Unimarc y Lider...</p>
            </div>
          ) : product ? (
            <>
              {/* Resumen del Mejor Precio */}
              <div className="bg-gradient-to-br from-emerald-500 to-teal-700 text-white rounded-2xl p-5 shadow-lg flex flex-wrap items-center justify-between gap-4">
                <div>
                  <span className="text-xs font-extrabold uppercase tracking-wider bg-white/20 px-2.5 py-1 rounded-full">
                    Opción más económica recomendada
                  </span>
                  <div className="text-2xl sm:text-3xl font-black mt-2">
                    ${Math.round(product.best_price_per_unit || 0).toLocaleString('es-CL')}
                    <span className="text-sm font-semibold text-emerald-100 ml-1">
                      / {product.standard_unit}
                    </span>
                  </div>
                  <p className="text-xs text-emerald-100 mt-1 flex items-center space-x-1">
                    <Store className="w-3.5 h-3.5" />
                    <span>Disponible en <strong>{product.best_supermarket_name}</strong></span>
                  </p>
                </div>

                <button
                  onClick={() => onSetAlert(product.name, product.id, Number(product.best_price_per_unit || 0))}
                  className="flex items-center space-x-2 bg-white text-emerald-800 hover:bg-emerald-50 active:scale-95 font-black px-4 py-2.5 rounded-xl shadow-md transition-all text-sm"
                >
                  <Bell className="w-4 h-4 text-emerald-600" />
                  <span>Activar Alerta WhatsApp</span>
                </button>
              </div>

              {/* Tabla Comparativa de Supermercados */}
              <div>
                <h3 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider mb-3 flex items-center space-x-1.5">
                  <span>Comparativa Directa de Tiendas</span>
                  <span className="text-xs font-normal text-slate-500">(Ordenado de menor a mayor precio por {product.standard_unit})</span>
                </h3>

                <div className="overflow-x-auto rounded-2xl border border-slate-200">
                  <table className="w-full text-left text-sm text-slate-600">
                    <thead className="bg-slate-100 text-xs font-bold text-slate-700 uppercase tracking-wider border-b border-slate-200">
                      <tr>
                        <th className="py-3 px-4">Supermercado</th>
                        <th className="py-3 px-4">Formato Tienda</th>
                        <th className="py-3 px-4">Precio Lista</th>
                        <th className="py-3 px-4">Precio Oferta</th>
                        <th className="py-3 px-4 text-emerald-800 font-black">Precio /{product.standard_unit}</th>
                        <th className="py-3 px-4 text-center">Ir a Tienda</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {product.items.map((item, idx) => {
                        const isBest = idx === 0;
                        return (
                          <tr key={item.id} className={isBest ? 'bg-emerald-50/60 font-semibold' : 'hover:bg-slate-50'}>
                            <td className="py-3.5 px-4 flex items-center space-x-2">
                              <span
                                className="w-3 h-3 rounded-full flex-shrink-0"
                                style={{ backgroundColor: item.supermarket_color }}
                              ></span>
                              <span className="font-bold text-slate-900">{item.supermarket_name}</span>
                              {isBest && (
                                <span className="bg-emerald-600 text-white text-[10px] font-black px-2 py-0.5 rounded-full">
                                  MEJOR PRECIO
                                </span>
                              )}
                            </td>
                            <td className="py-3.5 px-4 text-xs font-medium text-slate-700">
                              {item.store_title} ({item.package_quantity} {item.package_unit})
                            </td>
                            <td className="py-3.5 px-4 text-slate-500">
                              ${Math.round(item.current_normal_price).toLocaleString('es-CL')}
                            </td>
                            <td className="py-3.5 px-4">
                              {item.current_offer_price ? (
                                <span className="text-red-600 font-bold bg-red-50 px-2 py-0.5 rounded">
                                  ${Math.round(item.current_offer_price).toLocaleString('es-CL')}
                                </span>
                              ) : (
                                <span className="text-slate-400 text-xs">Sin descuento</span>
                              )}
                            </td>
                            <td className="py-3.5 px-4 text-slate-900 font-extrabold text-base">
                              ${Math.round(item.current_unit_price_normalized).toLocaleString('es-CL')}
                            </td>
                            <td className="py-3.5 px-4 text-center">
                              <a
                                href={item.product_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center space-x-1 text-blue-600 hover:text-blue-800 text-xs font-bold"
                              >
                                <span>Ver</span>
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
                <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="text-sm font-black text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
                        <TrendingDown className="w-4 h-4 text-blue-600" />
                        <span>Histórico de Precios por {product.standard_unit} (CLP)</span>
                      </h4>
                      <p className="text-xs text-slate-500">Detección de inflación y fluctuación de ofertas</p>
                    </div>
                  </div>

                  <div className="h-60 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={history}>
                        <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} />
                        <YAxis stroke="#94a3b8" fontSize={11} domain={['auto', 'auto']} tickFormatter={(v) => `$${v}`} />
                        <Tooltip
                          formatter={(value: any) => [`$${Math.round(Number(value)).toLocaleString('es-CL')} CLP`, 'Precio']}
                          contentStyle={{ backgroundColor: '#1e293b', borderRadius: '12px', border: 'none', color: '#fff' }}
                        />
                        <Line
                          type="monotone"
                          dataKey="price_per_unit"
                          stroke="#2563eb"
                          strokeWidth={3}
                          dot={{ r: 4, fill: '#2563eb' }}
                          name="Precio Normalizado"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="py-12 text-center text-slate-500">No se encontraron detalles del producto.</div>
          )}
        </div>
      </div>
    </div>
  );
};
