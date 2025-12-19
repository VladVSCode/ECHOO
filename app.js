// ==============================
// Налаштування бекенду
// ==============================

// TODO: зміни на IP свого ПК з Flask-сервером
// Наприклад: const API_BASE = "http://192.168.0.106:5000";
const API_BASE = "http://192.168.0.106:5000";

const LOGIN_URL = `${API_BASE}/login`;
const REGISTER_URL = `${API_BASE}/register`;

// ==============================
// DOM-елементи
// ==============================

const loginScreen = document.getElementById("loginScreen");
const appScreen = document.getElementById("appScreen");

const loginForm = document.getElementById("loginForm");
const loginInput = document.getElementById("login");
const passwordInput = document.getElementById("password");
const loginResult = document.getElementById("loginResult");

const userLoginSpan = document.getElementById("userLogin");
const loginTimeSpan = document.getElementById("loginTime");
const logoutBtn = document.getElementById("logoutBtn");

const registerScreen = document.getElementById("registerScreen");
const registerForm = document.getElementById("registerForm");
const registerLoginInput = document.getElementById("registerLogin");
const registerPasswordInput = document.getElementById("registerPassword");
// ==============================
// Локальне "збереження сесії"
// ==============================

const SESSION_KEY = "echoo_session";

function saveSession(login) {
  const session = {
    login,
    loginTime: new Date().toISOString()
  };
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

function loadSession() {
  const raw = localStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (e) {
    console.warn("Failed to parse session", e);
    return null;
  }
}

function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

// ==============================
// UI: перемикання екранiв
// ==============================

function showLoginScreen() {
  loginScreen.classList.remove("hidden");
  appScreen.classList.add("hidden");
  registerScreen.classList.add("hidden");
  loginResult.textContent = "";
}

function showAppScreen(session) {
  loginScreen.classList.add("hidden");
  appScreen.classList.remove("hidden");
  registerScreen.classList.add("hidden");

  userLoginSpan.textContent = session.login;
  loginTimeSpan.textContent = new Date(session.loginTime).toLocaleString();
}

//перемикання на екран реєстрації
function showRegisterScreen() {
  loginScreen.classList.add("hidden");
  appScreen.classList.add("hidden");
  registerScreen.classList.remove("hidden");
}

// ==============================
// Обробка логіну
// ==============================

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginResult.textContent = "";
  loginResult.className = "mt-3 text-center";

  const login = loginInput.value.trim();
  const password = passwordInput.value;

  if (!login || !password) {
    loginResult.textContent = "Будь ласка, заповніть логін і пароль.";
    loginResult.classList.add("status-error");
    return;
  }

  try {
    const response = await fetch(LOGIN_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login, password })
    });

    const data = await response.json();

    if (response.ok) {
      // Успішний вхід
      loginResult.textContent = "Вхід успішний.";
      loginResult.classList.add("status-ok");

      saveSession(login);
      const session = loadSession();
      showAppScreen(session);
    } else {
      // Помилка логіну або блокування
      loginResult.textContent = data.error || "Помилка входу.";
      loginResult.classList.add("status-error");
    }
  } catch (error) {
    console.error("Login error:", error);
    loginResult.textContent = "Помилка з’єднання з сервером.";
    loginResult.classList.add("status-error");
  }
});

// ==============================
// Реєстрація
// ==============================


async function registerUser(login, password) {
  try {
    const response = await fetch(REGISTER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login, password })
    });
    const data = await response.json();
    if (response.ok) {
      alert("Реєстрація успішна! Тепер увійдіть.");
    } else {
      alert(data.error || "Помилка реєстрації.");
    }
  } catch (err) {
    alert("Помилка з’єднання з сервером.");
  }
}


// ==============================
// Логаут
// ==============================

logoutBtn.addEventListener("click", () => {
  clearSession();
  showLoginScreen();
});

// ==============================
// Обробка реєстрації  (пункт 3)
// ==============================
registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const login = registerLoginInput.value.trim();
  const password = registerPasswordInput.value;

  if (!login || !password) {
    alert("Будь ласка, заповніть логін і пароль.");
    return;
  }

  await registerUser(login, password);

  // після успішної реєстрації повертаємо на логін
  showLoginScreen();
});

// ==============================
// Ініціалізація при завантаженні
// ==============================

document.addEventListener("DOMContentLoaded", () => {
  const session = loadSession();
  if (session) {
    showAppScreen(session);
  } else {
    showLoginScreen();
  }
});
