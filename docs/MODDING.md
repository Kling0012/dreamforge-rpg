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
- a star map of its own: stat stars, memory stars, power stars, choice stars, clusters, gimmick stars and keystones, with your own connections and positions, checked against limits taken from the built-in travelers

A declaration cannot change the built-in nine travelers or their stars. It also cannot set per-traveler difficulty or reward scaling. New scripted mechanisms and pair combos cannot be written, but the ones on built-in stars can be copied (see `authoredEffect`). Declared travelers always use the default scaling.

The extended star-map fields (everything beyond `stat`, `perRank`, `maxRank`, `tier`, `keystone`, `value` and `description`) arrive in the first release after v3.8.85.

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

### Traveler

| Field | Required | Meaning |
| --- | --- | --- |
| `dreamforgeApi` | yes | Format version. Use `1`. |
| `heroes` | yes | List of travelers. One file can declare several. |
| `key` | yes | Class name of the Hero subclass. Starts with `Hero_`; letters, digits and `_`, up to 64 characters. |
| `name` | no | Display name with `en`, `ja` and `zh`. A missing language falls back to `en`, then to the key without `Hero_`. |
| `melee` | no | `true` for a melee traveler. Default `false`. |
| `memories` | no | The traveler's memories (`key` is the memory class name) with display names. Memory stars can target them. They are not added to Dreamforge's loot or links. |
| `starTree` | no | The traveler's own star map (`nodes`, and optionally `clusters`). Without it, the traveler uses the generic star map. |

### Stars (`starTree.nodes[]`)

Every star has an `id`: lowercase letters, digits and `_`, up to 32 characters, unique within the traveler. The saved star ID is `x.<key>.<id>`. `name` is the display name (defaults to `id`).

Each star has exactly one effect:

| Effect | Fields | Meaning |
| --- | --- | --- |
| Stat | `stat`, `perRank`, `maxRank` | A stat bonus, such as `AttackPct`. |
| Memory star | `link`, `memory`, `perRank`, `maxRank` | A bonus tied to one memory, using a link kind from the built-in memory routes (for example `MemoryDamage`, `MemoryHaste`, `MemorySurge`, `Guard`). `memory` is one of your `memories` or a base-game memory. |
| Power | `power`, `perRank`, `maxRank` | A power star, such as `Aegis`. With `"kind": "Notable"` it is shown as a notable. |
| Keystone | `keystone: true`, `value`, plus `stat` or `power` | A keystone. Stat keystones need `description`; power keystones use the power's own text when `description` is missing. Same mastery requirement as the built-in keystones. |
| Choice | `choices`, `maxRank` | The player picks one of the listed options. Each option is a normal star without `id`, connections or position. |
| Gimmick | `gimmick`, `memory`, `maxRank` | Reuses the gimmick of a built-in star, given by that star's ID (for example `h.vesper.route.resolve.2`). New gimmicks cannot be declared. |
| Gimmick boost | `gimmickBoost`, `memory`, `maxRank` | Strengthens the gimmick on that memory. |
| Gimmick parameter | `gimmickParam`, `perRank`, `maxRank`, `memory` | Raises one parameter of the gimmick, such as `Duration` or `Radius`. |
| Memory modifier | `nativeModifier` or `scopedModifier`, `memory`, `maxRank` | Damage or haste for one memory, or a scoped bonus to other stars' effects, using the same units as built-in stars (100 units = 1%). |
| Copied mechanism | `authoredEffect`, `maxRank` | Copies a scripted mechanism, pair combo or keystone from a built-in star. See below. |

Placement and access, all optional:

| Field | Meaning |
| --- | --- |
| `requires` | IDs of stars in the same tree. Taking any one of them opens this star. An empty list connects it to the center. Without `requires`, connections are automatic. |
| `center` | `true` also connects the star to the center; `false` keeps an empty `requires` from doing so. |
| `requiredStars`, `requiredAnyStars` | Stars that must already be taken (all of them / any one), in addition to the connections. |
| `position` | `{ "ring": 2, "angle": -45 }` or `{ "x": 120, "y": -30 }`. Angle 0 is right, 90 is down. Without it, placement is automatic. |
| `tier` | `1` (inner ring, default) or `2` (outer ring) for automatic placement. |
| `cluster`, `clusterOrder` | The local ID of a cluster in `starTree.clusters` (each with `id` and `name`), and the order inside it. |
| `isDreamRing` | Marks the star as part of the dream ring. |
| `rankCost` | Points per rank. Defaults to the built-in cost. |

Example of the extra star types, added to the `nodes` of the full example:

```json
{ "id": "blink_damage", "link": "MemoryDamage", "memory": "St_Q_NovaBlink",
  "perRank": 1, "maxRank": 3, "requires": ["edge", "focus"],
  "position": { "ring": 2, "angle": -45 } },
{ "id": "aegis", "power": "Aegis", "perRank": 1, "maxRank": 3, "requires": ["blink_damage"] },
{ "id": "pick", "maxRank": 1, "requires": ["aegis"], "choices": [
    { "stat": "AttackPct", "perRank": 1, "maxRank": 1 },
    { "power": "Aegis", "perRank": 1, "maxRank": 1 } ] }
```

Connections work both ways, like the built-in star maps. If the connections form a cycle, point to an unknown ID, or leave a star unreachable from the center, the traveler uses the generic star map and the reason goes to the report file.

### Reusing built-in mechanisms (`authoredEffect`)

Many built-in stars carry scripted mechanisms: effects that trigger when a memory hits, kills or is used, pair combos between two memories, and the mechanism keystones. You cannot write new mechanisms, but you can copy one from a built-in star and attach it to your own stars and memories.

```json
{ "id": "ward", "authoredEffect": { "hero": "Hero_Vesper", "star": "outer.ward.a2" },
  "maxRank": 1, "requires": ["edge"] }
```

- `hero` and `star` name the built-in star to copy. For an option of a choice star, give the parent star and `"option": 0` (0-based).
- The copied star keeps its numbers, triggers and rank table. You set `maxRank` (no higher than the original) and may set `rankCost` (no lower than the original). `perRank`, `value` and `gimmick` cannot be combined with it. A copied keystone needs `keystone: true`.
- `starTree.effectBindings` maps what the original refers to onto your tree:
  - `stars`: original star ID → your local star ID. Required for every star the mechanism refers to (its owner, prerequisites, both ends of a pair-combo bridge, keystone targets).
  - `memories` (optional): original memory → your memory or a base-game memory. Memories you leave out stay as they are.

```json
"effectBindings": {
  "stars": { "outer.ward.a2": "ward" }
}
```

- Mechanisms react to the game's usual memory events (use, hit, kill, owned attacks). If your memory deals damage or summons through its own code path without those events, a copied mechanism may never trigger. The report file lists your mapped memories with this warning.
- A few mechanisms are tied to one specific built-in memory or keystone and cannot be moved; those declarations are rejected with the reason.

With this, the built-in Vesper and Bismuth star maps can be rebuilt from a declaration file: every star, including all keystones, except Vesper's four expedition-training stars. The [examples](examples/) folder has both as reference declarations; their star IDs are the ones you can copy.

Unknown fields are ignored, so a file written for a newer format still loads the parts this version understands.

## Star map limits

Limits are not fixed numbers in the code. Dreamforge works them out at startup from the star maps of the built-in travelers, so they follow future balance changes.

- Only stats, link kinds, powers, gimmick parameters and modifiers that appear on built-in stars can be used.
- For each kind, a star must stay within all three of: the highest value per rank, the highest number of ranks, and the highest total (value × ranks) of a single built-in star of that kind. For example, a memory-damage star of 150.21% per rank is allowed with 1 rank but not with 3.
- The numbers of stars, keystones, choice stars, options per choice and clusters, and `rankCost`, cannot exceed the largest built-in traveler. A star map can be as large as a built-in one (around 900 stars).

Values over a limit are not rounded down. The traveler is still registered, but it uses the generic star map, and the reason is written to the report file. The report file lists every current limit.

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
