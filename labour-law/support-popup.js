(() => {
  const PIX_KEY = "millena@usp.br";

  const SUPPORT_STATE_KEY =
    "law-mock-tests:support-popup:v4";

  const LABOUR_REVIEW_PAGES = new Set([
    "aviso-previo.html",
    "contribuicao-confederativa.html",
    "contribuicao-sindical.html",
    "convencao-acordo-coletivo.html",
    "mensalidade-sindical.html"
  ]);


  function readSupportState(){

    try{

      return JSON.parse(
        localStorage.getItem(
          SUPPORT_STATE_KEY
        )
      ) || {};

    }catch(error){

      return {};

    }

  }


  function hasSeenSupport(slot){

    return Boolean(
      readSupportState()[slot]
    );

  }


  function markSupportSeen(slot){

    const state =
      readSupportState();

    state[slot] = true;

    localStorage.setItem(
      SUPPORT_STATE_KEY,
      JSON.stringify(state)
    );

  }


  function getSupportContext(){

    const pathname =
      window.location.pathname;

    const filename =
      pathname.split("/").pop()
      || "index.html";


    if(
      pathname.includes(
        "/labour-law/"
      )
    ){

      if(
        LABOUR_REVIEW_PAGES.has(
          filename
        )
      ){
        return "labour";
      }

      return "none";
    }


    return "root";

  }

  const markup = `
    <div
      class="support-popup-overlay"
      id="supportPopupOverlay"
      aria-hidden="true"
    >

      <section
        class="support-popup"
        id="supportPopup"
        role="dialog"
        aria-modal="true"
        aria-labelledby="supportPopupTitle"
      >

        <div
          class="support-popup-stars"
          aria-hidden="true"
        ></div>

        <button
          class="support-popup-close"
          id="supportPopupClose"
          type="button"
          aria-label="Fechar"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.6"
            stroke-linecap="round"
          >
            <path d="M6 6l12 12"/>
            <path d="M18 6L6 18"/>
          </svg>
        </button>


        <div
          class="support-popup-art"
          aria-hidden="true"
        >

          <div class="support-cat">

            <span class="support-zzz support-z1">Z</span>
            <span class="support-zzz support-z2">z</span>

            <svg
              viewBox="0 0 200 200"
              aria-hidden="true"
            >
              <defs>

                <radialGradient
                  id="supportEyeIris"
                  cx="50%"
                  cy="42%"
                  r="65%"
                >
                  <stop
                    offset="0%"
                    stop-color="#fffdf2"
                  />

                  <stop
                    offset="42%"
                    stop-color="#f7ecbe"
                  />

                  <stop
                    offset="100%"
                    stop-color="#c99b25"
                  />
                </radialGradient>

                <radialGradient
                  id="supportRugGlow"
                  cx="50%"
                  cy="50%"
                  r="50%"
                >
                  <stop
                    offset="0%"
                    stop-color="#ae91ff"
                    stop-opacity=".10"
                  />

                  <stop
                    offset="100%"
                    stop-color="#ae91ff"
                    stop-opacity="0"
                  />
                </radialGradient>

              </defs>


              <ellipse
                cx="100"
                cy="158"
                rx="84"
                ry="26"
                fill="url(#supportRugGlow)"
              />

              <ellipse
                cx="100"
                cy="160"
                rx="70"
                ry="15"
                fill="#080d17"
                stroke="#e6bf78"
                stroke-opacity=".32"
                stroke-width=".7"
                stroke-dasharray="2 5"
              />


              <g class="support-cat-body">

                <path
                  d="
                    M145 145
                    C170 145 175 160 140 160
                    C110 160 80 160 60 155
                  "
                  fill="none"
                  stroke="#121925"
                  stroke-width="14"
                  stroke-linecap="round"
                />

                <ellipse
                  cx="100"
                  cy="135"
                  rx="45"
                  ry="30"
                  fill="#111925"
                />

                <path
                  d="M65 125 Q100 100 135 125"
                  fill="none"
                  stroke="#222c3b"
                  stroke-width="2"
                  opacity=".6"
                />

                <ellipse
                  cx="80"
                  cy="155"
                  rx="12"
                  ry="6"
                  fill="#0d131d"
                />

                <ellipse
                  cx="105"
                  cy="155"
                  rx="12"
                  ry="6"
                  fill="#0d131d"
                />


                <g class="support-cat-head">

                  <path
                    d="M75 90 L65 60 L90 82 Z"
                    fill="#111925"
                  />

                  <path
                    d="M115 90 L125 60 L100 82 Z"
                    fill="#111925"
                  />

                  <circle
                    cx="95"
                    cy="105"
                    r="28"
                    fill="#111925"
                  />


                  <g class="support-eyes-closed">

                    <path
                      d="M81 110 Q88 113 95 110"
                      fill="none"
                      stroke="#e6bf78"
                      stroke-width="1.4"
                      stroke-linecap="round"
                      opacity=".72"
                    />

                    <path
                      d="M103 110 Q110 113 117 110"
                      fill="none"
                      stroke="#e6bf78"
                      stroke-width="1.4"
                      stroke-linecap="round"
                      opacity=".72"
                    />

                  </g>


                  <g class="support-eyes-open">

                    <path
                      d="
                        M80.5 110
                        Q88 105.5 95.5 110
                        Q88 114.5 80.5 110 Z
                      "
                      fill="url(#supportEyeIris)"
                    />

                    <ellipse
                      cx="88"
                      cy="110"
                      rx="1.1"
                      ry="3"
                      fill="#050811"
                    />

                    <circle
                      cx="86.4"
                      cy="108.2"
                      r="1"
                      fill="#fff"
                    />


                    <path
                      d="
                        M102.5 110
                        Q110 105.5 117.5 110
                        Q110 114.5 102.5 110 Z
                      "
                      fill="url(#supportEyeIris)"
                    />

                    <ellipse
                      cx="110"
                      cy="110"
                      rx="1.1"
                      ry="3"
                      fill="#050811"
                    />

                    <circle
                      cx="108.4"
                      cy="108.2"
                      r="1"
                      fill="#fff"
                    />

                  </g>


                  <polygon
                    points="97,118 101,118 99,121"
                    fill="#586171"
                    opacity=".55"
                  />

                  <path
                    d="
                      M99 90
                      l1.8 4
                      4 1.8
                      -4 1.8
                      -1.8 4
                      -1.8 -4
                      -4 -1.8
                      4 -1.8 Z
                    "
                    fill="#e6bf78"
                    opacity=".47"
                  />

                </g>

              </g>

            </svg>

          </div>


          <div class="support-cup" aria-hidden="true">
            <svg viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="supportTeacupBody" x1="20" y1="40" x2="88" y2="89" gradientUnits="userSpaceOnUse">
                  <stop stop-color="#3a3545"/>
                  <stop offset=".45" stop-color="#1d2538"/>
                  <stop offset="1" stop-color="#0b1425"/>
                </linearGradient>
                <linearGradient id="supportTeacupRim" x1="25" y1="45" x2="91" y2="58" gradientUnits="userSpaceOnUse">
                  <stop stop-color="#f3dcaa"/>
                  <stop offset=".5" stop-color="#9e7640"/>
                  <stop offset="1" stop-color="#e7c687"/>
                </linearGradient>
              </defs>
              <ellipse cx="59" cy="106" rx="41" ry="5" fill="#02070c" opacity=".47"/>
              <g class="support-steam support-steam-one">
                <path d="M43 46 C32 33 52 29 42 13" stroke="#edddb7" stroke-width="1.7" stroke-linecap="round"/>
              </g>
              <g class="support-steam support-steam-two">
                <path d="M60 44 C72 32 49 28 63 10" stroke="#e8d6b2" stroke-width="1.7" stroke-linecap="round"/>
              </g>
              <g class="support-steam support-steam-three">
                <path d="M76 46 C65 35 85 30 78 18" stroke="#ead2a4" stroke-width="1.4" stroke-linecap="round"/>
              </g>
              <ellipse cx="56" cy="99" rx="39" ry="6" fill="#111b2d" stroke="#b58c55" stroke-width="1.2"/>
              <path d="M23 98 Q56 104 91 98" stroke="#e6c78b" stroke-width=".8" opacity=".75"/>
              <path d="M85 55 C108 43 115 71 98 81 C94 84 89 83 82 80" stroke="url(#supportTeacupRim)" stroke-width="5" stroke-linecap="round"/>
              <path d="M86 58 C101 52 105 70 95 75" stroke="#141c2a" stroke-width="2.5" stroke-linecap="round"/>
              <path d="M23 50 H88 C86 77 77 89 56 89 C35 89 25 76 23 50 Z" fill="url(#supportTeacupBody)" stroke="#d4ad6e" stroke-width="1.5"/>
              <path d="M28 60 C34 83 46 85 55 85" stroke="#f7e2b9" stroke-width="1.1" stroke-linecap="round" opacity=".29"/>
              <path d="M48 66 C50 61 55 60 58 66 C61 71 66 71 68 66 M47 71 C52 76 62 76 68 71" stroke="#c5a066" stroke-width="1" stroke-linecap="round" opacity=".8"/>
              <ellipse cx="55.5" cy="50" rx="32.5" ry="7.5" fill="#151723" stroke="url(#supportTeacupRim)" stroke-width="1.8"/>
              <ellipse cx="55.5" cy="50.5" rx="28.5" ry="4.2" fill="#6e4630" opacity=".75"/>
              <path d="M31 49 C42 45 68 45 79 49" stroke="#d5ae76" stroke-width=".8" opacity=".65"/>
              <path d="M47 89 H66 L70 94 H43 Z" fill="#131d2e" stroke="#be965f" stroke-width="1"/>
            </svg>
          </div>

        </div>


        <div class="support-popup-copy">

          <div class="support-popup-kicker">
            Law Mock Tests
          </div>

          <h2 id="supportPopupTitle">
            Buy me a tea.
          </h2>

          <p>
            Eu sou <strong>Millena Franco</strong>
            e organizei este banco de questões.
            Se ele for útil para você e quiser
            contribuir, minha chave Pix é:
          </p>

          <button
            class="support-pix"
            id="supportPixButton"
            type="button"
          >

            <span>
              millena@usp.br
            </span>

            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
            >
              <rect
                x="9"
                y="9"
                width="12"
                height="12"
                rx="2"
              />

              <path
                d="
                  M5 15H4
                  a2 2 0 0 1-2-2
                  V4
                  a2 2 0 0 1 2-2
                  h9
                  a2 2 0 0 1 2 2
                  v1
                "
              />
            </svg>

            <span
              class="support-copy-status"
              id="supportCopyStatus"
            >
              Copiado
            </span>

          </button>

          <p class="support-thanks">
            Obrigada <span>♥</span>
          </p>




        </div>

      </section>


      <div class="support-popup-hint">
        Clique fora para fechar · Esc
      </div>

    </div>
  `;


  function initSupportPopup(){

    if(
      document.getElementById(
        "supportPopupOverlay"
      )
    ){
      return;
    }


    document.body.insertAdjacentHTML(
      "beforeend",
      markup
    );


    const overlay =
      document.getElementById(
        "supportPopupOverlay"
      );

    const dialog =
      document.getElementById(
        "supportPopup"
      );

    const closeButton =
      document.getElementById(
        "supportPopupClose"
      );

    const pixButton =
      document.getElementById(
        "supportPixButton"
      );

    const copyStatus =
      document.getElementById(
        "supportCopyStatus"
      );


    function restartAnimations(){

      const animated =
        dialog.querySelectorAll(
          [
            ".support-cat-body",
            ".support-cat-head",
            ".support-eyes-open",
            ".support-eyes-closed",
            ".support-zzz"
          ].join(",")
        );

      animated.forEach(el => {
        el.style.animation = "none";
      });

      void dialog.offsetWidth;

      animated.forEach(el => {
        el.style.animation = "";
      });

    }


    function openPopup(){

      restartAnimations();

      overlay.classList.add(
        "is-open"
      );

      overlay.setAttribute(
        "aria-hidden",
        "false"
      );

      document.body.classList.add(
        "support-popup-open"
      );

    }


    function closePopup(){

      overlay.classList.remove(
        "is-open"
      );

      overlay.setAttribute(
        "aria-hidden",
        "true"
      );

      document.body.classList.remove(
        "support-popup-open"
      );

    }


    closeButton.addEventListener(
      "click",
      closePopup
    );


    overlay.addEventListener(
      "click",
      event => {

        if(
          event.target === overlay
        ){
          closePopup();
        }

      }
    );


    document.addEventListener(
      "keydown",
      event => {

        if(
          event.key === "Escape" &&
          overlay.classList.contains(
            "is-open"
          )
        ){
          closePopup();
        }

      }
    );


    pixButton.addEventListener(
      "click",
      async () => {

        try{

          await navigator.clipboard.writeText(
            PIX_KEY
          );

        }catch(error){

          const textarea =
            document.createElement(
              "textarea"
            );

          textarea.value =
            PIX_KEY;

          textarea.style.position =
            "fixed";

          textarea.style.opacity =
            "0";

          document.body.appendChild(
            textarea
          );

          textarea.select();

          document.execCommand(
            "copy"
          );

          textarea.remove();

        }


        copyStatus.classList.add(
          "show"
        );

        setTimeout(
          () => {
            copyStatus.classList.remove(
              "show"
            );
          },
          1500
        );

      }
    );



    /* =====================================================
       PERMANENT, DISCREET SUPPORT NOTE
       ===================================================== */

    function installSupportFootnote(){

      const footer =
        document.querySelector(
          "footer.refs"
        )
        ||
        document.querySelector(
          ".page > footer"
        )
        ||
        document.querySelector(
          ".shell > footer"
        )
        ||
        document.querySelector(
          "body > footer"
        );


      if(
        !footer ||
        footer.querySelector(
          ".support-footnote"
        )
      ){
        return;
      }


      const note =
        document.createElement(
          "div"
        );

      note.className =
        "support-footnote";

      note.innerHTML = `
        <span>Gostou do projeto?</span>

        <button
          class="support-footnote-open"
          type="button"
        >
          Buy me a tea
        </button>

        <span
          class="support-footnote-separator"
          aria-hidden="true"
        >
          ·
        </span>

        <span>
          Pix:
          <strong>${PIX_KEY}</strong>
        </span>
      `;


      footer.appendChild(
        note
      );


      note
        .querySelector(
          ".support-footnote-open"
        )
        .addEventListener(
          "click",
          openPopup
        );

    }


    installSupportFootnote();


    /* =====================================================
       SUPPORT POPUP LIFECYCLE · V4

       Automatic appearances:

       1. First visit to the ROOT index
       2. First visit to ANY Labour Law review bank
       3. First click on "Resultado"
       4. EVERY successful restart
       ===================================================== */

    const context =
      getSupportContext();


    /* -----------------------------------------------------
       1 · ROOT INDEX
       Only once per browser.
       ----------------------------------------------------- */

    if(
      context === "root" &&
      !hasSeenSupport(
        "rootIndex"
      )
    ){

      markSupportSeen(
        "rootIndex"
      );

      openPopup();

    }


    /* -----------------------------------------------------
       2 · FIRST REVIEW BANK
       Any of the five Labour Law HTML pages.
       Only one appearance total.
       ----------------------------------------------------- */

    if(
      context === "labour" &&
      !hasSeenSupport(
        "firstReviewBank"
      )
    ){

      markSupportSeen(
        "firstReviewBank"
      );

      openPopup();

    }


    /* -----------------------------------------------------
       3 · FIRST CLICK ON "RESULTADO"
       Does not require 100% completion.
       Only once across all five banks.
       ----------------------------------------------------- */

    const finishButton =
      document.getElementById(
        "finishBtn"
      );


    if(finishButton){

      finishButton.addEventListener(
        "click",
        () => {

          if(
            hasSeenSupport(
              "firstResult"
            )
          ){
            return;
          }


          markSupportSeen(
            "firstResult"
          );


          /*
            Small delay so the result screen appears
            underneath the modal first.
          */

          setTimeout(
            openPopup,
            100
          );

        }
      );

    }


    /* -----------------------------------------------------
       4 · EVERY SUCCESSFUL RESTART

       This one is intentionally NOT stored.

       Some review banks use confirm() before restarting.
       Therefore we wait for their own restart code to run
       and verify that the result screen actually closed and
       progress returned to zero.

       If the user cancels confirm(), no popup appears.
       ----------------------------------------------------- */

    const restartButton =
      document.getElementById(
        "restartBtn"
      );


    if(restartButton){

      restartButton.addEventListener(
        "click",
        () => {

          setTimeout(
            () => {

              const result =
                document.getElementById(
                  "result"
                );

              const progressText =
                document.getElementById(
                  "progressText"
                );


              const resultClosed =
                !result ||
                !result.classList.contains(
                  "show"
                );


              const restarted =
                progressText &&
                progressText.textContent
                  .trim()
                  .startsWith("0%");


              if(
                resultClosed &&
                restarted
              ){
                openPopup();
              }

            },
            150
          );

        }
      );

    }


    /*
      Small developer API for testing.
      It does not affect normal visitors.
    */

    window.SupportPopup = {

      open:
        openPopup,

      state:
        () => readSupportState(),

      reset:
        () => {

          localStorage.removeItem(
            SUPPORT_STATE_KEY
          );

          location.reload();

        }

    };
  }


  if(
    document.readyState === "loading"
  ){

    document.addEventListener(
      "DOMContentLoaded",
      initSupportPopup,
      { once:true }
    );

  }else{

    initSupportPopup();

  }

})();
