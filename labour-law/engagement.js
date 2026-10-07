(() => {

  const API =
    "/api/engagement";

  const SCOPE =
    "labour-law";

  const VISITOR_KEY =
    "law-mock-tests:visitor:v1";


  const BANKS = {

    "convencao-acordo-coletivo.html":
      "convencao-acordo-coletivo",

    "contribuicao-sindical.html":
      "contribuicao-sindical",

    "contribuicao-confederativa.html":
      "contribuicao-confederativa",

    "mensalidade-sindical.html":
      "mensalidade-sindical",

    "aviso-previo.html":
      "aviso-previo"

  };


  function randomId(){

    return (
      crypto.randomUUID?.()
      ||
      (
        Date.now().toString(36)
        + "-"
        + Math.random()
          .toString(36)
          .slice(2)
      )
    );

  }


  function visitorId(){

    let id =
      localStorage.getItem(
        VISITOR_KEY
      );

    if(!id){

      id =
        randomId();

      localStorage.setItem(
        VISITOR_KEY,
        id
      );

    }

    return id;

  }


  function filename(){

    return (
      location.pathname
        .split("/")
        .pop()
      || "index.html"
    );

  }


  function currentBank(){

    return (
      BANKS[filename()]
      || null
    );

  }


  function inLabour(){

    return location.pathname
      .includes(
        "/labour-law/"
      );

  }


  function pageScope(){

    /*
      A home apenas exibe o agregado de Labour Law.
      Ela não possui um contador global próprio.
    */

    return SCOPE;

  }


  async function post(body){

    const response =
      await fetch(
        API,
        {
          method:"POST",

          headers:{
            "content-type":
              "application/json"
          },

          body:
            JSON.stringify(body)
        }
      );


    if(!response.ok){

      throw new Error(
        "API "
        + response.status
      );

    }


    return response.json();

  }


  async function get(params = {}){

    const query =
      new URLSearchParams(
        params
      );


    const response =
      await fetch(
        API
        + "?"
        + query.toString(),
        {
          cache:"no-store"
        }
      );


    if(!response.ok){

      throw new Error(
        "API "
        + response.status
      );

    }


    return response.json();

  }


  function format(value){

    return new Intl.NumberFormat(
      "pt-BR"
    ).format(
      Number(value || 0)
    );

  }


  function stripMarkup(
    rankingLink = false
  ){

    const likes =
      rankingLink

        ? `
          <a
            class="
              engagement-stat
              engagement-stat-link
              engagement-heart
            "
            href="./mais-curtidas.html"
            target="_blank"
            rel="noopener"
            title="Ver questões mais curtidas"
          >
            <span>♥</span>
            <strong
              data-engagement="likes"
            >0</strong>
            <span>curtidas</span>
          </a>
        `

        : `
          <span
            class="
              engagement-stat
              engagement-heart
            "
          >
            <span>♥</span>
            <strong
              data-engagement="likes"
            >0</strong>
            <span>curtidas</span>
          </span>
        `;


    return `
      <span class="engagement-stat">
        <span>◉</span>
        <strong
          data-engagement="views"
        >0</strong>
        <span>visualizações</span>
      </span>

      ${likes}

      <span
        class="
          engagement-stat
          engagement-complete
        "
      >
        <span>✓</span>
        <strong
          data-engagement="completions"
        >0</strong>
        <span>finalizações</span>
      </span>

      <span
        class="
          engagement-stat
          engagement-feedback
        "
      >
        <span>⚑</span>
        <strong
          data-engagement="feedbacks"
        >0</strong>
        <span>feedbacks</span>
      </span>
    `;

  }


  function installCounters(){

    /*
      ROOT INDEX
      Labour Law metrics live inside the Labour Law card.
    */

    if(!inLabour()){

      const labourContent =
        document.querySelector(
          ".card.labour .card-content"
        );

      if(
        labourContent &&
        !labourContent.querySelector(
          ".engagement-strip"
        )
      ){

        const footer =
          labourContent.querySelector(
            ".card-footer"
          );

        const strip =
          document.createElement(
            "div"
          );

        strip.className =
          "engagement-strip engagement-strip--card";

        strip.innerHTML =
          stripMarkup(false);


        if(footer){

          labourContent.insertBefore(
            strip,
            footer
          );

        }else{

          labourContent.appendChild(
            strip
          );

        }

      }

      return;
    }


    /*
      LABOUR LAW INDEX
      Aggregate Labour Law metrics below the introduction.
    */

    if(!currentBank()){

      const lead =
        document.querySelector(
          ".lead"
        );


      if(
        lead &&
        !document.querySelector(
          ".engagement-strip--hero"
        )
      ){

        const strip =
          document.createElement(
            "div"
          );

        strip.className =
          "engagement-strip engagement-strip--hero";

        strip.innerHTML =
          stripMarkup(true);


        lead.insertAdjacentElement(
          "afterend",
          strip
        );

      }

    }

  }


  function renderStats(stats){

    [
      "views",
      "likes",
      "completions",
      "feedbacks"
    ].forEach(key => {

      document
        .querySelectorAll(
          `[data-engagement="${key}"]`
        )
        .forEach(el => {

          el.textContent =
            format(stats[key]);

        });

    });

  }


  async function refreshStats(){

    try{

      const stats =
        await get({
          scope:
            pageScope()
        });


      renderStats(stats);

    }catch(error){

      console.warn(
        "Engagement stats:",
        error
      );

    }

  }


  async function registerView(){

    /*
      The root index only displays Labour Law totals.
      Opening the homepage does not count as a Labour Law view.
    */

    if(!inLabour()){
      return;
    }


    try{

      const data =
        await post({
          action:"view",

          scope:
            pageScope(),

          bank:
            currentBank(),

          visitorId:
            visitorId()
        });


      renderStats(data);

    }catch(error){

      console.warn(
        "View:",
        error
      );

    }

  }


  /* =======================================================
     QUESTION COMMUNITY BAR
     ======================================================= */

  function currentQuestion(){

    const card =
      document.getElementById(
        "quizCard"
      );


    if(!card){
      return null;
    }


    const questionId =
      card.dataset.questionId;


    if(!questionId){
      return null;
    }


    return {
      questionId,

      questionType:
        card.dataset.questionType
        || "",

      section:
        card.dataset.questionSection
        || "",

      prompt:
        card.dataset.questionPrompt
        || ""
    };

  }


  function installQuestionBar(){

    const bank =
      currentBank();

    const card =
      document.getElementById(
        "quizCard"
      );


    if(
      !bank ||
      !card
    ){
      return;
    }


    const qhead =
      card.querySelector(
        ".qhead"
      );


    const badges =
      card.querySelector(
        ".badges"
      )
      ||
      qhead?.lastElementChild;


    if(!badges){
      return;
    }


    /*
      Normalize every review-bank header so the
      question actions always have the same home.
    */
    badges.classList.add(
      "badges"
    );


    const bar =
      document.createElement(
        "div"
      );


    bar.className =
      "question-community-bar";


    bar.innerHTML = `
      <button
        type="button"
        class="question-report-btn"
        id="questionReportBtn"
        title="Deixe um report de comentário, dúvida ou sugestão de melhoria para a questão"
      >
        <span
          class="question-flag"
          aria-hidden="true"
        >⚑</span>

        <span class="question-action-label">
          Reportar
        </span>
      </button>


      <button
        type="button"
        class="question-like-btn"
        id="questionLikeBtn"
        aria-pressed="false"
        title="Curtir esta questão"
      >
        <span
          class="question-heart"
          aria-hidden="true"
        >♡</span>

        <span
          id="questionLikeCount"
          class="question-like-count"
        >0</span>
      </button>
    `;


    badges.appendChild(
      bar
    );


    const likeButton =
      document.getElementById(
        "questionLikeBtn"
      );

    const reportButton =
      document.getElementById(
        "questionReportBtn"
      );


    function paintLike(
      liked,
      count,
      animate = false
    ){

      likeButton.classList.toggle(
        "is-liked",
        liked
      );


      likeButton
        .querySelector(
          ".question-heart"
        )
        .textContent =
          liked
            ? "♥"
            : "♡";


      likeButton.setAttribute(
        "aria-pressed",
        liked
          ? "true"
          : "false"
      );


      document.getElementById(
        "questionLikeCount"
      ).textContent =
        format(count);


      if(
        liked &&
        animate
      ){

        likeButton.classList.remove(
          "just-liked"
        );

        void likeButton.offsetWidth;

        likeButton.classList.add(
          "just-liked"
        );

      }

    }


    async function syncQuestion(){

      const q =
        currentQuestion();


      if(!q){
        return;
      }


      try{

        const data =
          await get({
            scope:SCOPE,
            bank,
            question:
              q.questionId,

            visitor:
              visitorId()
          });


        paintLike(
          Boolean(data.liked),
          data.questionLikes
        );

      }catch(error){

        console.warn(
          "Question likes:",
          error
        );

      }

    }


    likeButton.addEventListener(
      "click",
      async () => {

        const q =
          currentQuestion();


        if(!q){
          return;
        }


        likeButton.disabled =
          true;


        try{

          const data =
            await post({
              action:
                "toggle_question_like",

              scope:SCOPE,
              bank,

              visitorId:
                visitorId(),

              ...q
            });


          paintLike(
            Boolean(data.liked),
            data.questionLikes,
            Boolean(data.liked)
          );


        }catch(error){

          console.warn(
            "Like:",
            error
          );

        }finally{

          likeButton.disabled =
            false;

        }

      }
    );


    reportButton.addEventListener(
      "click",
      () => {

        openReportModal();

      }
    );


    const observer =
      new MutationObserver(
        () => {

          clearTimeout(
            observer.timer
          );


          observer.timer =
            setTimeout(
              syncQuestion,
              80
            );

        }
      );


    observer.observe(
      card,
      {
        attributes:true,

        attributeFilter:[
          "data-question-id"
        ]
      }
    );


    window.addEventListener(
      "law-question-rendered",
      syncQuestion
    );


    syncQuestion();

  }


  /* =======================================================
     REPORT MODAL
     ======================================================= */

  function installReportModal(){

    if(
      document.getElementById(
        "questionReportModal"
      )
    ){
      return;
    }


    document.body.insertAdjacentHTML(
      "beforeend",
      `
        <div
          class="report-modal-overlay"
          id="questionReportModal"
          aria-hidden="true"
        >
          <section
            class="report-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="reportModalTitle"
          >

            <button
              type="button"
              class="report-modal-close"
              id="reportModalClose"
              aria-label="Fechar"
            >
              ×
            </button>

            <div class="report-kicker">
              Feedback da questão
            </div>

            <h2 id="reportModalTitle">
              Reportar uma questão
            </h2>

            <p>
              Deixe um comentário, dúvida ou
              sugestão de melhoria. A questão
              e seu identificador serão
              registrados automaticamente.
            </p>

            <label>
              Tipo de feedback

              <select id="reportCategory">
                <option value="duvida">
                  Dúvida
                </option>

                <option value="gabarito">
                  Possível problema no gabarito
                </option>

                <option value="ambiguidade">
                  Enunciado ambíguo
                </option>

                <option value="conteudo">
                  Possível erro de conteúdo
                </option>

                <option value="tecnico">
                  Problema técnico
                </option>

                <option value="sugestao">
                  Sugestão de melhoria
                </option>

                <option value="outro">
                  Outro
                </option>
              </select>
            </label>

            <label>
              Comentário

              <textarea
                id="reportText"
                rows="5"
                maxlength="4000"
                placeholder="Conte o que você percebeu..."
              ></textarea>
            </label>

            <div class="report-modal-actions">

              <button
                type="button"
                class="report-cancel"
                id="reportCancel"
              >
                Cancelar
              </button>

              <button
                type="button"
                class="report-send"
                id="reportSend"
              >
                Enviar feedback
              </button>

            </div>

            <div
              class="report-status"
              id="reportStatus"
            ></div>

          </section>
        </div>
      `
    );


    const overlay =
      document.getElementById(
        "questionReportModal"
      );


    const close = () => {

      overlay.classList.remove(
        "is-open"
      );

      overlay.setAttribute(
        "aria-hidden",
        "true"
      );

    };


    document.getElementById(
      "reportModalClose"
    ).onclick =
      close;


    document.getElementById(
      "reportCancel"
    ).onclick =
      close;


    overlay.addEventListener(
      "click",
      event => {

        if(
          event.target === overlay
        ){
          close();
        }

      }
    );


    document.getElementById(
      "reportSend"
    ).addEventListener(
      "click",
      async () => {

        const q =
          currentQuestion();

        const reportText =
          document.getElementById(
            "reportText"
          ).value.trim();

        const category =
          document.getElementById(
            "reportCategory"
          ).value;

        const status =
          document.getElementById(
            "reportStatus"
          );


        if(
          !q ||
          !reportText
        ){

          status.textContent =
            "Escreva uma mensagem antes de enviar.";

          return;
        }


        const button =
          document.getElementById(
            "reportSend"
          );


        button.disabled =
          true;

        status.textContent =
          "Enviando…";


        try{

          await post({
            action:"report",
            scope:SCOPE,

            bank:
              currentBank(),

            visitorId:
              visitorId(),

            ...q,

            category,
            reportText
          });


          status.textContent =
            "Feedback enviado. Obrigada ♥";


          document.getElementById(
            "reportText"
          ).value = "";


          setTimeout(
            close,
            1000
          );


        }catch(error){

          status.textContent =
            "Não foi possível enviar agora.";

        }finally{

          button.disabled =
            false;

        }

      }
    );

  }


  function openReportModal(){

    const overlay =
      document.getElementById(
        "questionReportModal"
      );


    if(!overlay){
      return;
    }


    document.getElementById(
      "reportStatus"
    ).textContent = "";


    overlay.classList.add(
      "is-open"
    );


    overlay.setAttribute(
      "aria-hidden",
      "false"
    );

  }


  /* =======================================================
     COMPLETIONS
     ======================================================= */

  function attemptKey(bank){

    return (
      "law-mock-tests:attempt:"
      + bank
    );

  }


  function attemptId(bank){

    let id =
      localStorage.getItem(
        attemptKey(bank)
      );


    if(!id){

      id =
        randomId();

      localStorage.setItem(
        attemptKey(bank),
        id
      );

    }


    return id;

  }


  function installCompletion(){

    const bank =
      currentBank();


    if(!bank){
      return;
    }


    attemptId(bank);


    /*
      Completion is emitted by showResult() itself.
      No text parsing, no progress-bar inference.
    */

    window.addEventListener(
      "law-bank-result",
      async event => {

        if(
          !event.detail ||
          event.detail.complete !== true
        ){
          return;
        }


        try{

          const data =
            await post({
              action:
                "completion",

              scope:
                SCOPE,

              bank,

              visitorId:
                visitorId(),

              attemptId:
                attemptId(bank)
            });


          renderStats(
            data
          );


        }catch(error){

          console.warn(
            "Completion:",
            error
          );

        }

      }
    );


    const restart =
      document.getElementById(
        "restartBtn"
      );


    if(restart){

      restart.addEventListener(
        "click",
        () => {

          setTimeout(
            () => {

              const progress =
                document.getElementById(
                  "progressText"
                );

              const result =
                document.getElementById(
                  "result"
                );


              if(
                progress &&
                progress.textContent
                  .trim()
                  .startsWith("0%")
                &&
                (
                  !result ||
                  !result.classList
                    .contains("show")
                )
              ){

                localStorage.setItem(
                  attemptKey(bank),
                  randomId()
                );

              }

            },
            220
          );

        }
      );

    }

  }


  async function init(){

    if(currentBank()){

      document.body.classList.add(
        "review-bank-page"
      );

    }


    installCounters();

    installReportModal();

    installQuestionBar();

    installCompletion();

    await registerView();

    await refreshStats();


    if(
      document.querySelector(
        ".engagement-strip"
      )
    ){

      setInterval(
        refreshStats,
        45000
      );

    }

  }


  if(
    document.readyState ===
    "loading"
  ){

    document.addEventListener(
      "DOMContentLoaded",
      init,
      { once:true }
    );

  }else{

    init();

  }

})();
