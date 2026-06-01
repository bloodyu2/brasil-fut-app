# Mobile APK Banner + Mobile Adaptations

## Contexto

Site index.html tem download modal com checklist/referral que é complexo demais para mobile. Usuário quer experiência mobile simples: banner direto para download do APK, sem impedimentos.

## Comportamento Mobile vs Desktop

| | Desktop | Mobile |
|---|---|---|
| Hero "Jogar Brasil Fut" | Abre modal de download | Abre `brasil-fut.html` diretamente |
| Download APK | Modal checklist + referral (existente) | Banner sticky no rodapé |
| Card "Android" | Link direto pro APK (existente) | Link direto pro APK (existente) |

## Banner APK Mobile

- **Posição:** fixed bottom, apenas em mobile (max-width: 600px via media query + classe `mobile-dl-banner`)
- **Visibilidade:** aparece quando detectado user agent mobile E banner não foi fechado (sessionStorage)
- **Conteúdo:** fundo gradiente verde escuro (#0B1810 → #060A0F), ícone + título + subtítulo + botão CTA + X
- **Botão "Baixar APK (441 KB)":** dispara download direto, link para GitHub Release
- **"X":** fecha o banner, salva `sessionStorage.setItem('apkBannerClosed','1')`
- **Link "Jogar no navegador":** fecha banner + navega para `brasil-fut.html`

## Adaptações Mobile no index.html

- Hero button: em mobile, `onclick` navega para `brasil-fut.html` ao invés de `openDownload()`
- Estatísticas (`.stats`): empilhamento vertical em telas < 480px
- Grids de features/copa/download: gap reduzido em mobile
- Nav: esconder link "Novidades" em telas muito pequenas
- Source: inline no index.html (mesmo padrão existente)

## Arquivos Alterados

- `index.html` — adicionar CSS do banner, JS de detecção mobile, ajustes responsivos

