# Brasil Fut — Correção Geral, Modo Copa, Redesign e APK

> **Para workers:** Este plano cobre 3 fases independentes. Use subagent-driven-development para executar tarefas em paralelo quando possível.

**Objetivo:** Corrigir 18 bugs da engine, adicionar modo Copa do Mundo 2026, refatorar código, redesenhar o site, e gerar APK funcional.

**Arquitetura:** Fases sequenciais — (1) brasil-fut.html: refatorar + corrigir bugs + modo Copa, (2) index.html: redesign completo, (3) android/: build APK + workflow.

---

## Fase 1: Refatoração + Bugs + Modo Copa (brasil-fut.html)

### Task 1.1: Eliminar override pattern e código morto

**Arquivo:** `brasil-fut.html`

O arquivo atual tem 4 definições sobrepostas de funções-chave via hoisting:
- `endSeason` (linhas 3160, 5142, 6167, 7919) → consolidar em uma
- `advanceWeek` (linhas 2719, 5121, 6244, 7851) → consolidar em uma
- `generateMatchEvents` (linhas 2596, 4070) → manter só a v2.0 (linha 4070)
- `runMatchAnimation` (linhas 2546, 4183) → manter só a v2.0 (linha 4183)
- `buildSquadFromNames` (linhas 1255, 5418, 7733) → consolidar em uma
- `generatePlayer` (linhas 1030, 7719) → manter só a final (linha 7719)
- `renderWizard` (linhas 3688, 4436, 5476, 5873) → consolidar em uma
- `initGame` (linhas 1267, 5074) → manter só a final (linha 5074)
- `simulateCopaBrasilRound` vs `simulateCopa` → consolidar
- Remover código morto (~500 linhas das funções v1 originais que são sobrepostas)
- Manter patches v6-v8 (linhas ~11330-11420) e integrá-los no código principal

### Task 1.2: Corrigir 18 bugs

- **BUG-1:** `simulateMatchQuick` (linha 2679) — usar `teamEffRating()` em vez de `rating` bruto
- **BUG-13:** `bench` filter (linha 2663) — lógica de POSITIONS errada; corrigir para excluir titulares
- **BUG-14:** `simulateMatchQuick` filter fallback (linha 2688) — `.filter()` sempre retorna array; adicionar fallback real
- **BUG-15:** `scorerPool` vazio (linha 4111) — fallback para `t.players` mesmo que filter retorne vazio
- **BUG-7:** pm-field crash (linha 2831) — garantir que `pm-field` ou `pm-center` exista
- **BUG-2:** `updateMatchStats` só atualiza time do usuário (linha 2693) — expandir para oponente
- **BUG-4:** `simulateEstadualRound` só simula 1 fixture (linha 2839)
- **BUG-5:** Copa bracket com winners ímpar (linha 2885)
- **BUG-8:** Yellow cards acumulam sem reset (linha 2649)
- **BUG-9:** Suspensão aleatória 50% (linha 3027)
- **BUG-17:** Histórico grava 0 pontos (linha 3263)
- **BUG-18:** Rebaixamento/promoção só cosmético (linha 7930)
- **BUG-16:** Fórmula financeira errada (linha 2997)
- **BUG-6:** `p.age=p.age` no-op (linha 3025)
- Integrar patches v6-v8 no código principal

### Task 1.3: Modo Copa do Mundo 2026

**Adicionar ao `brasil-fut.html`:**

- Botão na tela inicial: "MODO COPA DO MUNDO 2026"
- Fluxo isolado (não interfere no modo clube)
- Grupos fixos A-L (12 grupos × 4 seleções = 48 seleções) baseados nos grupos reais da Copa 2026
- Tela de convocação: selecionar 23 jogadores
- Fase de grupos: cada seleção joga 3 partidas, top 2 avançam
- Mata-mata: oitavas → quartas → semi → final
- Popup ao final: "CAMPEÃO: [seleção]!" + botões "Nova Copa" / "Voltar ao Menu"
- Design temático de Copa do Mundo (cores, fontes, background)

### Task 1.4: Design temático Copa do Mundo no app

- Tema especial para o modo Copa (cores: verde/amarelo/azul, elementos de estádio, troféu)
- Transições e animações no modo Copa
- Manter tema escuro original para o modo clube

---

## Fase 2: Redesign Completo do Site (index.html)

### Task 2.1: Novo layout e estrutura

- Layout moderno responsivo
- Remover contradições (mobile/desktop)
- Hero reformulado
- Seção dedicada ao modo Copa do Mundo 2026
- Seção de download com link correto para APK
- Footer atualizado

---

## Fase 3: APK Android

### Task 3.1: Workflow + Build

- Commitar `.github/workflows/build-apk.yml` (não commitado atualmente)
- Copiar `brasil-fut.html` para `android/app/src/main/assets/`
- Adicionar `gradlew`/`gradlew.bat`/`gradle-wrapper.jar` ao repo
- Build e release do APK

---

## Ordem de Execução

```
Fase 1 (Task 1.1 + 1.2) → Fase 1 (Task 1.3 + 1.4)  [podem ser paralelas com Fase 2]
Fase 2 (independente, pode rodar em paralelo com Fase 1)
Fase 3 (APK, após Fase 1 estar completo)
```
