import { createStore } from '../../store/createStore';
import { policiesApi } from './policies.api';

export const usePolicies = createStore([
  (set, get) => ({
    items: [],
    loading: false,
    error: '',

    async refresh() {
      set({ loading:true, error:'' });
      try {
        const data = await policiesApi.list();
        set({ items: data, loading:false });
      } catch (e) {
        set({ error: e.message || String(e), loading:false });
      }
    },

    async createOne(p) {
      await policiesApi.create(p);
      await get().refresh();
    },

    async updateOne(policy_id, p) {
      await policiesApi.put(policy_id, p);
      await get().refresh();
    },

    async deleteOne(policy_id) {
      await policiesApi.del(policy_id);
      await get().refresh();
    },

    async getOne(policy_id) {
      return policiesApi.get(policy_id);
    }
  })
]);
