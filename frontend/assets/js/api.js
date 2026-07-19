/**
 * knowYourUniversity — Frontend API adapter (Django backend integration)
 * ------------------------------------------------------------------
 * By default this file assumes the frontend is served BY the same Django
 * server (recommended). In that case KYU_API_URL is empty and requests
 * go to `/api/...` on the same origin, so session cookies just work.
 *
 * If you serve the frontend from a different origin (e.g. python -m http.server
 * on port 5500), set the URL manually BEFORE this script loads:
 *     <script>window.KYU_API_URL = "http://localhost:8000";</script>
 *     <script src="assets/js/api.js"></script>
 *
 * Setting window.KYU_API_URL to `false` disables the backend and falls back
 * to pure localStorage mode.
 */
(function () {
  // Same-origin default → API base is empty, everything hits /api/...
  if (typeof window.KYU_API_URL === "undefined") window.KYU_API_URL = "";
  if (window.KYU_API_URL === false) return; // explicitly disabled

  const API = window.KYU_API_URL;
  const j = (r) => r.json().then((d) => ({ ok: r.ok, status: r.status, data: d }));
  const req = (path, opts = {}) =>
    fetch(API + path, {
      credentials: "include",
      headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
      ...opts,
    }).then(j);

  // ---------- Auth ----------
  window.apiSignup = (data) => req("/api/auth/signup", { method: "POST", body: JSON.stringify(data) });
  window.apiLogin = (email, password) => req("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
  window.apiLogout = () => req("/api/auth/logout", { method: "POST" });
  window.apiMe = () => req("/api/auth/me");
  window.apiChangePassword = (current_password, new_password) =>
    req("/api/auth/change-password", { method: "POST", body: JSON.stringify({ current_password, new_password }) });

  // ---------- Profile ----------
  window.apiUpdateProfile = (data) => req("/api/profile", { method: "PATCH", body: JSON.stringify(data) });
  window.apiUploadAvatar = (file) => {
    const fd = new FormData();
    fd.append("avatar", file);
    return fetch(API + "/api/profile/avatar", { method: "POST", credentials: "include", body: fd }).then(j);
  };

  // ---------- Shortlist ----------
  window.apiGetShortlist = () => req("/api/shortlist");
  window.apiToggleShortlist = (uniId) => req("/api/shortlist/" + encodeURIComponent(uniId), { method: "POST" });

  // ---------- Compare ----------
  window.apiGetCompare = () => req("/api/compare");
  window.apiToggleCompare = (uniId) => req("/api/compare/" + encodeURIComponent(uniId), { method: "POST" });

  // ---------- Bookings ----------
  window.apiGetBookings = () => req("/api/bookings");
  window.apiCancelBooking = (id) => req("/api/bookings/" + id, { method: "DELETE" });

  // ---------- Payments ----------
  window.apiCreatePaymentOrder = (data) => req("/api/payments/create-order", { method: "POST", body: JSON.stringify(data) });
  window.apiVerifyPayment = (data) => req("/api/payments/verify", { method: "POST", body: JSON.stringify(data) });

  // ---------- Hydrate localStorage from backend on load ----------
  async function hydrate() {
    try {
      const me = await window.apiMe();
      if (me.ok && me.data.user) {
        localStorage.setItem("kyu-user", JSON.stringify(me.data.user));
      } else {
        localStorage.removeItem("kyu-user");
      }
      const s = await window.apiGetShortlist();
      if (s.ok) localStorage.setItem("kyu-shortlist", JSON.stringify(s.data.shortlist || []));
      const c = await window.apiGetCompare();
      if (c.ok) localStorage.setItem("kyu-compare", JSON.stringify(c.data.compare || []));
      const b = await window.apiGetBookings();
      if (b.ok) localStorage.setItem("kyu-bookings", JSON.stringify(b.data.bookings || []));
    } catch (e) {
      console.warn("[KYU] Backend unreachable — falling back to localStorage.", e);
    }
  }
  window.KYU_HYDRATE = hydrate;
  document.addEventListener("DOMContentLoaded", hydrate);
  console.log("[KYU] Django backend integration active →", API || "(same-origin)");
})();
