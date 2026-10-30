# Translating Dreamforge RPG

[日本語の概要](#日本語の概要) · [中文概要](#中文概要)

Dreamforge RPG ships in Japanese, English and Chinese (Simplified). Any other language can be added by the community: you write one translation file and open a pull request in this repository. Checks run automatically, and once your pull request is merged, the translation is included in the next release of the mod on the [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3822274988).

You do not need to translate everything. Text without a translation is shown in English, so you can start small and improve it over time.

## Contents

1. [What you need](#1-what-you-need)
2. [Start a translation](#2-start-a-translation)
3. [The translation file](#3-the-translation-file)
4. [Rules](#4-rules)
5. [Test it in the game](#5-test-it-in-the-game)
6. [Send a pull request](#6-send-a-pull-request)
7. [Keep it up to date](#7-keep-it-up-to-date)
8. [Questions and problems](#8-questions-and-problems)

## 1. What you need

- A GitHub account.
- A text editor that saves UTF-8 (for example VS Code or Notepad++).
- Optional: Python 3, to run the same check as the automatic one before you send your pull request.
- Optional: the game with Dreamforge RPG installed, to see your translation in place.

## 2. Start a translation

1. Open [`translations/template.json`](../translations/template.json). It lists every English text the mod shows, as of the latest release.
2. Check [`translations/COVERAGE.md`](../translations/COVERAGE.md). If your language already exists, improve that file instead of starting a new one.
3. Copy the template to `translations/<code>.json`, where `<code>` is your language code: `fr` (French), `de` (German), `es` (Spanish), `pt-BR` (Brazilian Portuguese), `ko` (Korean), `ru` (Russian), `zh-TW` (Chinese, Traditional) and so on.
4. Fill in `language`, `name` and `strings` as described below.

## 3. The translation file

```json
{
  "language": "fr",
  "name": "Français",
  "authors": ["your-github-name"],
  "strings": {
    "Forge": "Forge",
    "Salvage all": "Tout recycler",
    "Deal {0} damage": "Inflige {0} dégâts"
  }
}
```

| Field | Meaning |
|---|---|
| `language` | The language code. It must match the file name (`fr.json` → `fr`). `ja`, `en` and `zh` are built in and cannot be used. |
| `name` | The language's own name. It is shown on the language button in the mod. |
| `authors` | Optional. GitHub names of the translators. They are credited in the patch notes when a new language is added. |
| `strings` | Pairs of English text (key) and your translation (value). Copy the keys from the template exactly, including spaces and punctuation. |

- An empty value (`""`) or a missing key means "not translated yet"; the English text is shown.
- Keys that are no longer in the template are ignored by the mod. The check reports them as warnings, and you can delete them.
- Keep the file in UTF-8. Escape double quotes inside text as `\"` and line breaks as `\n`.

## 4. Rules

The automatic check rejects a file that breaks any of these rules:

- **Placeholders**: keep `{0}`, `{1}` … exactly as in the English text. You may move them within the sentence.
- **Rich text tags**: keep tags such as `<b>`, `</b>`, `<i>`, `<color=#ffcc00>`, `</color>`, `<size=...>` with the same kinds and counts as in the English text. Do not add new tags.
- **No links**: no URLs (`http`, `www.`, `://`) or contact details.
- **Length**: at most four times the English text plus 40 characters. Long text may not fit on screen.
- **Characters**: no control characters other than line breaks and tabs.
- **File**: valid JSON, UTF-8, 2 MB or less.
- **Pull request**: change only files under `translations/` (and not `template.json` or `COVERAGE.md`), at most three files at once.

Translations are also screened for content. Pull requests with insults, advertising, unrelated text or hidden messages are not merged. Please translate the meaning faithfully; you do not need to translate word for word.

Tips:

- Game terms appear many times. Decide on one word for each term (Relic, Forge, Delve, Secure, Star map, Traveler, Essence and so on) and use it consistently.
- Names of base-game items and characters should follow the official translation of *Shape of Dreams* in your language, if there is one.
- Short labels on buttons and tabs have little room. Prefer short words there.

## 5. Test it in the game

1. Put your file in your local language folder:
   - Windows: `%USERPROFILE%/AppData/LocalLow/Lizard Smoothie/Shape of Dreams/QuickSave/Mods/DreamforgeRPG/lang/`
   - Other systems: `<persistentDataPath>/QuickSave/Mods/DreamforgeRPG/lang/`
2. Start the game, open the Dreamforge menu (F6), go to Settings and press the language button until your language appears. The order is 日本語 → English → 中文 → added languages.
3. A file in this folder takes priority over the one shipped with the mod, so you can test changes before they are released.
4. To find text you have not translated yet, turn on `translationDump` in the mod settings. While your language is selected, the mod writes `missing-<code>.json` in the same folder, listing the English text it showed without a translation. Copy those keys into your file.

Known limits:

- Some text is built from numbers at run time (for example "+12% attack"). Part of it still appears in English even with a full translation. This will shrink as the mod moves that text to placeholders.
- Text from the base game is translated by the base game, not by this file.
- Some languages need fonts that are not installed on every PC. If letters show as boxes, mention it in your pull request.

## 6. Send a pull request

1. Fork this repository, add or edit `translations/<code>.json`, and open a pull request to `main`.
2. Optional: run the check yourself first:
   ```
   python3 tools/check_translations.py --template translations/template.json translations/fr.json
   ```
3. The `translations` check runs on your pull request. If it fails, open its details: the summary lists each problem with the first part of the English text it belongs to. Fix the file and push again.
4. When the check passes and the content screening finds no problem, the pull request is merged automatically. If a maintainer needs to look at it, you will see a comment.
5. Merged translations are included in the next release of the mod.

## 7. Keep it up to date

- `template.json` is updated with every release. New or changed English text appears there; when the English text changes, the old key stops matching and that line shows in English until it is translated again.
- `COVERAGE.md` shows how much of each language is translated.
- Anyone may improve an existing translation. Add yourself to `authors` when you do.

## 8. Questions and problems

Open an [Issue](https://github.com/Kling0012/dreamforge-rpg/issues/new/choose) for questions about translating, wrong text in the game, or problems with the check.

## 日本語の概要

Dreamforge RPG は日本語・英語・中国語（簡体字）に対応しています。ほかの言語は、翻訳ファイル `translations/<言語コード>.json` を作ってこのリポジトリに Pull Request を送ると追加できます。訳していない文は英語で表示されるので、途中までの翻訳でもかまいません。自動の検査と内容の確認に通るとマージされ、次のリリースで Steam ワークショップの MOD に入ります。ファイルの形式、検査の規則、ゲーム内で試す方法は、上の英語の説明にあります。

## 中文概要

Dreamforge RPG 支持日语、英语和简体中文。其他语言可以由社区添加：创建翻译文件 `translations/<语言代码>.json`，并向本仓库提交 Pull Request。未翻译的文本会以英文显示，因此部分翻译也可以提交。通过自动检查和内容审核后会自动合并，并包含在 Steam 创意工坊的下一个版本中。文件格式、检查规则和在游戏中测试的方法，请参阅上方的英文说明。
