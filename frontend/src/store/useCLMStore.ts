import { create } from 'zustand';

interface CLMState {
  engineers: any[];
  recommendations: string;
  optimizationAction: string;
  isLoading: boolean;
  isOptimizing: boolean;
  error: string | null;
  fetchData: () => Promise<void>;
  triggerIncident: () => Promise<void>;
  fetchRecommendations: () => Promise<void>;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const useCLMStore = create<CLMState>((set) => ({
  engineers: [],
  recommendations: '',
  optimizationAction: '',
  isLoading: false,
  isOptimizing: false,
  error: null,
  fetchData: async () => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API_URL}/api/engineers`);
      if (!res.ok) {
        const message = await getErrorMessage(res);
        throw new Error(message);
      }
      const data = await res.json();
      set({ engineers: data, isLoading: false, error: null });
    } catch (e) {
      set({ error: getThrownMessage(e, 'Failed to fetch data'), isLoading: false });
    }
  },
  triggerIncident: async () => {
    set({ error: null });
    try {
      const incidentRes = await fetch(`${API_URL}/api/simulate/incident`, { method: 'POST' });
      if (!incidentRes.ok) {
        const message = await getErrorMessage(incidentRes);
        throw new Error(message);
      }

      const res = await fetch(`${API_URL}/api/engineers`);
      if (!res.ok) {
        const message = await getErrorMessage(res);
        throw new Error(message);
      }
      const data = await res.json();
      set({ engineers: data, error: null });
    } catch (e) {
      set({ error: getThrownMessage(e, 'Simulation failed') });
    }
  },
  fetchRecommendations: async () => {
    set({ isOptimizing: true, error: null });
    try {
      const res = await fetch(`${API_URL}/api/recommendations`, { method: 'POST' });
      if (!res.ok) {
        const message = await getErrorMessage(res);
        throw new Error(message);
      }
      const data = await res.json();
      set((state) => ({
        recommendations: data.recommendations || 'No recommendations returned.',
        optimizationAction: data.applied_action || '',
        engineers: Array.isArray(data.engineers) ? data.engineers : state.engineers,
        isOptimizing: false,
        error: null,
      }));
    } catch (e) {
      set({
        error: getThrownMessage(e, 'Failed to fetch AI recommendations'),
        isOptimizing: false,
      });
    }
  },
}));

const getErrorMessage = async (response: Response) => {
  try {
    const data = await response.json();
    return data.detail || data.message || `${response.status} ${response.statusText}`;
  } catch {
    return `${response.status} ${response.statusText}`;
  }
};

const getThrownMessage = (error: unknown, fallback: string) => {
  return error instanceof Error ? error.message : fallback;
};
