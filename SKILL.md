---
name: pokemon-random-intro
description: Fetch and introduce one random Pokemon from PokeAPI. Use only when the user explicitly invokes this skill as $pokemon-random-intro or directly requests this exact skill. Do not invoke implicitly during general Pokemon, PokéAPI, image, writing, translation, coding, or work tasks.
---

# Pokemon Random Intro

## Workflow

Run the bundled Python script `random_pokemon_intro.py` located in the `scripts/` subdirectory of this skill's directory. For example, if this skill is installed at `.claude/skills/pokemon-random-intro/`, run:

```bash
python3 .claude/skills/pokemon-random-intro/scripts/random_pokemon_intro.py
```

Adjust the path to match the actual location of this skill directory in your project.

The script calls PokéAPI, randomly selects one `pokemon-species`, fetches the default Pokemon form, resolves localized names, types, evolution chain, Pokedex flavor text, and artwork when available. It returns structured JSON for rendering. The `image` field is a local absolute image path when download succeeds.

When this skill is invoked, do not add any preface, progress update, explanation, source note, or closing sentence. Run the script, translate `flavor_text` to `zh-tw` only if `flavor_text_needs_translation` is `true`, then return only the rendered capture message.

The output format must be:

```text
[opening_lines, one paragraph per item]

你抓到了 [寶可夢名稱]

[圖片]

[寶可夢名稱]

[屬性]系寶可夢

[圖鑑描述]

[進化鏈]

[closing_line, only when present]
```

Use `opening_lines` exactly as provided by the script. If multiple opening lines are present, render each as its own paragraph. If `closing_line` is present, append it as its own final paragraph after the evolution chain.

Use blank lines exactly as shown so mobile Markdown renderers treat each item as a separate paragraph. Do not rely on single newlines for visual separation. Keep the Pokedex description and evolution chain in separate paragraphs.

Use only `zh-tw` visible text. Do not include JSON, language metadata, battle stats, abilities, moves, height, weight, trivia, labels, headings, or extra commentary unless the user asks.

## Data Rules

- Prefer `zh-Hant`, `zh-hant`, or `zh-tw` localized values.
- If the Pokedex flavor text lacks zh-tw data but has English data, translate the English flavor text into natural zh-tw.
- If no usable Pokedex flavor text exists, use a zh-tw unavailable-data sentence.
- Use `pokemon-species` for species names, Pokedex flavor text, and evolution-chain URL.
- Use `pokemon` for types and sprites.
- Use the default variety from `pokemon-species.varieties` when choosing which Pokemon form to fetch.
- Prefer official artwork from `sprites.other.official-artwork.front_default`; fall back to other sprite URLs only if official artwork is unavailable.
- For the image, choose based on platform:
  - **Codex**: Use `image` (the local absolute path) in the Markdown image tag: `![name](image)`.
  - **Claude, Claude Cowork, and Claude Code**: Use `image_url` (the remote URL) in the Markdown image tag: `![name](image_url)`. Do NOT use the local `image` path in Markdown, as Claude platforms may not be able to access server-side temp files.
- Make only the small number of requests needed for one random Pokemon. PokéAPI is free and keyless, but its fair use policy asks clients to avoid excessive requests.

## Special Responses

The script may return special `opening_lines` and `closing_line` for selected Pokemon. Render these fields exactly as provided, with no translation, paraphrase, or extra explanation.

## Failure Handling

If network access is unavailable, PokéAPI returns an error, or no valid species can be fetched after retries, tell the user you could not retrieve a random Pokemon from PokéAPI right now. Do not invent missing Pokemon data.
