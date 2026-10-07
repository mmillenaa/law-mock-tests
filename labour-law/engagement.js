(() => {

  const API =
    "/api/engagement";

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

    if(
      window.crypto?.randomUUID
    ){
      return crypto.randomUUID();
    }

    return (
      Date.now().toString(36)
      + "-"
      + Math.random()
          .toString(36)
          .slice(2)
    );

  }


  function visitorId(){

    let id =
      localStorage.getItem(
        VISITOR_KEY
      );

    if(!id){

      id = randomId();

      localStorage.setItem(
        VISITOR_KEY,
        id
      );

    }

    return id;

  }


  function currentFilename(){

    return (
      location.pathname
        .split("/")
        .pop()
      || "index.html"
    );

  }


  function currentBank(){

    return (
      BANKS[currentFilename()]
      || null
    );

  }


  function isLabourArea(){

    return location.pathname
      .includes(
        "/labour-law/"
      );

  }


  function attemptKey(bank){

    return (
      "law-mock-tests:attempt:"
      + bank
    );

  }


  function currentAttempt(bank){

    const key =
      attemptKey(bank);

    let id =
      localStorage.getItem(
        key
      );

    if(!id){

      id = randomId();

      localStorage.setItem(
        key,
        id
      );

    }

    return id;

  }


  function newAttempt(bank){

    const id =
      randomId();

    localStorage.setItem(
      attemptKey(bank),
      id
    );

    return id;

  }


  async function post(data){

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
            JSON.stringify(data)
        }
      );

    if(!response.ok){
      throw new Error(
        "Engagement API "
        + response.status
      );
    }

    return response.json();

  }


  async function getStats(bank = null){

    const params =
      new URLSearchParams({
        visitor:
          visitorId()
      });


    if(bank){
      params.set(
        "bank",
        bank
      );
    }


    const response =
      await fetch(
        API
        + "?"
        + params.toString(),
        {
          cache:"no-store"
        }
      );


    if(!response.ok){
      throw new Error(
        "Stats unavailable"
      );
    }


    return response.json();

  }


  function compact(value){

    return new Intl.NumberFormat(
      "pt-BR",
      {
        notation:
          value >= 10000
            ? "compact"
            : "standard",

        maximumFractionDigits:1
      }
    ).format(
      Number(value || 0)
    );

  }


  function stripMarkup(){

    return `
      <span class="engagement-stat">
        <span aria-hidden="true">◉</span>

        <strong data-engagement="views">
          0
        </strong>

        <span>visualizações</span>
      </span>


      <span class="engagement-stat engagement-heart">
        <span aria-hidden="true">♥</span>

        <strong data-engagement="likes">
          0
        </strong>

        <span>curtidas</span>
      </span>


      <span class="engagement-stat engagement-complete">
        <span aria-hidden="true">✓</span>

        <strong data-engagement="completions">
          0
        </strong>

        <span>finalizações</span>
      </span>


      <span class="engagement-stat engagement-feedback">
        <span aria-hidden="true">⚑</span>

        <strong data-engagement="feedbacks">
          0
        </strong>

        <span>feedbacks</span>
      </span>
    `;

  }


  function installPublicStats(){

    /*
      ROOT INDEX:
      metrics inside the Labour Law card.
    */

    const labourCard =
      document.querySelector(
        ".card.labour .card-content"
      );


    if(
      labourCard &&
      !labourCard.querySelector(
        ".engagement-strip"
      )
    ){

      const footer =
        labourCard.querySelector(
          ".card-footer"
        );

      const strip =
        document.createElement(
          "div"
        );

      strip.className =
        "engagement-strip engagement-strip--card";

      strip.innerHTML =
        stripMarkup();


      if(footer){

        labourCard.insertBefore(
          strip,
          footer
        );

      }else{

        labourCard.appendChild(
          strip
        );

      }

    }


    /*
      LABOUR LAW INDEX:
      metrics immediately under introduction.
    */

    const isLabourIndex =
      isLabourArea()
      &&
      !currentBank();


    if(isLabourIndex){

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
          stripMarkup();

        lead.insertAdjacentElement(
          "afterend",
          strip
        );

      }

    }

  }


  function renderStats(stats){

    document
      .querySelectorAll(
        '[data-engagement="views"]'
      )
      .forEach(el => {
        el.textContent =
          compact(stats.views);
      });


    document
      .querySelectorAll(
        '[data-engagement="likes"]'
      )
      .forEach(el => {
        el.textContent =
          compact(stats.likes);
      });


    document
      .querySelectorAll(
        '[data-engagement="completions"]'
      )
      .forEach(el => {
        el.textContent =
          compact(
            stats.completions
          );
      });


    document
      .querySelectorAll(
        '[data-engagement="feedbacks"]'
      )
      .forEach(el => {
        el.textContent =
          compact(
            stats.feedbacks
          );
      });

  }


  async function refreshStats(){

    try{

      const data =
        await getStats(
          currentBank()
        );

      renderStats(data);

      return data;

    }catch(error){

      console.warn(
        "Engagement:",
        error
      );

      return null;

    }

  }


  async function registerView(){

    /*
      The root homepage only DISPLAYS Labour Law stats.
      It does not count as a Labour Law view.

      Labour index + the five banks do.
    */

    if(!isLabourArea()){
      return;
    }


    try{

      const data =
        await post({
          action:"view",

          visitorId:
            visitorId(),

          bank:
            currentBank()
        });

      renderStats(data);

    }catch(error){

      console.warn(
        "View counter:",
        error
      );

    }

  }


  function installLikeButton(){

    const bank =
      currentBank();

    if(!bank){
      return;
    }


    const hero =
      document.querySelector(
        ".hero"
      );


    if(
      !hero ||
      document.getElementById(
        "engagementLikeButton"
      )
    ){
      return;
    }


    const wrap =
      document.createElement(
        "div"
      );

    wrap.className =
      "bank-like-wrap";


    const button =
      document.createElement(
        "button"
      );

    button.type =
      "button";

    button.id =
      "engagementLikeButton";

    button.className =
      "bank-like-btn";

    button.innerHTML = `
      <span
        class="heart"
        aria-hidden="true"
      >
        ♡
      </span>

      <span class="label">
        Curtir este banco
      </span>
    `;


    wrap.appendChild(
      button
    );


    hero.insertAdjacentElement(
      "afterend",
      wrap
    );


    function paint(liked){

      button.classList.toggle(
        "is-liked",
        liked
      );

      button.querySelector(
        ".heart"
      ).textContent =
        liked
          ? "♥"
          : "♡";

      button.querySelector(
        ".label"
      ).textContent =
        liked
          ? "Curtido"
          : "Curtir este banco";

      button.setAttribute(
        "aria-pressed",
        liked
          ? "true"
          : "false"
      );

    }


    getStats(bank)
      .then(data => {

        paint(
          Boolean(data.liked)
        );

        renderStats(data);

      })
      .catch(() => {});


    button.addEventListener(
      "click",
      async () => {

        button.disabled =
          true;

        try{

          const data =
            await post({
              action:
                "toggle_like",

              bank,

              visitorId:
                visitorId()
            });


          paint(
            Boolean(data.liked)
          );

          renderStats(data);

        }catch(error){

          console.warn(
            "Like:",
            error
          );

        }finally{

          button.disabled =
            false;

        }

      }
    );

  }


  function installCompletionTracking(){

    const bank =
      currentBank();

    if(!bank){
      return;
    }


    currentAttempt(bank);


    const finish =
      document.getElementById(
        "finishBtn"
      );


    if(finish){

      finish.addEventListener(
        "click",
        () => {

          setTimeout(
            async () => {

              const progress =
                document.getElementById(
                  "progressText"
                );


              if(
                !progress ||
                !progress.textContent
                  .trim()
                  .startsWith("100%")
              ){
                return;
              }


              try{

                const data =
                  await post({
                    action:
                      "completion",

                    bank,

                    visitorId:
                      visitorId(),

                    attemptId:
                      currentAttempt(
                        bank
                      )
                  });


                renderStats(data);

              }catch(error){

                console.warn(
                  "Completion:",
                  error
                );

              }

            },
            180
          );

        }
      );

    }


    const restart =
      document.getElementById(
        "restartBtn"
      );


    if(restart){

      restart.addEventListener(
        "click",
        () => {

          /*
            Wait for the bank's own restart
            handler. If the user cancelled
            confirm(), result remains open.
          */

          setTimeout(
            () => {

              const result =
                document.getElementById(
                  "result"
                );

              const progress =
                document.getElementById(
                  "progressText"
                );


              const restarted =
                progress
                &&
                progress.textContent
                  .trim()
                  .startsWith("0%");


              const resultClosed =
                !result
                ||
                !result.classList
                  .contains("show");


              if(
                restarted &&
                resultClosed
              ){
                newAttempt(bank);
              }

            },
            220
          );

        }
      );

    }

  }


  async function init(){

    installPublicStats();

    installLikeButton();

    installCompletionTracking();


    await registerView();

    await refreshStats();


    /*
      Only pages that visibly show the counters
      need periodic refresh.
    */

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
      {
        once:true
      }
    );

  }else{

    init();

  }

})();
