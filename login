<div id="login-container" style="max-width:420px;margin:60px auto;padding:24px;border:1px solid #e5e7eb;border-radius:16px;background:#fff;font-family:Inter,system-ui,Arial,sans-serif;">
  <h2 style="margin-bottom:8px;">Sign in</h2>
  <p style="margin-bottom:16px;color:#6b7280;">Enter your email and password to access your dashboard.</p>

  <div id="error-msg" style="color:#b91c1c;margin-bottom:12px;display:none;"></div>

  <div id="form-wrap">
    <input id="email" type="email" placeholder="Email" required autocomplete="email"
           style="width:100%;padding:12px;border:1px solid #cbd5e1;border-radius:10px;margin-bottom:10px;">
    <input id="password" type="password" placeholder="Password" required autocomplete="current-password"
           style="width:100%;padding:12px;border:1px solid #cbd5e1;border-radius:10px;margin-bottom:16px;">
    <button id="login-btn"
            style="width:100%;padding:12px;border:0;border-radius:12px;background:#685bc6;color:#fff;font-weight:600;cursor:pointer;">
      Log in
    </button>
  </div>

  <div id="already-wrap" style="display:none;">
    <p style="margin:12px 0;color:#374151;">You’re already signed in.</p>
    <button id="goto-dashboard"
            style="width:100%;padding:12px;border:0;border-radius:12px;background:#685bc6;color:#fff;font-weight:600;cursor:pointer;margin-bottom:8px;">
      Continue to dashboard
    </button>
    <button id="signout"
            style="width:100%;padding:12px;border:1px solid #e5e7eb;border-radius:12px;background:#fff;color:#111827;font-weight:600;cursor:pointer;">
      Sign out
    </button>
  </div>
</div>

<script type="module">
  import { initializeApp } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-app.js";
  import {
    getAuth,
    setPersistence,
    browserSessionPersistence, // use session-only so stale logins don't stick forever
    signInWithEmailAndPassword,
    onAuthStateChanged,
    signOut
  } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-auth.js";

  const firebaseConfig = {
    apiKey: "AIzaSyDbkrUWV13zBvl4L2lu5Qw5aLYbC9LCjJk",
    authDomain: "therfpqueen.firebaseapp.com",
    projectId: "therfpqueen-f11fd",
  };

  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);

  const err = document.getElementById("error-msg");
  const formWrap = document.getElementById("form-wrap");
  const alreadyWrap = document.getElementById("already-wrap");
  const loginBtn = document.getElementById("login-btn");
  const gotoBtn = document.getElementById("goto-dashboard");
  const signoutBtn = document.getElementById("signout");
  const emailEl = document.getElementById("email");
  const passEl = document.getElementById("password");

  const DASHBOARD_URL = "/dashboard"; // change to your path

  // Use session persistence so users aren’t silently logged in across browser restarts
  setPersistence(auth, browserSessionPersistence).catch(() => {});

  function showError(m) {
    err.textContent = m;
    err.style.display = "block";
  }
  function clearError() { err.style.display = "none"; }

  // Redirect ONLY after explicit login success
  loginBtn.addEventListener("click", async () => {
    clearError();
    const email = emailEl.value.trim();
    const password = passEl.value;
    if (!email || !password) return showError("Please enter your email and password.");

    try {
      await signInWithEmailAndPassword(auth, email, password);
      window.location.href = DASHBOARD_URL;
    } catch (e) {
      showError((e && e.message ? e.message : "Login failed.").replace("Firebase:", "").trim());
    }
  });

  // If already signed in, show “Continue” & “Sign out” instead of auto-redirecting
  onAuthStateChanged(auth, (user) => {
    if (user) {
      formWrap.style.display = "none";
      alreadyWrap.style.display = "block";
    } else {
      alreadyWrap.style.display = "none";
      formWrap.style.display = "block";
    }
  });

  gotoBtn?.addEventListener("click", () => (window.location.href = DASHBOARD_URL));
  signoutBtn?.addEventListener("click", async () => {
    await signOut(auth);
    alreadyWrap.style.display = "none";
    formWrap.style.display = "block";
  });

  // Optional: if you want to ALWAYS force a fresh login on this page, uncomment:
  // signOut(auth).catch(()=>{});
</script>
