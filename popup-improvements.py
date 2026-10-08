from pathlib import Path

root = Path('labour-law')
ranking = root / 'mais-curtidas.html'
popup_js = root / 'support-popup.js'
popup_css = root / 'support-popup.css'
for path in (ranking, popup_js, popup_css):
    if not path.exists():
        raise SystemExit(f'Arquivo não encontrado: {path}. Execute na raiz do repositório.')

# Ranking: não altera D1. Busca a explicação no JSON oficial de cada banco.
s = ranking.read_text(encoding='utf-8')
if 'question-explanation' not in s:
    style_anchor = '    .question-meta{'
    assert s.count(style_anchor) == 1, 'CSS do ranking mudou; interrompido.'
    style = '''    .question-explanation{
      margin:9px 0 0;
      color:#9ca9ba;
      font-family:"DM Sans",sans-serif;
      font-size:13px;
      font-weight:400;
      line-height:1.65;
    }


'''
    s = s.replace(style_anchor, style + style_anchor, 1)

    group_anchor = '        const groups = {};'
    assert s.count(group_anchor) == 1, 'Agrupamento do ranking mudou; interrompido.'
    enrich = '''        // Explicações oficiais dos cinco bancos; sem duplicar conteúdo no D1.
        const explanationByBank = new Map();
        const banksWithLikes = [...new Set(questions.map(q => q.bank))];

        await Promise.all(banksWithLikes.map(async bank => {
          if(!Object.prototype.hasOwnProperty.call(BANK_NAMES, bank)) return;
          try{
            const result = await fetch("./" + bank + ".json", {cache:"no-store"});
            if(!result.ok) throw new Error("JSON " + result.status);
            const source = await result.json();
            const byId = new Map((source.questions || []).map(q => [
              String(q.id),
              String(q.explanation || "").replace(/^\\s*Correto\\.\\s*/i, "").trim()
            ]));
            explanationByBank.set(bank, byId);
          }catch(error){
            console.warn("Explicação indisponível:", bank, error);
          }
        }));

        questions.forEach(q => {
          q.explanation = explanationByBank.get(q.bank)?.get(String(q.question_id)) || "";
        });


'''
    s = s.replace(group_anchor, enrich + group_anchor, 1)

    question_meta_anchor = '                                      <div class="question-meta">'
    assert s.count(question_meta_anchor) == 1, 'Cartão do ranking mudou; interrompido.'
    new_markup = '''                                      ${
                                        item.explanation
                                          ? '<p class="question-explanation">' + escapeHtml(item.explanation) + '</p>'
                                          : ''
                                      }

                                      <div class="question-meta">'''
    s = s.replace(question_meta_anchor, new_markup, 1)
    ranking.write_text(s, encoding='utf-8')
    print('OK: ranking agora exibe a explicação oficial abaixo da pergunta.')
else:
    print('SKIP: ranking já ajustado.')

# Mover a xícara da coluna do texto para a ilustração do gato.
s = popup_js.read_text(encoding='utf-8')
art_start = s.find('class="support-popup-art"')
copy_start = s.find('class="support-popup-copy"')
cup_start = s.find('          <div\n            class="support-cup"')
existing_cup = s.find('class="support-cup"')
assert -1 not in (art_start, copy_start, existing_cup), 'Markup do popup diferente; interrompido.'
if existing_cup > copy_start:
    assert cup_start >= 0, 'Bloco antigo da xícara não encontrado.'
    cup_end = s.find('\n          </div>', cup_start)
    assert cup_end > cup_start, 'Fim da xícara não encontrado.'
    cup_end += len('\n          </div>')
    s = s[:cup_start] + s[cup_end:]

    new_cup = '''          <div class="support-cup" aria-hidden="true">
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
          </div>'''

    copy_start = s.find('class="support-popup-copy"')
    art_end = s.rfind('\n        </div>', 0, copy_start)
    assert art_end > art_start, 'Fim da cena do gato não encontrado.'
    s = s[:art_end] + '\n\n' + new_cup + '\n' + s[art_end:]
    popup_js.write_text(s, encoding='utf-8')
    print('OK: xícara movida para o canto inferior direito da cena do gato.')
else:
    print('SKIP: xícara já está na área do gato.')

# Ajustes visuais: sobre a cena, sem encobrir o corpo do gato.
s = popup_css.read_text(encoding='utf-8')
if 'SUPPORT TEACUP FOREGROUND V2' not in s:
    s += '''

/* SUPPORT TEACUP FOREGROUND V2 */
.support-popup-art .support-cat{z-index:2;}
.support-popup-art .support-cup{
  position:absolute;
  z-index:3;
  right:10px;
  bottom:15px;
  width:84px;
  opacity:1;
  pointer-events:none;
  filter:drop-shadow(0 9px 7px rgba(0,0,0,.42));
}
.support-popup-art .support-cup svg{display:block;width:100%;height:auto;overflow:visible;}
.support-popup-art .support-steam{
  opacity:0;
  transform-box:fill-box;
  transform-origin:center bottom;
  animation:support-tea-steam 8s ease-in-out infinite;
}
.support-popup-art .support-steam-two{animation-delay:-2.7s;animation-duration:9s;}
.support-popup-art .support-steam-three{animation-delay:-5.3s;animation-duration:7.5s;}
@keyframes support-tea-steam{
  0%{opacity:0;transform:translate(0,9px) scaleX(.82);}
  20%{opacity:.49;}
  55%{opacity:.33;transform:translate(3px,-10px) scaleX(1.1);}
  100%{opacity:0;transform:translate(-3px,-24px) scaleX(1.28);}
}
@media(max-width:700px){
  .support-popup-art .support-cup{right:12px;bottom:7px;width:64px;}
}
@media(max-width:390px){
  .support-popup-art .support-cup{right:8px;width:53px;}
}
@media(prefers-reduced-motion:reduce){
  .support-popup-art .support-steam{animation:none;opacity:.25;}
}
'''
    popup_css.write_text(s, encoding='utf-8')
    print('OK: xícara em destaque e vapor lento animado (com acessibilidade).')
else:
    print('SKIP: estilos da xícara já ajustados.')
