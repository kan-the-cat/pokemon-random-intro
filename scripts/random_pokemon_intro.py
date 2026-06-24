#!/usr/bin/env python3
"""Fetch and print a concise Traditional Chinese intro for a random Pokemon."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


API_BASE = "https://pokeapi.co/api/v2/"
LANG_PRIORITY = ("zh-hant", "zh-tw")
FLAVOR_LANG_PRIORITY = ("zh-hant", "zh-tw", "en")

TYPE_ZH_TW = {
    "normal": "一般",
    "fire": "火",
    "water": "水",
    "electric": "電",
    "grass": "草",
    "ice": "冰",
    "fighting": "格鬥",
    "poison": "毒",
    "ground": "地面",
    "flying": "飛行",
    "psychic": "超能力",
    "bug": "蟲",
    "rock": "岩石",
    "ghost": "幽靈",
    "dragon": "龍",
    "dark": "惡",
    "steel": "鋼",
    "fairy": "妖精",
}

SPECIAL_RESPONSES = {
    "ditto": {
        "opening_lines": [
            "嗶⋯⋯嗶嗶⋯⋯",
            "咦⋯⋯這傢伙是⋯⋯！",
        ],
        "closing_line": "你知道嗎？以前 Aiworks 也有一隻百變怪同事，半夜也會在辦公室偷偷工作哦⋯⋯:D",
    },
    "togekiss": {
        "opening_lines": [
            "嗶⋯⋯嗶嗶⋯⋯",
            "天啊！你太幸運了！！！",
        ],
        "closing_line": "這是阿甘最喜歡的寶可夢，他會帶來幸福與和平，看來你今天會很順利哦 :D",
    },
    "gengar": {
        "opening_lines": [
            "嗶⋯⋯嗶嗶⋯⋯總覺得突然變冷了⋯⋯",
        ],
        "closing_line": "Aiworks 偶爾也會出現耿鬼哦！找找看身穿耿鬼的訓練家在哪裡吧 :D",
    },
    "quagsire": {
        "opening_lines": [
            "嗶⋯⋯嗶嗶⋯⋯",
            "⋯⋯這傢伙怎麼盯著我看？",
        ],
        "closing_line": "Aiworks 好像偶爾也會看到沼王的身影，在哪裡呢⋯⋯好像瞬間失憶了 :D",
    },
    "clodsire": {
        "opening_lines": [
            "嗶⋯⋯嗶嗶⋯⋯",
            "等等！嘴巴張得太大了吧！要被吃掉啦！！！",
        ],
        "closing_line": "原來不是要吃掉我，只是打哈欠而已，太好了呢⋯⋯",
    },
}


class PokeApiError(RuntimeError):
    pass


def normalize_language(language: str | None) -> str:
    return (language or "").strip().lower().replace("_", "-")


def fetch_json(url: str, *, timeout: float = 20.0, retries: int = 2) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "codex-pokemon-random-intro/1.0",
    }
    request = urllib.request.Request(url, headers=headers)
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if response.status >= 400:
                    raise PokeApiError(f"HTTP {response.status} from {url}")
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, PokeApiError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(0.4 * (attempt + 1))

    raise PokeApiError(f"Could not fetch {url}: {last_error}")


def api_url(path: str) -> str:
    return f"{API_BASE}{path.lstrip('/')}"


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\f", " ")).strip()


def choose_localized(
    entries: list[dict[str, Any]],
    value_key: str,
    languages: tuple[str, ...] = LANG_PRIORITY,
) -> tuple[str, str] | None:
    by_language: dict[str, tuple[str, str]] = {}

    for entry in entries:
        language = entry.get("language", {}).get("name")
        normalized = normalize_language(language)
        value = entry.get(value_key)
        if normalized and isinstance(value, str) and value.strip():
            by_language.setdefault(normalized, (clean_text(value), language))

    for language in languages:
        if language in by_language:
            return by_language[language]

    return None


def localized_species_name(species: dict[str, Any]) -> tuple[str, str]:
    localized = choose_localized(species.get("names", []), "name")
    if localized:
        return localized
    return "PokéAPI 未提供繁中名稱", "unknown"


def species_name_from_url(url: str, cache: dict[str, dict[str, Any]]) -> tuple[str, str]:
    if url not in cache:
        cache[url] = fetch_json(url)
    return localized_species_name(cache[url])


def choose_flavor_text(species: dict[str, Any]) -> tuple[str, str]:
    localized = choose_localized(
        species.get("flavor_text_entries", []),
        "flavor_text",
        FLAVOR_LANG_PRIORITY,
    )
    if localized:
        return localized
    return "PokéAPI 未提供可用的圖鑑描述。", "unknown"


def choose_default_pokemon_url(species: dict[str, Any]) -> str:
    varieties = species.get("varieties", [])
    for variety in varieties:
        if variety.get("is_default") and variety.get("pokemon", {}).get("url"):
            return variety["pokemon"]["url"]
    for variety in varieties:
        if variety.get("pokemon", {}).get("url"):
            return variety["pokemon"]["url"]
    species_id = species.get("id")
    if species_id is None:
        raise PokeApiError("Species has no usable Pokemon variety")
    return api_url(f"pokemon/{species_id}/")


def nonempty_file(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def download_image(url: str, species_name: str) -> str | None:
    suffix = Path(urllib.parse.urlparse(url).path).suffix or ".png"
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    image_dir = Path(tempfile.gettempdir()) / "pokemon-random-intro-images"
    image_path = image_dir / f"{species_name}-{digest}{suffix}"
    if nonempty_file(image_path):
        return str(image_path)

    try:
        image_dir.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "codex-pokemon-random-intro/1.0"},
        )
        with urllib.request.urlopen(request, timeout=20.0) as response:
            image_path.write_bytes(response.read())
    except (OSError, urllib.error.URLError, TimeoutError):
        return None

    return str(image_path) if nonempty_file(image_path) else None


def choose_image(pokemon: dict[str, Any]) -> str | None:
    sprites = pokemon.get("sprites") or {}
    other = sprites.get("other") or {}
    candidates = [
        ((other.get("official-artwork") or {}).get("front_default")),
        ((other.get("home") or {}).get("front_default")),
        ((other.get("dream_world") or {}).get("front_default")),
        sprites.get("front_default"),
    ]
    return next((url for url in candidates if isinstance(url, str) and url), None)


def pokemon_types(pokemon: dict[str, Any]) -> list[str]:
    ordered_types = sorted(pokemon.get("types", []), key=lambda item: item.get("slot", 0))
    names: list[str] = []
    for entry in ordered_types:
        type_name = entry.get("type", {}).get("name")
        if isinstance(type_name, str):
            names.append(TYPE_ZH_TW.get(type_name, type_name))
    return names


def evolution_paths(chain_node: dict[str, Any], cache: dict[str, dict[str, Any]]) -> list[list[str]]:
    species = chain_node.get("species") or {}
    species_url = species.get("url")
    if species_url:
        current_name = species_name_from_url(species_url, cache)[0]
    else:
        current_name = "PokéAPI 未提供繁中名稱"

    children = chain_node.get("evolves_to") or []
    if not children:
        return [[current_name]]

    paths: list[list[str]] = []
    for child in children:
        for path in evolution_paths(child, cache):
            paths.append([current_name, *path])
    return paths


def format_evolution(paths: list[list[str]]) -> str:
    if not paths:
        return "PokéAPI 未提供進化鏈。"
    unique = []
    seen = set()
    for path in paths:
        rendered = " → ".join(path)
        if rendered not in seen:
            unique.append(rendered)
            seen.add(rendered)
    return "；".join(unique)


def random_species(max_attempts: int = 8) -> dict[str, Any]:
    listing = fetch_json(api_url("pokemon-species/?limit=1"))
    count = int(listing.get("count") or 0)
    if count <= 0:
        raise PokeApiError("PokéAPI returned no species count")

    last_error: Exception | None = None
    for _ in range(max_attempts):
        species_id = random.randint(1, count)
        try:
            return fetch_json(api_url(f"pokemon-species/{species_id}/"))
        except PokeApiError as exc:
            last_error = exc

    raise PokeApiError(f"Could not fetch a random species: {last_error}")


def build_profile(species_ref: str | None = None) -> dict[str, Any]:
    species = fetch_json(api_url(f"pokemon-species/{species_ref}/")) if species_ref else random_species()
    pokemon = fetch_json(choose_default_pokemon_url(species))
    evolution = fetch_json(species["evolution_chain"]["url"])

    species_cache: dict[str, dict[str, Any]] = {}
    name, name_language = localized_species_name(species)
    flavor, flavor_language = choose_flavor_text(species)
    types = pokemon_types(pokemon)
    paths = evolution_paths(evolution.get("chain", {}), species_cache)
    special = SPECIAL_RESPONSES.get(species.get("name"), {})
    image_url = choose_image(pokemon)

    return {
        "species": species.get("name"),
        "name": name,
        "name_language": name_language,
        "types": types,
        "evolution_chain": format_evolution(paths),
        "flavor_text": flavor,
        "flavor_text_language": flavor_language,
        "flavor_text_needs_translation": normalize_language(flavor_language) == "en",
        "image_url": image_url,
        "image": download_image(image_url, species.get("name") or "pokemon") if image_url else None,
        "opening_lines": special.get("opening_lines", ["嗶⋯⋯嗶嗶⋯⋯"]),
        "closing_line": special.get("closing_line"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a random Pokemon profile from PokeAPI.")
    parser.add_argument("--species", help="Fetch a specific pokemon-species id or name for testing.")
    args = parser.parse_args()

    try:
        profile = build_profile(args.species)
    except PokeApiError:
        print("無法從 PokéAPI 取得隨機寶可夢資料，請稍後再試。", file=sys.stderr)
        return 1

    print(json.dumps(profile, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
