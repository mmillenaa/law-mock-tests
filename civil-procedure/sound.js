// sound.js — feedbacks sonoros para os simulados

// Define os URLs dos áudios (use os links brutos do GitHub)
const SOUNDS = {
    correct: './correct.mp3',
    wrong: './wrong.mp3',
    win: './win.mp3'
};

// Função para tocar um som
function playSound(type) {
    const url = SOUNDS[type];
    if (!url) return;
    const audio = new Audio(url);
    audio.play().catch(err => console.warn('Áudio não pôde ser reproduzido:', err));
}

// ============================================================
//  INTEGRAÇÃO COM OS SIMULADOS
// ============================================================

// 1. Para questões de múltipla escolha (Fase1, Fase2, Fase3, Fase4)
//    — Acionar quando o usuário seleciona uma opção e confirma.
//    Basta chamar playSound('correct') ou playSound('wrong') no momento apropriado.

// 2. Para questões de lacuna (Fase5, Fase6, Fase7)
//    — Acionar no confirmAnswer().

// 3. Para a conclusão do simulado (showResults)
//    — Chamar playSound('win') quando a tela de resultados for exibida.

console.log('🔊 sound.js carregado — feedbacks sonoros disponíveis.');
