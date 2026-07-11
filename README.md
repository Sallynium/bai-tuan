# 🐶 桌面小狗互動介面（bai-tuan）

> 🌐 線上版：https://sallynium.github.io/bai-tuan/

- **這是什麼？** 一個療癒系「養小狗」網頁：卡通狗狗會自己走動，可以摸牠、餵牠、搓肚子，冷落牠會委屈。單一 `index.html`，雙擊即開。
- **給誰用？** 自用（療癒 + 前端練習）。
- **MVP（v1 完成 = 全勾）**
  - [x] 場景 + 狗狗靜態 SVG（伯恩山），idle 動態（走動/坐下/眨眼/搖尾）
  - [x] 撫摸 + 愛心粒子 + happy；餵食完整流程（含按鈕冷卻）
  - [x] 連點翻肚、搓肚踢腿
  - [x] mood 系統 + lonely / comforted / sleeping
  - [x] 薩摩耶切換（柯小白大將軍 ⇄ 小肉團領主，各有專屬台詞）
  - [x] 對話泡泡、雲朵、reduced-motion

## 素材管線（Gemini 圖 → sprite sheet）

狗狗圖改用 Gemini 生成的 3x3 姿勢圖集（白底），處理流程：

```
python tools/build-sprites.py assets/samoyed-raw.png assets/samoyed-sheet.png
```

腳本會去背、切出 9 個姿勢、腳底對齊排成標準九宮格；取輸出的 `.q.png`（128 色量化版）
轉 base64 崁入 `index.html` 的 `--sheet-*` CSS 變數。
- **明確不做什麼？**
  - 不存檔（無 localStorage）、無音效、無外部資源（CDN/圖片/字型）
  - 不加規格書以外的功能或改動數值

## 玩法

摸摸（按住滑動）、點空地叫牠過去、連點兩下翻肚搓肚、餵食、換狗（領主⇄大將軍）。
放著 90 秒會鬧脾氣縮角落，只有按住摸 3 秒能哄好；心情太低會睡著。
遊戲內右上「？」按鈕有完整說明。

## 專案架構

維護指南（檔案地圖、index.html 內部結構、素材管線、驗收方法、編輯地雷）
全部寫在 **[CLAUDE.md](CLAUDE.md)**——要迭代先讀它。

## 本機執行

雙擊 `index.html` 即可，或任一靜態伺服器：

```
npx serve .
```

規格書：見開發對話（實作嚴格依照規格書，勿自行加料）。
