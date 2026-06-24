# Pokemon Random Intro

從 PokeAPI 隨機抽一隻寶可夢，以繁體中文呈現捕獲訊息，包含圖片、名稱、屬性、圖鑑描述與進化鏈。

支援 Claude Code / Claude Cowork 與 OpenAI Codex 雙平台。

## 安裝

### Claude Code / Claude Cowork

將 skill 複製到專案的 `.claude/skills/` 目錄下：

```bash
mkdir -p .claude/skills
cp -r pokemon-random-intro .claude/skills/
```

安裝完成後，在 Claude Code 中輸入 `/pokemon-random-intro` 即可使用。

### OpenAI Codex

將整個 `pokemon-random-intro/` 目錄放入 Codex 專案的 skill 目錄中，Codex 會自動讀取 `SKILL.md` 與 `agents/openai.yaml`。

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
