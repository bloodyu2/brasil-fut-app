# Brasil Fut App

> Gerenciador de futebol offline — monte elencos, defina táticas e jogue campeonatos. Roda no navegador ou como app nativo no Windows.

## Stack

- **HTML5 + CSS + Vanilla JS** — SPA completo em arquivo único (`brasil-fut.html`)
- **Electron v28** — empacotamento como app nativo para Windows
- Sem backend, sem banco de dados — estado salvo em `localStorage`

## Funcionalidades

- Gestão de clube: elenco, contratações, finanças, moral
- Escalação tática com drag-and-drop no campo
- Simulação de partidas e campeonatos temporada a temporada
- Save/load automático via localStorage
- 8.317+ escudos de clubes mundiais (`escudos/`)
- 86 seleções nacionais com camisas (`camisas/`)

## Como rodar

### No navegador

```bash
# Opção 1: abrir diretamente
# Clique duplo em brasil-fut.html

# Opção 2: via launcher Windows
JOGAR.bat
```

### Como app Electron

```bash
npm install
npm start
```

### Build do executável Windows

```bash
build-windows.bat
```

O executável portátil será gerado via `electron-builder`.

## Arquivos principais

```
brasil-fut.html         # Jogo completo (SPA — ~994 KB)
main.js                 # Entry point Electron (menu: Novo Jogo, Salvar, Carregar)
index.html              # Landing page para beta testers (GitHub Pages)
JOGAR.bat               # Launcher principal Windows (detecta Python → Edge → Chrome)
BrasilFut.vbs           # Launcher silencioso (sem janela de terminal)
launcher.pyw            # Launcher Python com servidor HTTP local
build-windows.bat       # Gera executável portátil
escudos/                # 8.317+ escudos de clubes
camisas/                # 86 seleções nacionais
```

## Deploy

- **GitHub Pages** — `index.html` (landing page para beta testers)
- **GitHub Releases** — download do ZIP com o executável Windows

**Repo:** https://github.com/bloodyu2/brasil-fut-app

---

Desenvolvido pela [Balaio Digital](https://balaio.net)
