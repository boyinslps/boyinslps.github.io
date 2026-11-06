# 教學網站總覽

資訊課程、教學遊戲、競賽活動與 AI 工具的分類導覽頁。

網址：https://boyinslps.github.io/


## 自動更新

`.github/workflows/update-auto.yml` 每 6 小時（也可在 Actions 頁手動執行）執行 `scripts/gen_auto.py`，
掃描帳號下有開 Pages 的 repo，寫入 `auto.json`。首頁會把尚未放進固定清單的網站顯示在「最新新增」。

- 不想被列入：替該 repo 加上 topic `no-index`。
- 想列出子頁面：在該 repo 根目錄放 `site.json`，格式 `[{"t":"標題","d":"說明","u":"子路徑/"}]`。
- 想分類、改中文名稱：把網址放進 `index.html` 的 `DATA`，「最新新增」就會自動略過它。

made by 資訊老師黃博胤
