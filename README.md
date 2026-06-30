# Pokemon Random Intro

這是阿甘留給 Aiworks 夥伴的小玩具！

一起成為寶可夢大師吧 :D

## 使用說明

在 OpenAI Codex 輸入 `$pokemon-random-intro`，或在 Claude Code / Claude Cowork 輸入 `/pokemon-random-intro`，即可呼叫此 Skill 隨機抽一隻寶可夢，以繁體中文呈現捕獲訊息，包含圖片、名稱、屬性、圖鑑描述與進化鏈。

## 注意事項

在 Skill 內已有明確規範只有呼叫時觸發此 Skill，但仍然建議與工作專案區分開來，並避免在與工作相關的 session 觸發此 Skill，以免污染工作 context。

## 安裝

支援 OpenAI Codex、Claude Code、Claude Cowork。圖片顯示依平台分流，Codex 使用本機圖片路徑，Claude Code / Claude Cowork 使用遠端圖片 URL。

### OpenAI Codex

將整個 `pokemon-random-intro/` skill 複製到全域 `~/.codex/skills/`，或專案內的 `.codex/skills/` 目錄下，Codex 就會自動讀取 `SKILL.md` 與 `agents/openai.yaml`。

安裝完成後，在 Codex 中輸入 `$pokemon-random-intro` 即可使用。

### Claude Code

將整個 `pokemon-random-intro/` skill 複製到全域或專案的 `.claude/skills/` 目錄下：

```bash
mkdir -p .claude/skills
cp -r pokemon-random-intro .claude/skills/
```

安裝完成後，在 Claude Code 中輸入 `/pokemon-random-intro` 即可使用。

### Claude Cowork

於 Customize > Skill 頁面點選 Create Skill > Upload a skill，並上傳 `pokemon-random-intro.zip` 即可新增 skill。

安裝完成後，在 Claude Cowork 中輸入 `/pokemon-random-intro` 即可使用。

## 需求

- Python 3.8+（僅使用標準函式庫，不需安裝額外套件）
- 網路連線（存取 PokéAPI）

## 手動測試

```bash
# 隨機一隻
python3 scripts/random_pokemon_intro.py

# 指定物種
python3 scripts/random_pokemon_intro.py --species pikachu
```

## 專案結構

```
pokemon-random-intro/
├── SKILL.md                          # Skill 定義（雙平台共用）
├── scripts/
│   └── random_pokemon_intro.py       # 主程式
├── agents/
│   └── openai.yaml                   # Codex agent 設定
└── README.md
```

## 資料來源

[PokeAPI](https://pokeapi.co/) - 免費、無需 API key 的寶可夢資料 API。
