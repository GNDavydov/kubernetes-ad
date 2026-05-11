/** @typedef {{ access_token: string, token_type?: string }} TokenResponse */

const TOKEN_KEY = "kad_token";
const API = "";

let profile = null;
let trainChart = null;
let detectChart = null;

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(t) {
  if (t) localStorage.setItem(TOKEN_KEY, t);
  else localStorage.removeItem(TOKEN_KEY);
}

function showToast(msg, ok = true) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.remove("hidden", "ok", "err");
  el.classList.add(ok ? "ok" : "err");
  setTimeout(() => el.classList.add("hidden"), 3200);
}

async function api(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (opts.body && !(opts.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const res = await fetch(`${API}${path}`, { ...opts, headers });
  if (res.status === 401) {
    setToken(null);
    showApp(false);
    showToast("Сессия истекла — войдите снова", false);
    throw new Error("Unauthorized");
  }
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!res.ok) {
    const detail =
      data && typeof data === "object" && data.detail != null
        ? typeof data.detail === "string"
          ? data.detail
          : JSON.stringify(data.detail)
        : res.statusText;
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return data;
}

function showApp(show) {
  document.getElementById("login-view").classList.toggle("hidden", show);
  document.getElementById("app-view").classList.toggle("hidden", !show);
}

function setActiveNav(name) {
  document.querySelectorAll(".nav button[data-nav]").forEach((b) => {
    b.classList.toggle("active", b.dataset.nav === name);
  });
}

function destroyCharts() {
  if (trainChart) {
    trainChart.destroy();
    trainChart = null;
  }
  if (detectChart) {
    detectChart.destroy();
    detectChart = null;
  }
}

async function loadProfile() {
  profile = await api("/profile/me");
  const adminBtn = document.getElementById("nav-users");
  adminBtn.classList.toggle("hidden", profile.role !== "admin");
}

async function renderDashboard() {
  setActiveNav("dashboard");
  destroyCharts();
  const [models, integrations, tasks] = await Promise.all([
    api("/models"),
    api("/integrations"),
    api("/tasks"),
  ]);
  const trainTasks = tasks.filter((t) => t.type === "train");
  const detectTasks = tasks.filter((t) => t.type === "detect");
  const done = tasks.filter((t) => t.status === "done").length;
  document.getElementById("main").innerHTML = `
    <h2>Обзор</h2>
    <div class="grid cols-3">
      <div class="stat"><div class="value">${models.length}</div><div class="label">Моделей</div></div>
      <div class="stat"><div class="value">${integrations.length}</div><div class="label">Интеграций</div></div>
      <div class="stat"><div class="value">${tasks.length}</div><div class="label">Задач (всего)</div></div>
    </div>
    <p class="muted" style="margin-top:1rem">Обучение: ${trainTasks.length} · Детектирование: ${detectTasks.length} · Завершено: ${done}</p>
  `;
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function renderModels() {
  setActiveNav("models");
  destroyCharts();
  const models = await api("/models");
  document.getElementById("main").innerHTML = `
    <h2>Модели</h2>
    <div class="panel">
      <h3 style="margin-top:0">Создать</h3>
      <form id="form-model">
        <label>Имя <input name="name" required /></label>
        <label>Путь к весам (файл) <input name="model_path" required placeholder="./models/my.pt" /></label>
        <button type="submit">Создать</button>
      </form>
    </div>
    <div class="panel">
      <table><thead><tr><th>Имя</th><th>Статус</th><th>seq_len</th><th>threshold</th><th></th></tr></thead>
      <tbody>${models
        .map(
          (m) =>
            `<tr><td>${esc(m.name)}</td><td>${esc(m.status)}</td><td>${m.seq_len}</td><td>${m.threshold}</td>
            <td><button type="button" class="btn-secondary btn-del-model" data-id="${m.id}">Удалить</button></td></tr>`
        )
        .join("")}</tbody></table>
    </div>`;

  document.getElementById("form-model").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    await api("/models", {
      method: "POST",
      body: JSON.stringify({
        name: fd.get("name"),
        model_path: fd.get("model_path"),
      }),
    });
    showToast("Модель создана");
    renderModels();
  };
  document.querySelectorAll(".btn-del-model").forEach((btn) => {
    btn.onclick = async () => {
      if (!confirm("Удалить модель?")) return;
      await api(`/models/${btn.dataset.id}`, { method: "DELETE" });
      showToast("Удалено");
      renderModels();
    };
  });
}

async function renderIntegrations() {
  setActiveNav("integrations");
  destroyCharts();
  const list = await api("/integrations");
  document.getElementById("main").innerHTML = `
    <h2>Интеграции OpenSearch</h2>
    <div class="panel">
      <h3 style="margin-top:0">Создать</h3>
      <form id="form-int">
        <label>Имя <input name="name" required /></label>
        <label>URL <input name="url" required placeholder="https://opensearch:9200" /></label>
        <label>User <input name="username" /></label>
        <label>Password <input name="password" type="password" /></label>
        <label>Индекс логов <input name="log_source_name" required /></label>
        <label>Индекс аномалий <input name="anomaly_name" required /></label>
        <button type="submit">Создать</button>
      </form>
    </div>
    <div class="panel">
      <table><thead><tr><th>Имя</th><th>URL</th><th>Логи</th><th>Аномалии</th><th></th></tr></thead>
      <tbody>${list
        .map(
          (i) =>
            `<tr><td>${esc(i.name)}</td><td>${esc(i.url)}</td><td>${esc(i.log_source_name)}</td><td>${esc(i.anomaly_name)}</td>
            <td><button type="button" class="btn-secondary btn-del-int" data-id="${i.id}">Удалить</button></td></tr>`
        )
        .join("")}</tbody></table>
    </div>`;

  document.getElementById("form-int").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = {
      name: fd.get("name"),
      url: fd.get("url"),
      username: fd.get("username") || null,
      password: fd.get("password") || null,
      log_source_name: fd.get("log_source_name"),
      anomaly_name: fd.get("anomaly_name"),
    };
    await api("/integrations", { method: "POST", body: JSON.stringify(body) });
    showToast("Интеграция создана");
    renderIntegrations();
  };
  document.querySelectorAll(".btn-del-int").forEach((btn) => {
    btn.onclick = async () => {
      if (!confirm("Удалить интеграцию?")) return;
      await api(`/integrations/${btn.dataset.id}`, { method: "DELETE" });
      showToast("Удалено");
      renderIntegrations();
    };
  });
}

async function renderTasks() {
  setActiveNav("tasks");
  destroyCharts();
  const [tasks, models, integrations] = await Promise.all([
    api("/tasks"),
    api("/models"),
    api("/integrations"),
  ]);
  const modelOpts = models.map((m) => `<option value="${m.id}">${esc(m.name)}</option>`).join("");
  const intOpts = integrations.map((i) => `<option value="${i.id}">${esc(i.name)}</option>`).join("");
  document.getElementById("main").innerHTML = `
    <h2>Задачи</h2>
    <div class="panel">
      <h3 style="margin-top:0">Создать</h3>
      <form id="form-task">
        <label>Тип
          <select name="type" id="task-type"><option value="train">train</option><option value="detect">detect</option></select>
        </label>
        <label>Модель <select name="model_id" required>${modelOpts}</select></label>
        <label>Интеграция <select name="integration_id" required>${intOpts}</select></label>
        <label id="epochs-wrap">Эпохи (train) <input name="epochs" type="number" min="1" value="10" /></label>
        <button type="submit">Поставить в очередь</button>
      </form>
    </div>
    <div class="panel">
      <table><thead><tr><th>Тип</th><th>Статус</th><th>Эпохи</th><th>Создана</th><th></th></tr></thead>
      <tbody>${tasks
        .map(
          (t) =>
            `<tr><td>${esc(t.type)}</td><td>${esc(t.status)}</td><td>${t.epochs ?? "—"}</td><td>${t.created_at ? new Date(t.created_at).toLocaleString() : "—"}</td>
            <td class="row-actions">
              <button type="button" class="btn-metrics" data-id="${t.id}" data-type="${t.type}">Метрики</button>
            </td></tr>`
        )
        .join("")}</tbody></table>
    </div>`;

  const typeSel = document.getElementById("task-type");
  const epochsWrap = document.getElementById("epochs-wrap");
  const toggleEpochs = () => {
    epochsWrap.classList.toggle("hidden", typeSel.value !== "train");
  };
  typeSel.onchange = toggleEpochs;
  toggleEpochs();

  document.getElementById("form-task").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const type = fd.get("type");
    const body = {
      type,
      model_id: fd.get("model_id"),
      integration_id: fd.get("integration_id"),
      epochs: type === "train" ? Number(fd.get("epochs")) : null,
    };
    await api("/tasks", { method: "POST", body: JSON.stringify(body) });
    showToast("Задача создана");
    renderTasks();
  };

  document.querySelectorAll(".btn-metrics").forEach((btn) => {
    btn.onclick = () => openMetrics(btn.dataset.id, btn.dataset.type);
  });
}

async function openMetrics(taskId, type) {
  destroyCharts();
  const main = document.getElementById("main");
  main.innerHTML = `<p class="muted">Загрузка метрик…</p>`;
  if (type === "train") {
    const metrics = await api(`/tasks/${taskId}/train-metrics`);
    metrics.sort((a, b) => a.epoch - b.epoch);
    main.innerHTML = `
      <h2>Метрики обучения</h2>
      <p class="muted">Задача <code>${esc(taskId)}</code></p>
      <div class="panel"><div class="chart-wrap"><canvas id="chart-train"></canvas></div></div>
      <div class="panel">
        <table><thead><tr><th>Эпоха</th><th>loss</th><th>val_loss</th><th>duration</th></tr></thead>
        <tbody>${metrics
          .map(
            (m) =>
              `<tr><td>${m.epoch}</td><td>${m.loss.toFixed(6)}</td><td>${m.val_loss.toFixed(6)}</td><td>${m.duration.toFixed(2)}s</td></tr>`
          )
          .join("")}</tbody></table>
      </div>
      <button type="button" class="btn-secondary" id="back-tasks">← К задачам</button>`;
    const ctx = document.getElementById("chart-train");
    if (typeof Chart !== "undefined" && metrics.length) {
      trainChart = new Chart(ctx, {
        type: "line",
        data: {
          labels: metrics.map((m) => m.epoch),
          datasets: [
            {
              label: "train loss",
              data: metrics.map((m) => m.loss),
              borderColor: "#3d8bfd",
              tension: 0.15,
            },
            {
              label: "val loss",
              data: metrics.map((m) => m.val_loss),
              borderColor: "#3fb950",
              tension: 0.15,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { color: "#8b9cb3" } } },
          scales: {
            x: { ticks: { color: "#8b9cb3" }, grid: { color: "#2d3a4d" } },
            y: { ticks: { color: "#8b9cb3" }, grid: { color: "#2d3a4d" } },
          },
        },
      });
    } else if (!metrics.length) {
      main.querySelector(".panel").innerHTML = "<p>Метрик пока нет (задача не завершила обучение).</p>";
    }
  } else {
    const metrics = await api(`/tasks/${taskId}/detect-metrics`);
    main.innerHTML = `
      <h2>Дашборд детектирования</h2>
      <p class="muted">Задача <code>${esc(taskId)}</code></p>
      <div class="grid cols-3" style="margin-bottom:1rem">
        ${metrics
          .map(
            (m) => `
        <div class="stat">
          <div class="value">${m.anomalies_count}</div>
          <div class="label">Аномалий (запуск)</div>
          <div class="muted" style="margin-top:0.5rem;font-size:0.8rem">Событий: ${m.processed_events} · ${m.duration.toFixed(1)}s</div>
        </div>`
          )
          .join("")}
      </div>
      <div class="panel"><div class="chart-wrap"><canvas id="chart-detect"></canvas></div></div>
      <div class="panel">
        <table><thead><tr><th>Аномалий</th><th>Событий</th><th>Период</th><th>Длительность</th></tr></thead>
        <tbody>${metrics
          .map(
            (m) =>
              `<tr><td>${m.anomalies_count}</td><td>${m.processed_events}</td><td>${new Date(m.start_timestamp).toLocaleString()} — ${new Date(m.end_timestamp).toLocaleString()}</td><td>${m.duration.toFixed(2)}s</td></tr>`
          )
          .join("")}</tbody></table>
      </div>
      <button type="button" class="btn-secondary" id="back-tasks">← К задачам</button>`;
    const ctx = document.getElementById("chart-detect");
    if (typeof Chart !== "undefined" && metrics.length) {
      detectChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: metrics.map((_, i) => `Запуск ${i + 1}`),
          datasets: [
            {
              label: "Аномалий",
              data: metrics.map((m) => m.anomalies_count),
              backgroundColor: "rgba(61, 139, 253, 0.55)",
            },
            {
              label: "Обработано событий",
              data: metrics.map((m) => m.processed_events),
              backgroundColor: "rgba(63, 185, 80, 0.35)",
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { color: "#8b9cb3" } } },
          scales: {
            x: { ticks: { color: "#8b9cb3" }, grid: { color: "#2d3a4d" } },
            y: { ticks: { color: "#8b9cb3" }, grid: { color: "#2d3a4d" }, beginAtZero: true },
          },
        },
      });
    }
  }
  document.getElementById("back-tasks").onclick = () => renderTasks();
}

async function renderUsers() {
  if (profile?.role !== "admin") {
    showToast("Недостаточно прав", false);
    return renderDashboard();
  }
  setActiveNav("users");
  destroyCharts();
  const users = await api("/users");
  document.getElementById("main").innerHTML = `
    <h2>Пользователи (admin)</h2>
    <div class="panel">
      <h3 style="margin-top:0">Создать</h3>
      <form id="form-user">
        <label>Email <input name="email" type="email" required /></label>
        <label>Пароль <input name="password" type="password" required /></label>
        <label>Роль
          <select name="role"><option value="user">user</option><option value="admin">admin</option></select>
        </label>
        <button type="submit">Создать</button>
      </form>
    </div>
    <div class="panel">
      <table><thead><tr><th>Email</th><th>Роль</th><th>Создан</th></tr></thead>
      <tbody>${users
        .map(
          (u) =>
            `<tr><td>${esc(u.email)}</td><td>${esc(u.role)}</td><td>${u.created_at ? new Date(u.created_at).toLocaleString() : "—"}</td></tr>`
        )
        .join("")}</tbody></table>
    </div>`;

  document.getElementById("form-user").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    await api("/users", {
      method: "POST",
      body: JSON.stringify({
        email: fd.get("email"),
        password: fd.get("password"),
        role: fd.get("role"),
      }),
    });
    showToast("Пользователь создан");
    renderUsers();
  };
}

async function renderProfile() {
  setActiveNav("profile");
  destroyCharts();
  const me = await api("/profile/me");
  document.getElementById("main").innerHTML = `
    <h2>Профиль</h2>
    <div class="panel">
      <p><strong>Email:</strong> ${esc(me.email)}</p>
      <p><strong>Роль:</strong> ${esc(me.role)}</p>
      <p><strong>ID:</strong> <code>${me.id}</code></p>
    </div>
    <div class="panel">
      <h3 style="margin-top:0">Смена пароля</h3>
      <form id="form-pw">
        <label>Текущий пароль <input name="current_password" type="password" required /></label>
        <label>Новый пароль <input name="new_password" type="password" required /></label>
        <button type="submit">Обновить</button>
      </form>
    </div>`;

  document.getElementById("form-pw").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    await api("/profile/me/change-password", {
      method: "POST",
      body: JSON.stringify({
        current_password: fd.get("current_password"),
        new_password: fd.get("new_password"),
      }),
    });
    showToast("Пароль обновлён");
    renderProfile();
  };
}

function bindNav() {
  document.querySelectorAll(".nav button[data-nav]").forEach((btn) => {
    btn.onclick = () => {
      const nav = btn.dataset.nav;
      const routes = {
        dashboard: renderDashboard,
        models: renderModels,
        integrations: renderIntegrations,
        tasks: renderTasks,
        users: renderUsers,
        profile: renderProfile,
      };
      routes[nav]?.();
    };
  });
}

document.getElementById("login-form").onsubmit = async (e) => {
  e.preventDefault();
  const err = document.getElementById("login-error");
  err.textContent = "";
  const fd = new FormData(e.target);
  const body = new URLSearchParams();
  body.set("username", fd.get("email"));
  body.set("password", fd.get("password"));
  body.set("grant_type", "password");
  try {
    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || res.statusText);
    setToken(data.access_token);
    showApp(true);
    await loadProfile();
    await renderDashboard();
  } catch (ex) {
    err.textContent = ex.message || "Ошибка входа";
  }
};

document.getElementById("logout-btn").onclick = async () => {
  try {
    await api("/auth/logout", { method: "POST" });
  } catch {
    /* ignore */
  }
  setToken(null);
  profile = null;
  showApp(false);
};

bindNav();

if (getToken()) {
  (async () => {
    try {
      await loadProfile();
      showApp(true);
      await renderDashboard();
    } catch {
      setToken(null);
      showApp(false);
    }
  })();
} else {
  showApp(false);
}
