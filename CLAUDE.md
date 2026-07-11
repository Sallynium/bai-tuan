# bai-tuan 專案指南（給 AI session / 未來的自己）

療癒系養狗網頁。**單一 index.html、零外部資源**（圖以 base64 崁入）、無建置步驟、無存檔。
線上版：https://sallynium.github.io/bai-tuan/ ｜ Repo：https://github.com/Sallynium/bai-tuan

## 檔案地圖

```
index.html            ← 唯一產品檔（CSS+HTML+JS 全在裡面，含兩張 base64 圖集）
assets/
  bernese-raw.png     ← Gemini 原圖（伯恩山 3x3 白底）
  doggg2.jfif         ← Gemini 原圖（薩摩耶 3x3 白底）
  bernese-sheet.png   ← 處理後圖集（去背+正規化+128色量化）
  samoyed-sheet.png   ← 同上
tools/
  build-sprites.py    ← 圖集處理管線（見下）
  test-harness.js     ← 驗收用虛擬時鐘 harness（貼進 preview_eval 用）
.claude/launch.json   ← preview 伺服器設定（python http.server:4173，已 gitignore）
```

## ⚠️ 編輯 index.html 的地雷

1. **兩行超長 base64**（`--sheet-bernese` / `--sheet-samoyed` CSS 變數，共 ~150K 字元）。
   **整檔 Read 會爆 token** → 先 `Grep` 找行號，再用 offset/limit 分段讀。
2. 換圖集流程：CSS 變數值先寫占位符（如 `__XXX_B64__`），再用 python 注入：
   `python -c "import base64; b=...; s.replace('__XXX_B64__', b)"`（見 git log 慣例）。
3. 檔案被腳本改過後，Edit 工具要先重新 Read 相關段落才能改。

## index.html 內部結構（由上而下）

- **CSS**：色彩 token（`:root`，規格書指定）→ 場景/按鈕 → 雲朵 → 狗狗 sprite
  （`#dogSprite[data-pose=...]` 九宮格 background-position 表）→ 粒子/泡泡 → 玩法面板 → reduced-motion
- **HTML**：`#scene` > 雲、地面、topbar（換狗鈕＋？鈕＋心情量表）、`#dog`（jumpWrap>dogFlip>dogSprite 三層：跳躍動畫/左右翻面/換圖）、泡泡、餵食鈕、`#helpPanel`
- **JS（IIFE）**：
  - 常數區：規格書數值（衰減率、冷卻、閾值）都在最上面
  - `LINES` + `BREED_IDLE` + `COMMON_IDLE`：**台詞都在這裡改**
  - 狀態機：`idle / walking / sitting / happy / belly / lonely(go→curl) / comforted(rise→run) / sleeping / toFood / eating`
    - 優先權：belly > comforted > lonely/sleeping > happy > walking/sitting > idle
    - 核心委屈機制：90 秒沒互動→縮角落；餵食不解氣；累計摸 3 秒才 comforted
  - 輸入：pointer events（摸=按住滑動 40px/次；連點 300ms=翻肚；點空地=走過去）
  - 主迴圈：`requestAnimationFrame`，所有計時用時間戳，`dt` 上限 0.05s

## 素材管線（新增品種/換圖）

1. 用 Gemini 生 3x3 姿勢圖（prompt 見 git log 或問使用者；姿勢順序：站/走A/走B/坐/開心/翻肚/委屈/睡/吃）
2. `python tools/build-sprites.py <原圖> <輸出.png> [BG_MIN]`
   - 深色狗用預設 205；**淺色狗（描邊接近白）要拉高到 238**，否則去背會吃掉狗
   - 取輸出的 `.q.png`（量化版，小 5-7 倍）改名使用
3. base64 注入 CSS 變數 → `#dogSprite.<breed>` 加 background-image 規則

## 驗收方法（重要！）

**Claude Preview 的分頁在背景時，瀏覽器會暫停 rAF 與 CSS 動畫**——遊戲不會動、
preview_screenshot 一律逾時。**不要嘗試截圖驗收**。
正確做法：用 `tools/test-harness.js` 的 iframe+虛擬時鐘 harness（貼進 preview_eval），
可控制每一幀、可快轉 90 秒測 lonely。畫面美感請使用者肉眼確認。

## 部署

push 到 `main` → GitHub Pages 自動部署（無 build）。
驗證線上版：下載後 `git hash-object <檔>` 對比 `git rev-parse main:index.html`
（不要用 Invoke-WebRequest .Content 字串比對，編碼會誤判）。

## 世界觀（改台詞前先知道）

伯恩山＝**小肉團領主**，薩摩耶＝**柯小白大將軍**，互為君臣。共同口頭禪：呀噠噠、可欣可欣。
