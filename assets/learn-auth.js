/* stackcone Learn — accounts.
   Google sign-in with Firebase Auth; lesson progress synced to Firestore users/{uid}.
   Loaded as a module on every page that shows the header. Without window.SC_FIREBASE
   it does nothing and progress stays in localStorage. */
const SDK = "https://www.gstatic.com/firebasejs/10.12.2/";

import "./firebase-config.js"; // sets window.SC_FIREBASE, so pages need no extra tag

const cfg = window.SC_FIREBASE;

async function boot() {
  if (!cfg) return null;
  const [{ initializeApp }, auth, fs] = await Promise.all([
    import(SDK + "firebase-app.js"),
    import(SDK + "firebase-auth.js"),
    import(SDK + "firebase-firestore.js"),
  ]);
  const app = initializeApp(cfg);
  return { auth, fs, a: auth.getAuth(app), db: fs.getFirestore(app) };
}

const ready = boot().catch((e) => {
  console.warn("[stackcone] auth unavailable:", e);
  return null;
});

/* ---------- API used by the login / signup pages ---------- */

const MESSAGES = {
  "auth/popup-closed-by-user": "Sign-in was cancelled.",
  "auth/cancelled-popup-request": "Sign-in was cancelled.",
  "auth/popup-blocked": "Your browser blocked the Google window. Allow pop-ups for this site and try again.",
  "auth/unauthorized-domain": "Sign-in is not enabled for this domain yet.",
  "auth/network-request-failed": "Network error. Check your connection.",
  "auth/too-many-requests": "Too many attempts. Wait a minute and try again.",
  "auth/configuration-not-found": "Sign-in is not enabled yet for this site.",
  "auth/operation-not-allowed": "Sign-in is not enabled yet for this site.",
};

export function friendlyError(err) {
  return MESSAGES[err && err.code] || "Something went wrong. Please try again.";
}

async function need() {
  const f = await ready;
  if (!f) throw { code: "auth/configuration-not-found" };
  return f;
}

/** One button for both sign up and log in: Google creates the account on first use. */
export async function signInWithGoogle() {
  const { auth, a } = await need();
  const provider = new auth.GoogleAuthProvider();
  provider.setCustomParameters({ prompt: "select_account" });
  return (await auth.signInWithPopup(a, provider)).user;
}

export async function logOut() {
  const { auth, a } = await need();
  await auth.signOut(a);
}

/* ---------- header avatar ---------- */

function initials(user) {
  const src = (user.displayName || user.email || "?").trim();
  const parts = src.split(/[\s@._-]+/).filter(Boolean);
  return ((parts[0] || "?")[0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
}

function here() {
  return encodeURIComponent(location.pathname + location.search);
}

function renderAccount(user) {
  document.querySelectorAll("[data-auth-note]").forEach((el) => { el.hidden = !!user; });
  // Lesson pages reserve a [data-account] slot; other pages get one appended to the header.
  const host = document.querySelector("[data-account]") || document.querySelector(".header-inner");
  if (!host) return;
  let box = document.getElementById("sc-account");
  if (!box) {
    box = document.createElement("div");
    box.id = "sc-account";
    box.className = "sc-account";
    host.appendChild(box);
  }
  if (!user) {
    box.innerHTML = `<a class="sc-account-login" href="/login/?next=${here()}">Log in</a>`;
    return;
  }
  const label = user.displayName || user.email;
  box.innerHTML = `
    <button type="button" class="sc-avatar" aria-haspopup="true" aria-expanded="false" title="${escapeHtml(label)}">${escapeHtml(initials(user))}</button>
    <div class="sc-account-menu" hidden>
      <p class="sc-account-who"><strong>${escapeHtml(user.displayName || "Learner")}</strong><span>${escapeHtml(user.email || "")}</span></p>
      <a href="/learn/">My courses</a>
      <button type="button" data-logout>Log out</button>
    </div>`;
  const btn = box.querySelector(".sc-avatar");
  const menu = box.querySelector(".sc-account-menu");
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    menu.hidden = !menu.hidden;
    btn.setAttribute("aria-expanded", String(!menu.hidden));
  });
  document.addEventListener("click", () => { menu.hidden = true; btn.setAttribute("aria-expanded", "false"); });
  box.querySelector("[data-logout]").addEventListener("click", () => logOut());
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/* ---------- progress sync ---------- */

let unsubDoc = null;
let pushTimer = null;
let applyingRemote = false;
let currentPush = null;
let listening = false;

function startSync(f, user) {
  const P = window.SCProgress;
  if (!P) return;
  const ref = f.fs.doc(f.db, "users", user.uid);

  const push = () => {
    clearTimeout(pushTimer);
    pushTimer = setTimeout(() => {
      f.fs.setDoc(ref, { completed: P.all(), updatedAt: f.fs.serverTimestamp() }, { merge: true })
        .catch((e) => console.warn("[stackcone] progress save failed:", e));
    }, 400);
  };

  unsubDoc = f.fs.onSnapshot(ref, (snap) => {
    const remote = snap.exists() ? snap.data().completed : null;
    applyingRemote = true;
    P.merge(remote || {});
    applyingRemote = false;
    // Local has something the cloud lacks (first login, offline marks) → upload it.
    const local = P.all();
    const differs = !remote || Object.keys(local).some((k) => local[k] !== remote[k]);
    if (differs) push();
  });

  currentPush = push;
  if (!listening) {
    listening = true;
    P.onChange(() => {
      if (!applyingRemote && currentPush) currentPush();
    });
  }
}

function stopSync() {
  if (unsubDoc) unsubDoc();
  unsubDoc = null;
  currentPush = null;
  clearTimeout(pushTimer);
}

ready.then((f) => {
  if (!f) return;
  f.auth.onAuthStateChanged(f.a, (user) => {
    stopSync();
    renderAccount(user);
    if (user) startSync(f, user);
    document.dispatchEvent(new CustomEvent("sc:auth", { detail: { user } }));
  });
});
