import { http, API_BASE } from '../../api/http';

export const policiesApi = {
  list: async () => {
    const data = await http('GET', '/policies');
    return (data || []).map(p => ({ ...p, policy_id: p.policy_id ?? p.id }));
  },
  get:    (policy_id)          => http('GET',    `/policies/${policy_id}`),
  create: (objOrArr)           => http('POST',   '/policies', objOrArr),
  put:    (policy_id, payload) => http('PUT',    `/policies/${policy_id}`, payload),
  del:    (policy_id)          => http('DELETE', `/policies/${policy_id}`),

  // افزودن فلگ clear (اختیاری)
  upload: async (file, clear = false) => {
    const fd = new FormData();
    fd.append('file', file);
    if (clear) fd.append('clear', '1');

    const res = await fetch(`${API_BASE}/upload/policies`, {
      method: 'POST',
      body: fd,
      credentials: 'include',
    });
    if (!res.ok) {
      const err = await res.json().catch(()=>({error:`HTTP ${res.status}`}));
      throw new Error(err.error || `Upload failed (${res.status})`);
    }
    return res.json();
  },
};
