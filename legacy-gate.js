(() => {
  "use strict";

  const PASSWORD_HASH = "086a347a672b2b1e3f8f36234f757d2c0706cbcd106b784ca1278f6ba90705ac";
  const STORAGE_KEY = "law-mock-tests:legacy-unlocked:v1";

  const scriptUrl = document.currentScript?.src || window.location.href;
  const homeUrl = new URL("./", scriptUrl).href;

  function isUnlocked() {
    try {
      return sessionStorage.getItem(STORAGE_KEY) === "1";
    } catch {
      return false;
    }
  }

  if (isUnlocked()) return;

  document.documentElement.classList.add("legacy-lock-pending");

  const style = document.createElement("style");
  style.id = "legacy-gate-style";
  style.textContent = `
    html.legacy-lock-pending body > *:not(#legacy-password-gate) {
      visibility: hidden !important;
      pointer-events: none !important;
      user-select: none !important;
    }

    #legacy-password-gate {
      --gate-bg: #08111f;
      --gate-deep: #050a12;
      --gate-text: #f4f5f8;
      --gate-muted: #99a3b6;
      --gate-gold: #e6bf78;
      --gate-violet: #ae91ff;

      position: fixed;
      inset: 0;
      z-index: 2147483647;

      visibility: visible !important;

      display: grid;
      place-items: center;

      min-height: 100dvh;
      padding: 24px;

      color: var(--gate-text);

      font-family:
        "DM Sans",
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

      background:
        radial-gradient(
          circle at 18% 18%,
          rgba(131, 183, 255, 0.14),
          transparent 34%
        ),
        radial-gradient(
          circle at 82% 72%,
          rgba(174, 145, 255, 0.13),
          transparent 34%
        ),
        linear-gradient(
          145deg,
          rgba(11, 23, 40, 0.98),
          rgba(8, 17, 31, 0.99) 48%,
          rgba(5, 10, 18, 1)
        );

      transition:
        opacity 0.28s ease,
        visibility 0.28s ease;
    }

    #legacy-password-gate.is-leaving {
      opacity: 0;
      visibility: hidden !important;
    }

    #legacy-password-gate .legacy-gate-card {
      width: min(460px, 100%);

      padding: 34px;

      border: 1px solid rgba(255, 255, 255, 0.13);
      border-radius: 26px;

      background:
        linear-gradient(
          145deg,
          rgba(255, 255, 255, 0.075),
          rgba(255, 255, 255, 0.028)
        );

      box-shadow:
        0 35px 110px rgba(0, 0, 0, 0.48),
        0 0 70px rgba(174, 145, 255, 0.05);

      backdrop-filter: blur(22px);
      -webkit-backdrop-filter: blur(22px);
    }

    #legacy-password-gate .legacy-gate-icon {
      width: 52px;
      height: 52px;

      display: grid;
      place-items: center;

      margin-bottom: 28px;

      border: 1px solid rgba(230, 191, 120, 0.30);
      border-radius: 16px;

      color: var(--gate-gold);
      background: rgba(230, 191, 120, 0.07);
    }

    #legacy-password-gate .legacy-gate-icon svg {
      width: 24px;
      height: 24px;
    }

    #legacy-password-gate .legacy-gate-eyebrow {
      margin-bottom: 11px;

      color: var(--gate-violet);

      font-size: 11px;
      font-weight: 700;

      letter-spacing: 0.17em;
      text-transform: uppercase;
    }

    #legacy-password-gate h1 {
      margin: 0 0 13px;

      color: var(--gate-text);

      font-family:
        "Playfair Display",
        Georgia,
        serif;

      font-size: clamp(34px, 8vw, 46px);
      font-weight: 500;
      line-height: 1.06;
      letter-spacing: -0.035em;
    }

    #legacy-password-gate .legacy-gate-copy {
      margin: 0 0 28px;

      color: var(--gate-muted);

      font-size: 14px;
      line-height: 1.65;
    }

    #legacy-password-gate form {
      display: grid;
      gap: 12px;
    }

    #legacy-password-gate label {
      color: #c5cbd5;

      font-size: 12px;
      font-weight: 600;

      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    #legacy-password-gate input {
      width: 100%;
      height: 52px;

      padding: 0 16px;

      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 14px;

      outline: none;

      color: var(--gate-text);
      background: rgba(5, 10, 18, 0.62);

      font: inherit;

      transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease;
    }

    #legacy-password-gate input:focus {
      border-color: rgba(174, 145, 255, 0.60);
      box-shadow: 0 0 0 4px rgba(174, 145, 255, 0.08);
    }

    #legacy-password-gate button {
      height: 52px;

      border: 1px solid rgba(174, 145, 255, 0.42);
      border-radius: 14px;

      cursor: pointer;

      color: #f6f1ff;
      background:
        linear-gradient(
          135deg,
          rgba(174, 145, 255, 0.22),
          rgba(174, 145, 255, 0.10)
        );

      font: inherit;
      font-size: 13px;
      font-weight: 700;

      letter-spacing: 0.07em;
      text-transform: uppercase;

      transition:
        transform 0.2s ease,
        background 0.2s ease,
        border-color 0.2s ease;
    }

    #legacy-password-gate button:hover {
      transform: translateY(-1px);
      border-color: rgba(174, 145, 255, 0.68);
      background:
        linear-gradient(
          135deg,
          rgba(174, 145, 255, 0.30),
          rgba(174, 145, 255, 0.14)
        );
    }

    #legacy-password-gate .legacy-gate-error {
      min-height: 20px;
      margin: 2px 0 0;

      color: #ff8094;

      font-size: 12px;
      line-height: 1.45;
    }

    #legacy-password-gate .legacy-gate-back {
      display: inline-block;

      margin-top: 22px;

      color: #7f8aa0;

      text-decoration: none;

      font-size: 12px;

      transition: color 0.2s ease;
    }

    #legacy-password-gate .legacy-gate-back:hover {
      color: white;
    }
  `;
  document.head.appendChild(style);

  async function sha256(value) {
    const data = new TextEncoder().encode(value);
    const digest = await crypto.subtle.digest("SHA-256", data);

    return Array.from(new Uint8Array(digest))
      .map(byte => byte.toString(16).padStart(2, "0"))
      .join("");
  }

  function subjectName() {
    const path = window.location.pathname.toLowerCase();

    if (path.includes("/civil-procedure/")) {
      return "Civil Procedure Law";
    }

    if (path.includes("/philosophy-of-law/")) {
      return "Philosophy of Law";
    }

    return "Archived module";
  }

  function createGate() {
    const gate = document.createElement("div");
    gate.id = "legacy-password-gate";

    gate.innerHTML = `
      <section class="legacy-gate-card" aria-labelledby="legacy-gate-title">
        <div class="legacy-gate-icon" aria-hidden="true">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.7"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect x="4" y="10" width="16" height="11" rx="2"></rect>
            <path d="M8 10V7a4 4 0 0 1 8 0v3"></path>
          </svg>
        </div>

        <div class="legacy-gate-eyebrow">
          Archived study module
        </div>

        <h1 id="legacy-gate-title">
          ${subjectName()}
        </h1>

        <p class="legacy-gate-copy">
          This older study project is kept as an archive.
          Enter the password to continue.
        </p>

        <form id="legacy-gate-form">
          <label for="legacy-gate-password">
            Password
          </label>

          <input
            id="legacy-gate-password"
            name="password"
            type="password"
            autocomplete="current-password"
            spellcheck="false"
            autofocus
            required
          >

          <button type="submit">
            Unlock archive
          </button>

          <p
            class="legacy-gate-error"
            id="legacy-gate-error"
            aria-live="polite"
          ></p>
        </form>

        <a
          class="legacy-gate-back"
          href="${homeUrl}"
        >
          ← Back to Law Mock Tests
        </a>
      </section>
    `;

    document.body.appendChild(gate);

    const form = gate.querySelector("#legacy-gate-form");
    const input = gate.querySelector("#legacy-gate-password");
    const error = gate.querySelector("#legacy-gate-error");

    form.addEventListener("submit", async event => {
      event.preventDefault();

      error.textContent = "";

      const candidateHash = await sha256(input.value);

      if (candidateHash !== PASSWORD_HASH) {
        error.textContent = "Incorrect password.";
        input.value = "";
        input.focus();
        return;
      }

      try {
        sessionStorage.setItem(STORAGE_KEY, "1");
      } catch {
        // The page still unlocks even if browser storage is unavailable.
      }

      gate.classList.add("is-leaving");

      window.setTimeout(() => {
        document.documentElement.classList.remove("legacy-lock-pending");
        gate.remove();
        document.getElementById("legacy-gate-style")?.remove();
      }, 280);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", createGate, { once: true });
  } else {
    createGate();
  }
})();
