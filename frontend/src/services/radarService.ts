import axios from 'axios';
import { PriceOpportunity, AlternativeStore, RadarKPIs } from '../types/radar';

const API_BASE_URL = 'http://localhost:8000/api/v1/radar';

export const radarService = {
  async getOpportunities(category?: string): Promise<PriceOpportunity[]> {
    const params = category && category !== 'todos' ? { category } : {};
    const res = await axios.get(`${API_BASE_URL}/opportunities`, { params });
    return res.data;
  },

  async getStores(): Promise<AlternativeStore[]> {
    const res = await axios.get(`${API_BASE_URL}/stores`);
    return res.data;
  },

  async getKpis(): Promise<RadarKPIs> {
    const res = await axios.get(`${API_BASE_URL}/kpis`);
    return res.data;
  }
};
