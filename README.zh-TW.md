# InkBrush Motion｜水墨知識動畫 Skill

這是一個開源 AI Skill，把已確認的知識內容轉成原生 9:16 中國水墨／書法感動畫包。它刻意避開霓虹、漂浮卡片與科技粒子，改用宣紙、山水、留白、運筆與墨色擴散呈現 AI 知識。

[公開後觀看 HTML 動畫示範](https://vivi911.github.io/inkbrush-motion-skill/)｜[英文主 README](README.md)｜[Skill 規格](SKILL.md)

## 核心規則

- 先做 9:16 靜態稿，Vivi／使用者拍板後才做動態。
- 預覽 720×1280；正式規格 1080×1920、30fps、H.264。
- 正式文字必須是 SVG／程式字層，不相信生圖模型寫字。
- 筆尖必須走在墨跡最前方；墨色延遲擴散，不能用全畫面擦除假裝書寫。
- 動態交付要附開頭／中段／結尾三張證據畫面。

## 一分鐘試玩

```bash
git clone https://github.com/vivi911/inkbrush-motion-skill.git
cd inkbrush-motion-skill
python3 -m http.server 8000
```

瀏覽器開啟 `http://localhost:8000`，按下 **Replay the brush**。

## 著作權

Copyright © 2026 Vivi（GoAskVivi）。

本 repo 的程式、Skill 指令、文件、SVG／CSS／JavaScript 視覺與已發布的社群預覽 PNG 採 [MIT License](LICENSE)，但第三方工具與系統字體仍依各自授權。轉載或改作時需保留著作權與授權聲明。GoAskVivi 名稱與品牌識別不包含在背書授權內。

公開包沒有放入 ImageGen 點陣樣張，也沒有內嵌第三方開源程式碼；完整邊界見 [COPYRIGHT.md](COPYRIGHT.md)。

如果你也想讓 AI 知識回到安靜、手作、有人味的畫面，歡迎替 repo 按一顆 Star。
