// ============ Theme toggle ============
(function initTheme() {
  const saved = localStorage.getItem("kyu-theme") || "dark";
  document.documentElement.setAttribute("data-theme", saved);
})();
function toggleTheme() {
  const cur = document.documentElement.getAttribute("data-theme");
  const next = cur === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("kyu-theme", next);
  const icon = document.getElementById("themeIcon");
  if (icon) icon.className = next === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
}
document.addEventListener("DOMContentLoaded", () => {
  const cur = document.documentElement.getAttribute("data-theme");
  const icon = document.getElementById("themeIcon");
  if (icon) icon.className = cur === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";

  // Highlight active nav
  const path = location.pathname.split("/").pop() || "home.html";
  document.querySelectorAll(".navbar .nav-link").forEach(a => {
    if (a.getAttribute("href") === path) a.classList.add("active");
  });
});

// ============ Populate filter selects ============
function populateSelect(id, items, placeholder) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = `<option value="">${placeholder}</option>` + items.map(x => `<option value="${x}">${x}</option>`).join("");
}
function initFinderOptions() {
  if (!window.EDU_DATA) return;
  const D = window.EDU_DATA;
  populateSelect("f-course", D.courses, "Any course");
  populateSelect("f-personality", D.personalities, "Any personality");
  populateSelect("f-budget", D.budgets, "Any budget");
  populateSelect("f-location", D.countries, "Any country");
  populateSelect("f-ranking", D.rankings, "Any ranking");
  populateSelect("f-exam", D.exams, "Any exam");
}

// ============ Rendering: University Cards ============
function uniCardHTML(u) {
  const shortlisted = isShortlisted(u.id);
  const inCompare = isInCompare(u.id);
  return `
  <div class="uni-card" data-testid="uni-card-${u.id}">
    <a class="uni-card-link text-decoration-none" href="university.html?id=${u.id}">
      <div class="uni-image">
        <img src="${u.image}" alt="${u.name}" loading="lazy" />
        <div class="uni-logo">${u.short}</div>
        <div class="badge-rank">#${u.rank} World</div>
      </div>
      <div class="uni-body">
        <h5>${u.name}</h5>
        <div class="uni-loc">${u.city}, ${u.country}</div>
        <div class="uni-flag">
          <span class="flag-txt"><span style="font-size:1.15rem">${u.flag}</span> ${u.country}</span>
          <span class="arrow-btn"><i class="bi bi-arrow-right"></i></span>
        </div>
      </div>
    </a>
    <div class="uni-actions-strip" data-testid="uni-actions-${u.id}">
      <button type="button" class="uni-action-btn heart-action ${shortlisted?'active':''}" data-uni-heart="${u.id}" data-testid="heart-${u.id}" onclick="toggleShortlist('${u.id}', this)" aria-label="Save to shortlist">
        <i class="bi bi-heart${shortlisted?'-fill':''}"></i>
        <span>Save</span>
      </button>
      <button type="button" class="uni-action-btn compare-action ${inCompare?'active':''}" data-uni-compare="${u.id}" data-testid="compare-${u.id}" onclick="toggleCompare('${u.id}', this)" aria-label="Add to compare">
        <i class="bi bi-${inCompare?'check-lg':'plus-lg'}"></i>
        <span>Compare</span>
      </button>
    </div>
  </div>`;
}

// ============ Shortlist & Compare (localStorage) ============
const KYU_SHORTLIST = "kyu-shortlist";
const KYU_COMPARE = "kyu-compare";

function getShortlist() { try { return JSON.parse(localStorage.getItem(KYU_SHORTLIST) || "[]"); } catch(e) { return []; } }
function setShortlist(arr) { localStorage.setItem(KYU_SHORTLIST, JSON.stringify(arr)); updateFAB(); }
function isShortlisted(id) { return getShortlist().includes(id); }
function toggleShortlist(id, btn) {
  const list = getShortlist();
  const i = list.indexOf(id);
  if (i > -1) list.splice(i, 1); else list.push(id);
  setShortlist(list);
  document.querySelectorAll(`[data-uni-heart="${id}"]`).forEach(b => {
    const active = list.includes(id);
    b.classList.toggle("active", active);
    b.querySelector("i").className = "bi bi-heart" + (active ? "-fill" : "");
  });
  showToast(list.includes(id) ? "Added to shortlist ❤" : "Removed from shortlist");
  // Re-render shortlist page if we're on it
  if (typeof renderShortlist === "function" && document.getElementById("shortlistGrid")) renderShortlist();
}

function getCompare() { try { return JSON.parse(localStorage.getItem(KYU_COMPARE) || "[]"); } catch(e) { return []; } }
function setCompare(arr) { localStorage.setItem(KYU_COMPARE, JSON.stringify(arr)); updateFAB(); }
function isInCompare(id) { return getCompare().includes(id); }
function toggleCompare(id, btn) {
  const list = getCompare();
  const i = list.indexOf(id);
  if (i > -1) {
    list.splice(i, 1);
  } else {
    if (list.length >= 3) { showToast("Max 3 universities in compare. Remove one first."); return; }
    list.push(id);
  }
  setCompare(list);
  document.querySelectorAll(`[data-uni-compare="${id}"]`).forEach(b => {
    const active = list.includes(id);
    b.classList.toggle("active", active);
    b.querySelector("i").className = "bi bi-" + (active ? "check-lg" : "plus-lg");
  });
  showToast(list.includes(id) ? "Added to compare" : "Removed from compare");
  if (typeof renderCompare === "function" && document.getElementById("compareWrap")) renderCompare();
}

// ============ Floating Action Bar (visible on all pages) ============
function injectFAB() {
  if (document.getElementById("kyuFab")) return;
  const fab = document.createElement("div");
  fab.id = "kyuFab";
  fab.className = "kyu-fab";
  fab.innerHTML = `
    <a href="shortlist.html" class="kyu-fab-btn" data-testid="fab-shortlist" title="My Shortlist" aria-label="Shortlist">
      <i class="bi bi-heart-fill"></i>
      <span class="kyu-fab-count" id="fabShortlistCount">0</span>
    </a>
    <a href="compare.html" class="kyu-fab-btn" data-testid="fab-compare" title="Compare Universities" aria-label="Compare">
      <i class="bi bi-columns-gap"></i>
      <span class="kyu-fab-count" id="fabCompareCount">0</span>
    </a>`;
  document.body.appendChild(fab);
  updateFAB();
}
function updateFAB() {
  const s = getShortlist().length, c = getCompare().length;
  const fab = document.getElementById("kyuFab");
  if (!fab) return;
  // Hide entire FAB when nothing added — prevents overlap on other content
  fab.style.display = (s + c) > 0 ? "flex" : "none";
  const es = document.getElementById("fabShortlistCount");
  const ec = document.getElementById("fabCompareCount");
  const btnShort = es ? es.closest("a") : null;
  const btnComp = ec ? ec.closest("a") : null;
  if (btnShort) btnShort.style.display = s > 0 ? "inline-flex" : "none";
  if (btnComp) btnComp.style.display = c > 0 ? "inline-flex" : "none";
  if (es) { es.textContent = s; es.style.display = s ? "flex" : "none"; }
  if (ec) { ec.textContent = c; ec.style.display = c ? "flex" : "none"; }
}

// ============ Toast (lightweight, no bootstrap needed) ============
function showToast(msg) {
  let t = document.getElementById("kyuToast");
  if (!t) {
    t = document.createElement("div");
    t.id = "kyuToast";
    t.className = "kyu-toast";
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(t._h);
  t._h = setTimeout(() => t.classList.remove("show"), 2200);
}

// ============ User / Auth (localStorage) ============
const KYU_USER = "kyu-user";
const KYU_BOOKINGS = "kyu-bookings";
function getUser() { try { return JSON.parse(localStorage.getItem(KYU_USER) || "null"); } catch(e) { return null; } }
function setUser(u) { localStorage.setItem(KYU_USER, JSON.stringify(u)); }
function logoutUser() {
  if (!confirm("Log out of your account?")) return;
  const finish = () => {
    localStorage.removeItem(KYU_USER);
    localStorage.removeItem(KYU_BOOKINGS);
    localStorage.removeItem("kyu-shortlist");
    localStorage.removeItem("kyu-compare");
    window.location.href = "home.html";
  };
  if (typeof window.apiLogout === "function") {
    window.apiLogout().finally(finish);
  } else {
    finish();
  }
}
function getBookings() { try { return JSON.parse(localStorage.getItem(KYU_BOOKINGS) || "[]"); } catch(e) { return []; } }
function setBookings(list) { localStorage.setItem(KYU_BOOKINGS, JSON.stringify(list)); }

// Swap Login link for Dashboard when user is logged in
function updateAuthNav() {
  const user = getUser();
  if (!user) return;
  document.querySelectorAll('[data-testid="nav-login"]').forEach(el => {
    el.setAttribute("href", "dashboard.html");
    el.setAttribute("data-testid", "nav-dashboard-link");
    el.innerHTML = `<i class="bi bi-person-circle me-1"></i>${(user.name||"Dashboard").split(" ")[0]}`;
  });
  document.querySelectorAll('[data-testid="nav-signup"]').forEach(el => el.remove());
}

// ============ University Detail Page ============
function renderUniversityDetail() {
  const wrap = document.getElementById("uniDetail");
  if (!wrap || !window.EDU_DATA) return;
  const id = new URLSearchParams(location.search).get("id");
  const u = window.EDU_DATA.universities.find(x => x.id === id);
  if (!u) {
    wrap.innerHTML = `<div class="container" style="padding-top:9rem"><div class="feature-card text-center"><h3 class="font-display">University not found</h3><p class="text-muted-2">Please browse the directory.</p><a href="universities.html" class="btn-yellow mt-3">Browse Universities</a></div></div>`;
    return;
  }
  document.title = `${u.name} — knowYourUniversity`;

  const courseChips = u.courses.map(c => `<span class="chip-mini">${c}</span>`).join(" ");
  const highlights = [
    { icon:"bi-award-fill", title:"World-Class Education", txt:"Learn from renowned professors through a rigorous curriculum recognized globally." },
    { icon:"bi-lightbulb-fill", title:"Cutting-Edge Research", txt:"Participate in groundbreaking research using advanced laboratories and technologies." },
    { icon:"bi-rocket-takeoff", title:"Innovation & Entrepreneurship", txt:"Develop creative ideas, build startups, and collaborate in a thriving ecosystem." },
    { icon:"bi-people-fill", title:"Powerful Alumni Network", txt:"Join a global network of successful alumni supporting career growth." },
    { icon:"bi-building", title:"State-of-the-Art Facilities", txt:"Access modern classrooms, research centers, libraries, and world-class resources." },
    { icon:"bi-cash-coin", title:"Scholarship Opportunities", txt:"Access merit-based and need-based scholarships to reduce tuition costs." }
  ];

  wrap.innerHTML = `
    <!-- Detail Hero -->
    <section class="uni-hero-detail" data-testid="uni-detail-hero" style="
      position:relative; min-height:70vh; padding: 8rem 0 4rem;
      background: linear-gradient(180deg, rgba(11,17,32,.55) 0%, rgba(11,17,32,.92) 100%), url('${u.image}') center/cover no-repeat;
      color:#fff;">
      <div class="container">
        <a href="universities.html" class="text-decoration-none" style="color:rgba(255,255,255,.85)" data-testid="back-to-directory"><i class="bi bi-arrow-left me-2"></i>Back to directory</a>
        <div class="row mt-4 align-items-end g-4">
          <div class="col-lg-8">
            <div class="d-flex align-items-center gap-3 mb-3">
              <div class="uni-logo" style="position:static;width:64px;height:64px;font-size:1.2rem">${u.short}</div>
              <div>
                <div class="text-uppercase-wide" style="color:var(--accent-primary);letter-spacing:.24em;font-size:.8rem">Ranked #${u.rank} in the World</div>
                <div style="font-size:.9rem;opacity:.85"><span style="font-size:1.1rem">${u.flag}</span> ${u.city}, ${u.country}</div>
              </div>
            </div>
            <h1 class="font-display" style="font-size:clamp(2.4rem,6vw,5rem);font-weight:900;line-height:1;letter-spacing:-.02em;text-transform:uppercase" data-testid="uni-detail-name">${u.name}</h1>
            <p class="mt-3" style="max-width:640px;opacity:.9;font-size:1.1rem" data-testid="uni-detail-desc">${u.desc}</p>
            <div class="mt-4 d-flex flex-wrap gap-3">
              <a href="${u.website||'contact.html'}" target="_blank" rel="noopener" class="btn-yellow" data-testid="uni-apply-btn"><i class="bi bi-box-arrow-up-right me-2"></i>Visit Official Website</a>
              <a href="scholarships.html" class="btn-outline-glass" data-testid="uni-scholarships-btn"><i class="bi bi-cash-coin me-2"></i>View Scholarships</a>
              <button class="btn-outline-glass ${isShortlisted(u.id)?'active-heart':''}" id="detailHeartBtn" onclick="toggleShortlist('${u.id}', this)" data-testid="uni-shortlist-btn" data-uni-heart="${u.id}"><i class="bi bi-heart${isShortlisted(u.id)?'-fill':''} me-2"></i>${isShortlisted(u.id)?'Shortlisted':'Add to Shortlist'}</button>
              <button class="btn-outline-glass" onclick="toggleCompare('${u.id}', this)" data-testid="uni-compare-btn" data-uni-compare="${u.id}"><i class="bi bi-${isInCompare(u.id)?'check-lg':'plus-lg'} me-2"></i>${isInCompare(u.id)?'In Compare':'Add to Compare'}</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Band -->
    <section style="padding: 3rem 0" data-testid="uni-stats">
      <div class="container">
        <div class="row g-3">
          <div class="col-6 col-md-3"><div class="feature-card text-center"><div class="feature-icon mx-auto"><i class="bi bi-calendar3"></i></div><div class="font-display fw-bold" style="font-size:1.8rem;color:var(--accent-primary)">${u.founded||"—"}</div><div class="text-muted-2 text-uppercase-wide">Founded</div></div></div>
          <div class="col-6 col-md-3"><div class="feature-card text-center"><div class="feature-icon mx-auto"><i class="bi bi-people-fill"></i></div><div class="font-display fw-bold" style="font-size:1.8rem;color:var(--accent-primary)">${u.students?u.students.toLocaleString():"—"}</div><div class="text-muted-2 text-uppercase-wide">Students</div></div></div>
          <div class="col-6 col-md-3"><div class="feature-card text-center"><div class="feature-icon mx-auto"><i class="bi bi-trophy-fill"></i></div><div class="font-display fw-bold" style="font-size:1.8rem;color:var(--accent-primary)">#${u.rank}</div><div class="text-muted-2 text-uppercase-wide">World Rank</div></div></div>
          <div class="col-6 col-md-3"><div class="feature-card text-center"><div class="feature-icon mx-auto"><i class="bi bi-cash-stack"></i></div><div class="font-display fw-bold" style="font-size:1.8rem;color:var(--accent-primary)">$${(u.tuition||0).toLocaleString()}</div><div class="text-muted-2 text-uppercase-wide">Tuition / yr</div></div></div>
        </div>
      </div>
    </section>

    <!-- Courses Offered -->
    <section style="background:var(--bg-secondary); padding: 4rem 0" data-testid="uni-courses">
      <div class="container">
        <div class="d-flex align-items-center mb-2"><div class="divider-line me-3"></div><span class="section-eyebrow">Courses Offered</span></div>
        <h2 class="section-title mb-4">Programs at ${u.short}</h2>
        <div>${courseChips.replace(/chip-mini/g,'chip-mini').replace(/></g,'>').replace(/class="chip-mini"/g,'class="chip-mini" style="font-size:.85rem;padding:.5rem 1rem;margin:.3rem"')}</div>
        <p class="text-muted-2 mt-4">${u.name} is celebrated for excellence across ${u.courses.length} major disciplines. Students benefit from world-renowned faculty, extensive research resources and a global alumni network.</p>
      </div>
    </section>

    <!-- Why Choose -->
    <section style="padding: 4rem 0" data-testid="uni-why">
      <div class="container">
        <div class="d-flex align-items-center mb-2"><div class="divider-line me-3"></div><span class="section-eyebrow">Have you ever wondered?</span></div>
        <h2 class="section-title mb-4">Why Choose ${u.short}?</h2>
        <div class="row g-4">
          ${highlights.map(h => `
            <div class="col-md-6 col-lg-4">
              <div class="feature-card">
                <div class="feature-icon"><i class="bi ${h.icon}"></i></div>
                <h5 class="font-display">${h.title}</h5>
                <p class="text-muted-2 mb-0">${h.txt}</p>
              </div>
            </div>`).join("")}
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section style="background:var(--bg-secondary); padding: 4rem 0" data-testid="uni-cta">
      <div class="container">
        <div class="finder-card d-flex flex-wrap gap-3 align-items-center justify-content-between" style="padding:2rem">
          <div>
            <h3 class="font-display mb-1">Ready to apply to ${u.short}?</h3>
            <p class="text-muted-2 mb-0">Our advisors help with applications, essays, and scholarships — free.</p>
          </div>
          <div class="d-flex gap-2">
            <a href="contact.html" class="btn-yellow" data-testid="uni-book-consultation"><i class="bi bi-calendar-check me-2"></i>Book Consultation</a>
            <a href="universities.html" class="btn-outline-glass" data-testid="uni-explore-more">Explore More Universities</a>
          </div>
        </div>
      </div>
    </section>
  `;
}

function renderHomeUniversities() {
  const wrap = document.getElementById("uniScroll");
  if (!wrap || !window.EDU_DATA) return;
  wrap.innerHTML = window.EDU_DATA.universities.map(uniCardHTML).join("");
}
function scrollUni(dir) {
  const wrap = document.getElementById("uniScroll");
  if (!wrap) return;
  wrap.scrollBy({ left: dir * 340, behavior: "smooth" });
}

// ============ Universities Directory ============
let uniFilters = { q:"", country:"", course:"", ranking:"" };
function renderUniversitiesGrid() {
  const grid = document.getElementById("uniGrid");
  const count = document.getElementById("uniCount");
  if (!grid || !window.EDU_DATA) return;
  const q = uniFilters.q.toLowerCase();
  let list = window.EDU_DATA.universities.filter(u => {
    if (uniFilters.country && u.country !== uniFilters.country) return false;
    if (uniFilters.course && !u.courses.includes(uniFilters.course)) return false;
    if (uniFilters.ranking === "Top 10" && u.rank > 10) return false;
    if (uniFilters.ranking === "Top 50" && u.rank > 50) return false;
    if (uniFilters.ranking === "Top 100" && u.rank > 100) return false;
    if (q && !(u.name.toLowerCase().includes(q) || u.city.toLowerCase().includes(q) || u.country.toLowerCase().includes(q))) return false;
    return true;
  });
  grid.innerHTML = list.length
    ? list.map(u => `<div class="col-md-6 col-lg-4">${uniCardHTML(u)}</div>`).join("")
    : `<div class="col-12"><div class="feature-card text-center"><h5>No universities match your filters.</h5><p class="text-muted-2 mb-0">Try loosening a filter.</p></div></div>`;
  if (count) count.textContent = `${list.length} universities found`;
}
function initUniversitiesPage() {
  if (!document.getElementById("uniGrid")) return;
  const D = window.EDU_DATA;
  populateSelect("u-country", D.countries, "All countries");
  populateSelect("u-course", D.courses, "All courses");
  populateSelect("u-ranking", D.rankings, "All rankings");

  document.getElementById("u-search").addEventListener("input", e => { uniFilters.q = e.target.value; renderUniversitiesGrid(); });
  document.getElementById("u-country").addEventListener("change", e => { uniFilters.country = e.target.value; renderUniversitiesGrid(); });
  document.getElementById("u-course").addEventListener("change", e => { uniFilters.course = e.target.value; renderUniversitiesGrid(); });
  document.getElementById("u-ranking").addEventListener("change", e => { uniFilters.ranking = e.target.value; renderUniversitiesGrid(); });

  renderUniversitiesGrid();
}

// ============ Courses Page ============
function renderCourses() {
  const grid = document.getElementById("courseGrid");
  if (!grid || !window.EDU_DATA) return;
  const tag = document.getElementById("courseTag")?.value || "";
  const q = (document.getElementById("courseSearch")?.value || "").toLowerCase();
  const list = window.EDU_DATA.courseCatalog.filter(c => {
    if (tag && c.tag !== tag) return false;
    if (q && !c.name.toLowerCase().includes(q)) return false;
    return true;
  });
  grid.innerHTML = list.length ? list.map(c => {
    const id = c.name.replace(/\s+/g,'-').toLowerCase();
    const careers = (c.careers||[]).slice(0,4).map(x => `<span class="chip-mini" style="margin:2px">${x}</span>`).join("");
    const skills = (c.skills||[]).slice(0,4).map(x => `<span style="font-size:.75rem;color:var(--text-secondary)">${x}</span>`).join(" · ");
    return `
    <div class="col-md-6 col-lg-4">
      <div class="course-card" data-testid="course-card-${id}" onclick="openCourseModal('${encodeURIComponent(c.name)}')" style="cursor:pointer">
        <div class="cimg"><img src="${c.image}" alt="${c.name}" loading="lazy"></div>
        <div class="cbody">
          <span class="chip-mini">${c.tag}</span>
          <h5 class="mt-2">${c.name}</h5>
          <p>${c.desc}</p>
          <div class="d-flex gap-3 pt-2 pb-2 mb-2" style="border-top:1px dashed var(--border-color);border-bottom:1px dashed var(--border-color)">
            <div><small class="text-muted-2 text-uppercase-wide">Duration</small><div style="font-size:.85rem">${c.duration||'—'}</div></div>
            <div><small class="text-muted-2 text-uppercase-wide">Avg Salary</small><div style="font-size:.85rem;color:var(--accent-primary);font-weight:700">${c.avgSalary||'—'}</div></div>
          </div>
          <div class="mb-2"><small class="text-muted-2 text-uppercase-wide">Career Paths</small><div class="mt-1">${careers}</div></div>
          <div class="mb-3"><small class="text-muted-2 text-uppercase-wide">Top Universities</small><div style="font-size:.85rem" class="mt-1">${(c.topUnis||[]).slice(0,4).join(" · ")}</div></div>
          ${skills ? `<div class="mb-3"><small class="text-muted-2 text-uppercase-wide">Key Skills</small><div class="mt-1">${skills}</div></div>` : ""}
          <div class="d-flex justify-content-between align-items-center pt-2" style="border-top:1px solid var(--border-color)">
            <span class="text-accent text-uppercase-wide" data-testid="course-open-${id}"><i class="bi bi-eye me-1"></i>View Details & Best Colleges</span>
            <i class="bi bi-arrow-right-circle-fill text-accent" style="font-size:1.25rem"></i>
          </div>
        </div>
      </div>
    </div>`; }).join("") : `<div class="col-12"><div class="feature-card text-center"><h5>No courses match.</h5></div></div>`;
}

// ============ Course Detail Modal ============
function openCourseModal(encodedName) {
  const name = decodeURIComponent(encodedName);
  const c = window.EDU_DATA.courseCatalog.find(x => x.name === name);
  if (!c) return;
  const modalEl = document.getElementById("courseModal");
  if (!modalEl) return;
  const bestColleges = window.EDU_DATA.universities
    .filter(u => u.courses.includes(c.name))
    .sort((a, b) => a.rank - b.rank)
    .slice(0, 6);
  document.getElementById("cmImage").style.backgroundImage = `url('${c.image}')`;
  document.getElementById("cmTag").textContent = c.tag;
  document.getElementById("cmName").textContent = c.name;
  document.getElementById("cmDesc").textContent = c.desc;
  document.getElementById("cmDuration").textContent = c.duration || "—";
  document.getElementById("cmSalary").textContent = c.avgSalary || "—";
  document.getElementById("cmCareers").innerHTML = (c.careers||[]).map(x => `<span class="chip-mini" style="margin:3px">${x}</span>`).join("");
  document.getElementById("cmSkills").innerHTML = (c.skills||[]).map(x => `<span class="chip-mini" style="margin:3px;background:rgba(59,130,246,.14);color:#3B82F6">${x}</span>`).join("");
  const cw = document.getElementById("cmColleges");
  cw.innerHTML = bestColleges.length ? bestColleges.map(u => `
    <a href="university.html?id=${u.id}" class="d-flex align-items-center gap-3 text-decoration-none" style="color:inherit;padding:.85rem;border:1px solid var(--border-color);border-radius:14px;background:var(--bg-secondary);margin-bottom:.6rem;transition:all .25s ease" onmouseover="this.style.borderColor='var(--accent-primary)'" onmouseout="this.style.borderColor='var(--border-color)'" data-testid="cm-college-${u.id}">
      <div class="uni-logo" style="position:static;width:44px;height:44px;font-size:.85rem">${u.short}</div>
      <div style="flex:1">
        <div class="font-display fw-bold" style="font-size:.95rem;line-height:1.15">${u.name}</div>
        <small class="text-muted-2">${u.flag} ${u.city}, ${u.country}</small>
      </div>
      <div style="text-align:right">
        <div class="text-accent font-display fw-bold" style="font-size:.9rem">#${u.rank} World</div>
        <small class="text-muted-2">$${(u.tuition||0).toLocaleString()}/yr</small>
      </div>
      <i class="bi bi-arrow-right text-accent"></i>
    </a>`).join("") : `<div class="text-muted-2 text-center" style="padding:1rem">No universities in our directory currently offer this course.</div>`;
  const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
  bsModal.show();
}
function initCoursesPage() {
  if (!document.getElementById("courseGrid")) return;
  const tags = [...new Set(window.EDU_DATA.courseCatalog.map(c => c.tag))];
  populateSelect("courseTag", tags, "All categories");
  document.getElementById("courseTag").addEventListener("change", renderCourses);
  document.getElementById("courseSearch").addEventListener("input", renderCourses);
  renderCourses();
}

// ============ Scholarships Page ============
function renderScholarships() {
  const grid = document.getElementById("schGrid");
  if (!grid || !window.EDU_DATA) return;
  const country = document.getElementById("schCountry")?.value || "";
  const q = (document.getElementById("schSearch")?.value || "").toLowerCase();
  const list = window.EDU_DATA.scholarships.filter(s => {
    if (country && s.country !== country) return false;
    if (q && !s.name.toLowerCase().includes(q)) return false;
    return true;
  });
  grid.innerHTML = list.length ? list.map(s => `
    <div class="col-md-6 col-lg-4">
      <div class="scholarship-card" data-testid="sch-card-${s.name.replace(/\s+/g,'-').toLowerCase()}">
        <span class="sc-tag">${s.type}</span>
        <h5 class="mt-3 font-display">${s.name}</h5>
        <div class="text-muted-2 mb-2"><i class="bi bi-geo-alt me-1"></i>${s.country}</div>
        <p class="text-muted-2">${s.desc}</p>
        <div class="d-flex align-items-center justify-content-between mt-3 pt-3" style="border-top:1px solid var(--border-color)">
          <div>
            <div class="sc-amount">${s.amount}</div>
            <small class="text-muted-2">Deadline: ${s.deadline}</small>
          </div>
          <button class="btn-yellow btn-sm" style="padding:.55rem 1rem" data-testid="sch-apply-${s.name.replace(/\s+/g,'-').toLowerCase()}">Apply</button>
        </div>
      </div>
    </div>`).join("") : `<div class="col-12"><div class="feature-card text-center"><h5>No scholarships match.</h5></div></div>`;
}
function initScholarshipsPage() {
  if (!document.getElementById("schGrid")) return;
  const countries = [...new Set(window.EDU_DATA.scholarships.map(s => s.country))];
  populateSelect("schCountry", countries, "All countries");
  document.getElementById("schCountry").addEventListener("change", renderScholarships);
  document.getElementById("schSearch").addEventListener("input", renderScholarships);
  renderScholarships();
}

// ============ College Finder Submit ============
function submitFinder(e) {
  e.preventDefault();
  const params = new URLSearchParams();
  ["f-course","f-personality","f-budget","f-location","f-ranking","f-exam"].forEach(id => {
    const val = document.getElementById(id)?.value;
    if (val) params.set(id.replace("f-",""), val);
  });
  // Basic client-side: navigate to universities with course/country/ranking
  const target = new URLSearchParams();
  if (params.get("course")) target.set("course", params.get("course"));
  if (params.get("location")) target.set("country", params.get("location"));
  if (params.get("ranking")) target.set("ranking", params.get("ranking"));
  window.location.href = "universities.html?" + target.toString();
}

// ============ Contact / Login form (mock) ============
function handleForm(e, msgId) {
  e.preventDefault();
  const msg = document.getElementById(msgId);
  if (msg) {
    msg.classList.remove("d-none");
    setTimeout(() => msg.classList.add("d-none"), 4500);
  }
  e.target.reset();
}

// ============ Auto-init on load ============
document.addEventListener("DOMContentLoaded", () => {
  injectFAB();
  updateAuthNav();
  initFinderOptions();
  renderHomeUniversities();
  initUniversitiesPage();
  initCoursesPage();
  initScholarshipsPage();

  // Prefill from query params on universities page
  const p = new URLSearchParams(location.search);
  if (document.getElementById("uniGrid") && (p.get("course") || p.get("country") || p.get("ranking"))) {
    if (p.get("course")) { document.getElementById("u-course").value = p.get("course"); uniFilters.course = p.get("course"); }
    if (p.get("country")) { document.getElementById("u-country").value = p.get("country"); uniFilters.country = p.get("country"); }
    if (p.get("ranking")) { document.getElementById("u-ranking").value = p.get("ranking"); uniFilters.ranking = p.get("ranking"); }
    renderUniversitiesGrid();
  }
});
