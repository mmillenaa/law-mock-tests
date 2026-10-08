/* Legis Lectiones — resultado automatico e celebracao Constelacao Eterea.
   Compatibilidade: 5 bancos antigos + 4 bancos P2.
   Nao altera gabaritos, status, som de respostas nem os eventos do engagement. */
(() => {
  'use strict';

  const byId = id => document.getElementById(id);
  const result = byId('result');
  const finish = byId('finishBtn');
  const progressBar = byId('progressBar');
  const scoreDetail = byId('scoreDetail');
  if (!result || !finish || !progressBar || !scoreDetail) return;

  const SOUND_URL = new URL('../civil-procedure/win.mp3', document.baseURI).href;
  const AUTO_DELAY_MS = 5000;
  let lastComplete = null;
  let autoTimer = null;
  let celebratedThisAttempt = false;
  let webAudio = null;
  let decodedWin = null;
  let winBufferRequested = false;
  let winAudioElement = null;

  const showingResult = () => result.classList.contains('show');

  function exactScore() {
    // Usa quantidades reais, nao o percentual exibido (que e arredondado).
    const text = scoreDetail.textContent || '';
    const hits = text.match(/\b(\d+)\s+acertos?\b/i);
    const total = text.match(/\b(\d+)\s+atividades?\b/i);
    if (!hits || !total) return null;
    const right = Number(hits[1]);
    const count = Number(total[1]);
    return count > 0 && right >= 0 && right <= count ? right / count : null;
  }

  function createScene() {
    if (result.querySelector('.ll-stellar-scene')) return;
    const scene = document.createElement('div');
    scene.className = 'll-stellar-scene';
    scene.setAttribute('aria-hidden', 'true');
    for (const kind of ['inner', 'outer']) {
      const orbit = document.createElement('span');
      orbit.className = 'll-stellar-orbit' + (kind === 'outer' ? ' ll-stellar-orbit--outer' : '');
      scene.appendChild(orbit);
    }
    for (let i = 0; i < 34; i++) {
      // Distribuicao deterministica, para evitar movimento aleatorio ou saltos ao reabrir.
      const star = document.createElement('span');
      star.className = 'll-stellar-star';
      star.style.setProperty('--ll-x', `${(11 + i * 37) % 94}%`);
      star.style.setProperty('--ll-y', `${(7 + i * 29) % 90}%`);
      star.style.setProperty('--ll-size', `${i % 7 === 0 ? 3 : i % 3 === 0 ? 2 : 1}px`);
      star.style.setProperty('--ll-duration', `${2.4 + (i % 6) * 0.43}s`);
      star.style.setProperty('--ll-delay', `${(i % 8) * -0.49}s`);
      scene.appendChild(star);
    }
    result.prepend(scene);
  }

  function applyResultTheme() {
    if (!showingResult()) return;
    const ratio = exactScore();
    const shouldCelebrate = ratio !== null && ratio > 0.70;
    // Evita mostrar "70%" em uma conquista de 70,1% arredondada.
    const score = byId('score');
    if (shouldCelebrate && score && /^70%$/.test(score.textContent.trim())) {
      score.textContent = (ratio * 100).toFixed(1).replace('.', ',') + '%';
    }
    if (shouldCelebrate) createScene();
    result.classList.toggle('ll-celestial', shouldCelebrate);
  }

  function armAudio() {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    try {
      if (!webAudio) webAudio = new Ctx();
      if (webAudio.state === 'suspended') {
        Promise.resolve(webAudio.resume()).catch(() => {});
      }
      if (!winBufferRequested) {
        winBufferRequested = true;
        fetch(SOUND_URL)
          .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.arrayBuffer();
          })
          .then(buffer => webAudio.decodeAudioData(buffer))
          .then(buffer => { decodedWin = buffer; })
          .catch(() => {}); // Um elemento <audio> permanece como alternativa.
      }
    } catch (_) { /* AudioContext pode ser indisponivel no dispositivo. */ }
  }

  function playWinOnce() {
    if (celebratedThisAttempt || !showingResult() || exactScore() === null || exactScore() <= 0.70) return;
    celebratedThisAttempt = true;

    // WebAudio desbloqueado por interacao anterior permite tocar apos o delay.
    if (webAudio && decodedWin && webAudio.state === 'running') {
      try {
        const source = webAudio.createBufferSource();
        source.buffer = decodedWin;
        source.connect(webAudio.destination);
        source.start(0);
        return;
      } catch (_) { /* Recorrer ao HTMLAudio abaixo. */ }
    }
    try {
      if (!winAudioElement) {
        winAudioElement = new Audio(SOUND_URL);
        winAudioElement.preload = 'auto';
      }
      winAudioElement.currentTime = 0;
      const promise = winAudioElement.play();
      if (promise && typeof promise.catch === 'function') promise.catch(() => {});
    } catch (_) { /* Nao interromper o resultado quando o browser bloqueia som. */ }
  }

  // Desbloqueio facultativo de som durante um gesto real do estudante.
  document.addEventListener('pointerdown', armAudio, { once: true, capture: true });
  document.addEventListener('keydown', armAudio, { once: true, capture: true });

  function stopAuto() {
    if (autoTimer !== null) {
      clearTimeout(autoTimer);
      autoTimer = null;
    }
  }

  function isFullyAnswered() {
    const raw = progressBar.style.width;
    if (!raw || !raw.trim().endsWith('%')) return false;
    const width = Number.parseFloat(raw);
    return Number.isFinite(width) && width >= 99.9999 && width <= 100.0001;
  }

  function scheduleAuto() {
    stopAuto();
    if (showingResult()) return;
    autoTimer = setTimeout(() => {
      autoTimer = null;
      if (!isFullyAnswered() || showingResult()) return;
      // Chama o proprio botao: preserva calculo, D1, evento law-bank-result e UI.
      finish.click();
    }, AUTO_DELAY_MS);
  }

  function watchProgress() {
    // Aguarde o primeiro valor real: evita agendar ao abrir um banco ja completo.
    if (!progressBar.style.width || !progressBar.style.width.trim().endsWith('%')) return;
    const completed = isFullyAnswered();
    if (lastComplete === null) {
      // Nao redirecionar quem apenas recarregou um banco ja concluido.
      lastComplete = completed;
      return;
    }
    if (!completed) stopAuto();
    if (completed && !lastComplete) scheduleAuto();
    lastComplete = completed;
  }

  const observer = new MutationObserver(watchProgress);
  observer.observe(progressBar, {attributes:true, attributeFilter:['style']});
  watchProgress();

  // O motor emite esse evento depois de construir o resultado e seu placar.
  window.addEventListener('law-bank-result', applyResultTheme);

  // O bubble listener roda DEPOIS do handler nativo do botao Resultado,
  // ainda no gesto do usuario (importante para reproduzir win.mp3 no Safari).
  document.addEventListener('click', event => {
    const clicked = event.target;
    if (!(clicked instanceof Element)) return;
    if (clicked.closest('#finishBtn') === finish) {
      stopAuto();
      applyResultTheme();
      playWinOnce();
    } else if (clicked.closest('#restartBtn')) {
      stopAuto();
      celebratedThisAttempt = false;
      result.classList.remove('ll-celestial');
    } else if (clicked.closest('#reviewWrongBtn')) {
      stopAuto();
      result.classList.remove('ll-celestial');
    }
  });
})();
