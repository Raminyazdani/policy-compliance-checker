import { http, API_BASE } from '../../api/http';

export const usersApi = {
  list:   () => http('GET', '/users'),
  get:    (id) => http('GET', `/users/${id}`),
  create: (objOrArr) => http('POST', '/users', objOrArr),
  put:    (id, payload) => http('PUT', `/users/${id}`, payload),
  del:    (id) => http('DELETE', `/users/${id}`),

  upload: async (file, clear = false) => {
    const fd = new FormData();
    fd.append('file', file);
    if (clear) fd.append('clear', '1');

    const res = await fetch(`${API_BASE}/upload/users`, {
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
