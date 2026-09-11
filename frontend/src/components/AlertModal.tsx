import React, { useState } from 'react';
import { X, Bell, CheckCircle2, MessageSquare, AlertTriangle } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../config/api';

interface AlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  productName: string;
  canonicalId: number | null;
  currentBestPrice: number;
}

export const AlertModal: React.FC<AlertModalProps> = ({
  isOpen,
  onClose,
  productName,
  canonicalId,
  currentBestPrice
}) => {
  const [phone, setPhone] = useState('+569');
  const [userName, setUserName] = useState('');
  const [targetPrice, setTargetPrice] = useState(
    currentBestPrice > 0 ? Math.round(currentBestPrice * 0.9).toString() : '9000'
  );
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canonicalId) return;

    setLoading(true);
    setError(null);

    try {
      await axios.post(`${API_BASE_URL}/alerts`, {
        user_phone: phone,
        user_name: userName.trim() || 'Usuario Ofertis',
        canonical_id: canonicalId,
        target_unit_price: parseFloat(targetPrice)
      });

      // Disparar evaluación inmediata para probar la notificación
      await axios.post(`${API_BASE_URL}/alerts/evaluate/${canonicalId}`);

      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al suscribir la alerta de WhatsApp.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-stone-900/60 dark:bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white dark:bg-stone-900 rounded-3xl max-w-md w-full shadow-2xl overflow-hidden border border-stone-200 dark:border-stone-800 animate-in fade-in zoom-in duration-200">
        <div className="px-6 py-4 bg-gradient-to-r from-orange-600 to-amber-500 text-white flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <MessageSquare className="w-5 h-5 text-orange-100" />
            <h3 className="font-extrabold text-base">Alerta de Precios por WhatsApp 🇨🇱</h3>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-6">
          {success ? (
            <div className="text-center py-6 space-y-3">
              <div className="w-14 h-14 bg-orange-50 dark:bg-orange-950/60 text-orange-600 dark:text-orange-400 rounded-full flex items-center justify-center mx-auto border border-orange-200 dark:border-orange-800">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h4 className="text-lg font-black text-stone-900 dark:text-stone-100">¡Alerta Suscrita con Éxito!</h4>
              <p className="text-xs text-stone-600 dark:text-stone-300">
                Hemos registrado tu número <strong>{phone}</strong> para recibir alertas de <strong>{productName}</strong> cuando el precio baje a <strong>${parseInt(targetPrice).toLocaleString('es-CL')} CLP</strong> o menos.
              </p>
              <button
                onClick={onClose}
                className="mt-4 w-full bg-stone-900 dark:bg-stone-800 text-white font-bold py-2.5 rounded-xl text-xs hover:bg-stone-800 dark:hover:bg-stone-700"
              >
                Entendido
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <span className="text-xs text-stone-500 dark:text-stone-400 font-semibold uppercase">Producto a Monitorear</span>
                <p className="text-sm font-bold text-stone-900 dark:text-stone-100">{productName}</p>
                {currentBestPrice > 0 && (
                  <p className="text-xs text-orange-700 dark:text-orange-400 font-semibold mt-0.5">
                    Mejor precio actual: ${Math.round(currentBestPrice).toLocaleString('es-CL')} CLP
                  </p>
                )}
              </div>

              {error && (
                <div className="bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-xs p-3 rounded-xl flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div>
                <label className="block text-xs font-bold text-stone-700 dark:text-stone-300 mb-1">
                  Tu Nombre o Apodo
                </label>
                <input
                  type="text"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  placeholder="Ej: Camilo"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-stone-300 dark:border-stone-700 bg-white dark:bg-stone-800 text-stone-900 dark:text-stone-100 placeholder-stone-400 dark:placeholder-stone-500 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-stone-700 dark:text-stone-300 mb-1">
                  Número de Celular Chileno (WhatsApp)
                </label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+56912345678"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-stone-300 dark:border-stone-700 bg-white dark:bg-stone-800 text-stone-900 dark:text-stone-100 placeholder-stone-400 dark:placeholder-stone-500 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                  required
                />
                <span className="text-[11px] text-stone-500 dark:text-stone-400">Formato chileno: +56 9 XXXX XXXX</span>
              </div>

              <div>
                <label className="block text-xs font-bold text-stone-700 dark:text-stone-300 mb-1">
                  Alertarme si el precio por kg/L baja de:
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-2.5 text-stone-400 dark:text-stone-500 font-bold text-sm">$</span>
                  <input
                    type="number"
                    value={targetPrice}
                    onChange={(e) => setTargetPrice(e.target.value)}
                    className="w-full pl-7 pr-12 py-2.5 rounded-xl border border-stone-300 dark:border-stone-700 bg-white dark:bg-stone-800 text-sm font-bold text-stone-900 dark:text-stone-100 focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                  <span className="absolute right-3 top-2.5 text-stone-400 dark:text-stone-500 text-xs font-bold">CLP</span>
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center space-x-2 bg-orange-600 hover:bg-orange-500 active:scale-95 text-white font-extrabold py-3 px-4 rounded-xl text-sm transition-all shadow-md shadow-orange-500/20 disabled:opacity-50"
                >
                  <Bell className="w-4 h-4" />
                  <span>{loading ? 'Guardando Alerta...' : 'Crear Alerta WhatsApp'}</span>
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
