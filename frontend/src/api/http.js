// src/api/http.js
const API_BASE = '/api';            // مسیر پایه برای بک‌اند (پروکسی یا Nginx)
export { API_BASE };

/**
 * JSON & FormData-friendly HTTP helper
 * - اگر body از نوع FormData باشد، header ست نمی‌شود و بدنه همان FormData می‌رود.
 * - برای JSON، به‌صورت پیش‌فرض application/json ست می‌شود.
 */
export async function http(method, path, body) {
  const isForm = typeof FormData !== 'undefined' && body instanceof FormData;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: isForm ? undefined : { 'Content-Type': 'application/json' },
    body: isForm ? body : (body ? JSON.stringify(body) : undefined),
    credentials: 'include', // اگر کوکی لازم ندارید، می‌توانید بردارید
  });

  const text = await res.text();
  let data;
  try { data = text ? JSON.parse(text) : null; }
  catch { data = text; }

  if (!res.ok) {
    throw new Error((data && data.error) || `${res.status} ${res.statusText}`);
  }
  return data;
}
