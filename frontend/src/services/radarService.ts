import axios from 'axios';
import { PriceOpportunity, AlternativeStore, RadarKPIs } from '../types/radar';
import { API_BASE_URL } from '../config/api';

const RADAR_API_URL = `${API_BASE_URL}/radar`;

export const radarService = {
  async getOpportunities(category?: string, q?: string, store?: string): Promise<PriceOpportunity[]> {
    const params: Record<string, string> = {};
    if (category && category !== 'todos') {
      params.category = category;
    }
    if (store && store !== 'todas') {
      params.store = store;
    }
    if (q && q.trim()) {
      params.q = q.trim();
    }
    const res = await axios.get(`${RADAR_API_URL}/opportunities`, { params });
    return res.data;
  },

  async getStores(): Promise<AlternativeStore[]> {
    const res = await axios.get(`${RADAR_API_URL}/stores`);
    return res.data;
  },

  async getKpis(): Promise<RadarKPIs> {
    const res = await axios.get(`${RADAR_API_URL}/kpis`);
    return res.data;
  }
};
