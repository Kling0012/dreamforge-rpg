# Making your mod work with Dreamforge RPG

**English** | [日本語](MODDING.ja.md)

This guide is for authors of other Shape of Dreams mods, especially mods that add a new traveler (hero). With one JSON file, your traveler can use Dreamforge's gear, star map and co-op features.

- You write no C# code for Dreamforge and add no reference to it.
- Your mod keeps working when Dreamforge is not installed. The file is simply not read.
- Load order does not matter.
- A mistake in the file disables only that declaration. Neither Dreamforge nor your mod stops.

The connector is available from the Dreamforge release that first lists it in the [patch notes](../CHANGELOG.md).

## What the connector does and does not do

Your mod still adds the traveler itself through the base game: the Hero type, its prefab, skills, assets and unlock state. Dreamforge does not do this for you.

Once your traveler exists in the game, Dreamforge picks it up automatically, even without a declaration file. It gets equipment, the generic star map and its saved progress. A declaration file adds:

- the display name in Japanese, English and Chinese
- whether the traveler fights in melee (Dreamforge's melee co-op rules)
- display names for the traveler's memories (skills) in Dreamforge's screens
- a star map of its own (stat stars and keystones), checked against limits taken from the built-in travelers

A declaration cannot change the built-in nine travelers or their stars. It also cannot set per-traveler difficulty or reward scaling, pair combos, memory routes or special-effect stars. Declared travelers always use the default scaling.

## Quick start

Put a file named `dreamforge.json` in the root of your mod folder, next to `about/`:

```
MyHeroMod/
  about/
    metadata.json
  MyHeroMod.dll
  dreamforge.json
```

Minimal file (name only, generic star map):

```json
{
  "dreamforgeApi": 1,
  "heroes": [
    { "key": "Hero_Nova", "name": { "en": "Nova", "ja": "ノヴァ", "zh": "诺瓦" } }
  ]
}
```

`key` is the class name of your Hero subclass. Dreamforge identifies travelers by this name, so keep it stable once players have saves.

## Full example

```json
{
  "dreamforgeApi": 1,
  "heroes": [
    {
      "key": "Hero_Nova",
      "name": { "en": "Nova", "ja": "ノヴァ", "zh": "诺瓦" },
      "melee": false,
      "memories": [
        { "key": "St_Q_NovaBlink", "name": { "en": "Blink", "ja": "瞬き", "zh": "闪烁" } }
      ],
      "starTree": {
        "nodes": [
          { "id": "edge", "stat": "AttackPct", "perRank": 3, "maxRank": 3,
            "name": { "en": "Edge", "ja": "刃", "zh": "锋刃" } },
          { "id": "focus", "stat": "CritDamagePct", "perRank": 2, "maxRank": 3, "tier": 2,
            "name": { "en": "Focus", "ja": "集中", "zh": "专注" } },
          { "id": "nova_core", "keystone": true, "stat": "CritDamagePct", "value": 20,
            "name": { "en": "Nova Core", "ja": "新星の核", "zh": "新星之核" },
            "description": { "en": "Critical damage +20%.", "ja": "会心ダメージ +20%。", "zh": "暴击伤害 +20%。" } }
        ]
      }
    }
  ]
}
```

## Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `dreamforgeApi` | yes | Format version. Use `1`. |
| `heroes` | yes | List of travelers. One file can declare several. |
| `key` | yes | Class name of the Hero subclass. Starts with `Hero_`; letters, digits and `_`, up to 64 characters. |
| `name` | no | Display name with `en`, `ja` and `zh`. A missing language falls back to `en`, then to the key without `Hero_`. |
| `melee` | no | `true` for a melee traveler. Default `false`. |
| `memories` | no | Display names for the traveler's memories (`key` is the memory class name). Display only; this does not add them to Dreamforge's loot or links. |
| `starTree` | no | The traveler's own star map. Without it, the traveler uses the generic star map. |
| `nodes[].id` | yes | Lowercase letters, digits and `_`, up to 32 characters, unique within the traveler. The saved star ID is `x.<key>.<id>`. |
| `nodes[].stat` | yes | Stat name, such as `AttackPct`. See "Star map limits". |
| `nodes[].perRank`, `maxRank` | for normal stars | Value per rank and number of ranks. |
| `nodes[].tier` | no | `1` (inner ring, default) or `2` (outer ring). |
| `nodes[].keystone`, `value`, `description` | for keystones | A keystone. It uses the same mastery requirement and cost as the built-in keystones. |
| `nodes[].name` | no | Display name. Defaults to `id`. |

Unknown fields are ignored, so a file written for a newer format still loads the parts this version understands.

## Star map limits

Limits are not fixed numbers in the code. Dreamforge works them out at startup from the core star maps of the built-in travelers, so they follow future balance changes.

- Only stats that appear on built-in normal stars can be used.
- For each stat, `perRank` and `maxRank` cannot exceed the highest values used on built-in stars with that stat.
- A keystone's `value` cannot exceed one fully ranked built-in star of the same stat.
- The number of normal stars and keystones cannot exceed the largest built-in traveler.

Values over a limit are not rounded down. The traveler is still registered, but it uses the generic star map, and the reason is written to the report file. Stars are placed automatically; positions cannot be declared in version 1.

## Checking your file

Every time Dreamforge reads declarations, it rewrites a report:

```
<persistentDataPath>/QuickSave/Mods/DreamforgeRPG/connector-report.txt
Windows: %USERPROFILE%/AppData/LocalLow/Lizard Smoothie/Shape of Dreams/QuickSave/Mods/DreamforgeRPG/connector-report.txt
```

It lists the files read, the travelers accepted or rejected (with reasons), and the current limits for every stat. `Player.log` has the same messages, prefixed with `[Dreamforge/Connector]`.

Common rejections:

- The file is not valid JSON, or `dreamforgeApi` is missing or newer than this Dreamforge: the whole file is skipped.
- `key` is one of the built-in travelers, or another mod already declared it: only that traveler is skipped. When two mods declare the same key, the mod earlier in the game's mod order wins.
- A star is over a limit: the traveler uses the generic star map.

## Co-op

- Dreamforge players exchange their lists of declared travelers when both sides support the connector. Older Dreamforge versions and players without Dreamforge receive nothing new, and nothing changes for them.
- The host's declarations decide star effects. If a guest plays a declared traveler that the host does not have, or the host has a different version of its file, that traveler's star bonuses are off in that room. Equipment still works. Both sides get one notice.
- For the same results in co-op, everyone should use the same version of your mod.

## Saves

- Progress for your traveler is saved under its key, like any other traveler.
- If a player removes your mod, Dreamforge keeps that traveler's saved progress untouched. Reinstalling the mod brings it back.
- If you remove or rename stars in a later version, allocations to stars that no longer exist stop having an effect. Their points return to the player as unspent. The records are kept, so restoring the stars restores the allocation.

## Optional: runtime API

You only need this if you want to build declarations in code or check Dreamforge from your mod. The type is `Dreamforge.Api.HeroConnector` (public, static).

| Member | Meaning |
| --- | --- |
| `int ApiVersion` | `1` |
| `string DreamforgeVersion` | Dreamforge's version |
| `bool RegisterHeroes(string json, string sourceModId, out string error)` | Registers the same JSON as `dreamforge.json`. During a run, the registration is held until the run ends; the method returns `true` and says so in `error`. |
| `bool IsHeroRegistered(string heroKey)` | Whether the traveler is registered |
| `string[] GetRegisteredHeroes()` | Keys of all declared travelers |
| `string GetReport()` | The same text as the report file |

None of the members throw. The game loads each mod's assembly under a changed name, so find the type by its full name instead of referencing the DLL:

```csharp
static System.Type FindDreamforgeConnector()
{
    foreach (var asm in System.AppDomain.CurrentDomain.GetAssemblies())
    {
        var t = asm.GetType("Dreamforge.Api.HeroConnector", false);
        if (t != null) return t;
    }
    return null; // Dreamforge is not installed
}
```

If your mod loads before Dreamforge, this returns `null` at that moment. Call it later, for example from the game's `DewMod.onModLoadEnded` event, or just use `dreamforge.json`, which does not depend on load order.

## Compatibility promise

- Fields in `dreamforgeApi: 1` keep their meaning. New features arrive as new fields, and old files keep loading.
- If a meaning ever has to change, the format becomes `2`, and version 1 files are still read.
- Public members of `Dreamforge.Api` are not removed while their API version is supported.

## Questions and requests

Open an [Issue](https://github.com/Kling0012/dreamforge-rpg/issues/new/choose). Requests for more connection points are welcome, for example mods that add memories, essences or relics.
