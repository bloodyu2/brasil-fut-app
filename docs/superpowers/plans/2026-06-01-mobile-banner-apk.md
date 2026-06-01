# Mobile APK Banner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add mobile APK download banner and responsive adaptations to index.html

**Architecture:** Single file change (index.html). Banner fixed at bottom on <600px viewports, hidden by default on desktop. Desktop flow unchanged.

**Tech Stack:** Vanilla HTML/CSS/JS (inline), sessionStorage for dismiss state

---

### Task 1: Add banner CSS

**Files:**
- Modify: `index.html` (add styles to existing `<style>` block, before `@media (max-width: 600px)`)

- [ ] **Step 1: Add mobile banner styles**

Add inside `<style>` before the existing media query:

```css
.mobile-dl-banner {
  display: none;
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 300;
  background: linear-gradient(135deg, #0B1810 0%, #060A0F 100%);
  border-top: 1px solid var(--bd);
  padding: 14px 16px 16px;
  font-family: var(--fb);
}
.mobile-dl-banner.visible { display: block; }
.mdl-inner {
  display: flex; align-items: center; gap: 12px;
}
.mdl-icon {
  flex-shrink: 0; width: 40px; height: 40px;
  background: var(--g); border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  color: #060A0F;
}
.mdl-text { flex: 1; min-width: 0; }
.mdl-title {
  font-family: var(--fd); font-size: 14px; font-weight: 700; color: var(--t1);
  line-height: 1.3;
}
.mdl-sub {
  font-size: 12px; color: var(--t3); margin-top: 2px; line-height: 1.3;
}
.mdl-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.mdl-btn {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--g); color: #060A0F;
  font-family: var(--fd); font-weight: 700; font-size: 12px;
  padding: 8px 14px; border-radius: 8px; border: none; cursor: pointer;
  white-space: nowrap; transition: background .15s;
}
.mdl-btn:hover { background: var(--gd); }
.mdl-close {
  width: 28px; height: 28px; border-radius: 6px;
  background: var(--s2); border: 1px solid var(--bd); color: var(--t3);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  font-size: 14px; transition: background .15s; flex-shrink: 0;
}
.mdl-close:hover { background: var(--s3); color: var(--t1); }
.mdl-browser-link {
  font-size: 11px; color: var(--t3); cursor: pointer; text-decoration: underline;
  transition: color .15s; white-space: nowrap;
}
.mdl-browser-link:hover { color: var(--g); }
```

- [ ] **Step 2: Add mobile display rule in media query**

Inside existing `@media (max-width: 600px)`, add:

```css
.mobile-dl-banner.visible { display: block; }
```

---

### Task 2: Add banner HTML

**Files:**
- Modify: `index.html` (add before `</body>`)

- [ ] **Step 1: Add banner markup**

Add before the closing `</body>` tag:

```html
<div class="mobile-dl-banner" id="apkBanner">
  <div class="mdl-inner">
    <div class="mdl-icon">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
    </div>
    <div class="mdl-text">
      <div class="mdl-title">Brasil Fut para Android</div>
      <div class="mdl-sub">Jogue offline, sem travar. APK leve e rápido.</div>
    </div>
    <div class="mdl-actions">
      <button class="mdl-btn" onclick="downloadApk()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        APK (441 KB)
      </button>
      <button class="mdl-close" onclick="closeApkBanner()" aria-label="Fechar">&#10005;</button>
    </div>
  </div>
  <div style="text-align:right;margin-top:6px;padding-right:4px">
    <span class="mdl-browser-link" onclick="playBrowser()">Jogar no navegador</span>
  </div>
</div>
```

---

### Task 3: Add banner JS and mobile adaptations

**Files:**
- Modify: `index.html` (add to existing `<script>` block, before final IIFE)

- [ ] **Step 1: Add banner JS functions**

Add inside the `<script>` block:

```javascript
function closeApkBanner() {
  document.getElementById('apkBanner').classList.remove('visible');
  try { sessionStorage.setItem('apkBannerClosed', '1'); } catch(e) {}
}
function downloadApk() {
  var a = document.createElement('a');
  a.href = APK_URL;
  a.download = 'BrasilFut-Android.apk';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
function playBrowser() {
  closeApkBanner();
  window.location.href = 'brasil-fut.html';
}
```

- [ ] **Step 2: Show banner on mobile if not dismissed**

Modify the IIFE at the bottom of the script:

```javascript
(function() {
  var isMob = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  if (isMob) {
    document.getElementById('dlBtnLabel').textContent = 'Baixar APK — Android';
    var closed = false;
    try { closed = sessionStorage.getItem('apkBannerClosed') === '1'; } catch(e) {}
    if (!closed) {
      document.getElementById('apkBanner').classList.add('visible');
    }
  }
})();
```

- [ ] **Step 3: Change hero button behavior on mobile**

Modify the hero button `onclick`:

```html
<button class="btn-primary" onclick="handleHeroClick()">
```

Add the handler:

```javascript
function handleHeroClick() {
  if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    window.location.href = 'brasil-fut.html';
  } else {
    openDownload();
  }
}
```

---

### Task 4: Responsive adjustments

**Files:**
- Modify: `index.html` (existing `@media (max-width: 600px)` section)

- [ ] **Step 1: Improve mobile responsive CSS**

Replace existing media query contents:

```css
@media (max-width: 600px) {
  nav { padding: 0 12px; }
  .nav-link { display: none; }
  .stats { flex-wrap: wrap; }
  .stat { min-width: 50%; border-right: none; border-bottom: 1px solid var(--bd); }
  .stat:nth-child(odd) { border-right: 1px solid var(--bd); }
  .stat:last-child { border-bottom: none; }
  .features-grid, .copa-grid, .dl-grid { gap: 10px; }
  .dl-grid { grid-template-columns: 1fr; }
  .copa-grid { grid-template-columns: 1fr 1fr; }
  .section, .copa-inner { padding: 48px 16px; }
  .radio-group { flex-direction: column; }
  .update-label { display: none; }
  .steps-block { padding: 24px; }
  .mobile-dl-banner.visible { display: block; }
}
```

---

### Task 5: Commit and push

- [ ] **Step 1: Commit**

```bash
git add index.html docs/superpowers/specs/2026-06-01-mobile-banner-apk-design.md docs/superpowers/plans/2026-06-01-mobile-banner-apk.md
git commit -m "feat: mobile APK banner + responsive adaptations

- Sticky bottom banner for Android APK download on mobile
- Direct download without modal/checklist
- 'Jogar no navegador' option that opens brasil-fut.html
- Hero button opens game directly on mobile
- Responsive improvements for small screens"
git push origin master
```
