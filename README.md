# World War — jogo de estratégia (estilo Combate)

Jogo para iPhone feito em uma única página HTML (`index.html`), sem dependências de build.
Publicado como artefato no Claude: https://claude.ai/artifact/Ri9EMsnLDqeJMXhuPE6VFi

## Estrutura
- `index.html` — todo o jogo (CSS + JS inline).
- `capa.webp` — capa com escolha de nação (botões invisíveis sobre as 11 bandeiras).
- `fundo.webp`, `fundo_blur.webp` — fundos da campanha e da batalha.
- `mapa.webp` — tabuleiro 10×9 (recorte do mapa do usuário; lago nas colunas 5–6, linhas 4–6).
- `cf/<país>.webp` — fundos da tela de confronto (placa medida em `CF` no código).
- `fim.webp` — cena da tela de fim de partida.
- `nac/<país>.webp` — brasões da janela "Escolha seu exército".
- `pecas/` — cartas: `<país>_<k>` (inimigo, selo verde), `P<país>_<k>` (jogador, selo vermelho),
  `<país>_1|B|F|M` (Espião, Granada, Bandeira, Morteiro), `verso.webp`, `r_*/g_*` (antigas/genéricas).
- `som/musica.mp3` — trilha. Efeitos são sintetizados (Web Audio).
- `tools/` — scripts Python usados para recortar as folhas de cartas.

Códigos de país: bra, us, ar, fr, de, ru, jp, cn, nl, it, uk.

## Regras implementadas
30 cartas por lado: Marechal 10, General 9, Coronel 8, Major 7 ×2, Capitão 6 ×3, Tenente 5 ×3,
Sargento 4 ×3, Cabo 3 ×4, Soldado 2 ×5, Espião 1, Granada ×4, Morteiro ×1, Bandeira.
Todas andam 1 casa. Cartas viram de novo após o confronto. Regra de repetição (3×).
Morteiro: uso único, destrói qualquer carta inimiga (inclusive a bandeira = vitória) e sai do jogo.
Campanha: 10 fases (os países menos o escolhido), dificuldade crescente (ruído e memória da IA).

## Rodar
Abra `index.html` num servidor local (`python3 -m http.server`) ou publique em qualquer hospedagem estática.
