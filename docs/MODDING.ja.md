# Dreamforge RPG と連携する MOD の作り方

[English](MODDING.md) | **日本語**

ほかの Shape of Dreams 用 MOD の作者向けの案内です。特に、新しい旅人（ヒーロー）を足す MOD を想定しています。JSON ファイルを1つ置くだけで、その旅人が Dreamforge の装備・星図・協力プレイに対応します。

- Dreamforge のための C# のコードも、Dreamforge への参照も要りません。
- Dreamforge が入っていない環境でも、あなたの MOD はそのまま動きます（ファイルが読まれないだけです）。
- MOD の読み込み順に関係なく動きます。
- ファイルに誤りがあっても止まるのはその宣言だけで、Dreamforge もあなたの MOD も止まりません。

この連携機能（コネクタ）は、[パッチノート](../CHANGELOG.md)に初めて載ったバージョンの Dreamforge から使えます。

## コネクタでできること・できないこと

旅人そのもの（Hero の型、プレハブ、スキル、アセット、解錠）は、これまでどおりあなたの MOD が本体の仕組みで追加します。Dreamforge が代わりに行うことはありません。

ゲームに旅人が加われば、宣言ファイルが無くても Dreamforge はその旅人を扱います。装備と汎用の星図が使え、進み具合も保存されます。宣言ファイルを置くと、次のことが加わります。

- 日本語・英語・中国語の表示名
- 近接の旅人かどうか（Dreamforge の協力プレイの近接向けの扱い）
- Dreamforge の画面に出る、その旅人の記憶（スキル）の表示名
- 専用の星図。能力値の星、記憶の星、Power の星、選択の星、星群、仕掛けの星、キーストーンを、つながりと位置も含めて決められます。上限は既存の旅人の星図から決まります。

宣言では、既存の9人の旅人とその星は変えられません。旅人ごとの難易度・報酬の倍率も宣言できません。新しい仕掛けやペア連携は書けませんが、既存の星が持つものは複製して使えます（`authoredEffect` を見てください）。宣言した旅人の倍率は、常に既定の値です。

星図の拡張の欄（`stat`・`perRank`・`maxRank`・`tier`・`keystone`・`value`・`description` 以外の欄）は、v3.8.85 の次のリリースから使えます。

## まず試す

MOD フォルダの直下（`about/` と同じ階層）に `dreamforge.json` を置きます。

```
MyHeroMod/
  about/
    metadata.json
  MyHeroMod.dll
  dreamforge.json
```

最小のファイル（名前だけで、星図は汎用）は次のとおりです。

```json
{
  "dreamforgeApi": 1,
  "heroes": [
    { "key": "Hero_Nova", "name": { "en": "Nova", "ja": "ノヴァ", "zh": "诺瓦" } }
  ]
}
```

`key` は Hero のサブクラスの型名です。Dreamforge はこの名前で旅人を見分けるので、プレイヤーのセーブができたあとは変えないでください。

## すべての欄を使った例

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

## 欄の説明

### 旅人

| 欄 | 必須 | 内容 |
| --- | --- | --- |
| `dreamforgeApi` | 必須 | 形式のバージョン。`1` を書きます。 |
| `heroes` | 必須 | 旅人の一覧。1つのファイルに複数の旅人を書けます。 |
| `key` | 必須 | Hero のサブクラスの型名。`Hero_` で始まる英数字と `_` で、64文字まで。 |
| `name` | 任意 | 表示名（`en`・`ja`・`zh`）。足りない言語は `en`、次に `key` から `Hero_` を除いた名前になります。 |
| `melee` | 任意 | 近接の旅人なら `true`。既定は `false`。 |
| `memories` | 任意 | その旅人の記憶（`key` は記憶の型名）と表示名。記憶の星の対象にできます。Dreamforge の報酬やリンクには入りません。 |
| `starTree` | 任意 | 専用の星図（`nodes` と、必要なら `clusters`）。無ければ汎用の星図を使います。 |

### 星（`starTree.nodes[]`）

どの星にも `id` を付けます。英小文字・数字・`_` で32文字まで、旅人の中で重ならないようにします。保存される星の ID は `x.<key>.<id>` です。`name` は表示名で、無ければ `id` を表示します。

星の効果は、次のどれか1つです。

| 効果 | 欄 | 内容 |
| --- | --- | --- |
| 能力値 | `stat`、`perRank`、`maxRank` | `AttackPct` などの能力値を上げます。 |
| 記憶の星 | `link`、`memory`、`perRank`、`maxRank` | 1つの記憶に結びついた効果です。種類は既存の記憶ルートで使われているもの（`MemoryDamage`・`MemoryHaste`・`MemorySurge`・`Guard` など）。`memory` は `memories` で宣言した記憶か、本体の記憶です。 |
| Power | `power`、`perRank`、`maxRank` | `Aegis` などの Power の星です。`"kind": "Notable"` を付けると Notable として表示します。 |
| キーストーン | `keystone: true`、`value`、`stat` か `power` | キーストーンです。能力値のキーストーンには `description` が要ります。Power のキーストーンは、`description` が無ければ Power の説明文を使います。熟練度の条件は既存のキーストーンと同じです。 |
| 選択の星 | `choices`、`maxRank` | 挙げた選択肢から1つを選ぶ星です。選択肢は、`id`・つながり・位置を持たない通常の星です。 |
| 仕掛け | `gimmick`、`memory`、`maxRank` | 既存の星の仕掛けを、その星の ID（例 `h.vesper.route.resolve.2`）で指して使います。新しい仕掛けは作れません。 |
| 仕掛けの強化 | `gimmickBoost`、`memory`、`maxRank` | その記憶の仕掛けを強めます。 |
| 仕掛けのパラメータ | `gimmickParam`、`perRank`、`maxRank`、`memory` | 仕掛けの `Duration`・`Radius` などのパラメータを上げます。 |
| 記憶の修飾 | `nativeModifier` か `scopedModifier`、`memory`、`maxRank` | 1つの記憶のダメージや加速、またはほかの星の効果への上乗せです。単位は既存の星と同じです（100 units が 1%）。 |
| 既存の仕掛けの複製 | `authoredEffect`、`maxRank` | 既存の星の仕掛け・ペア連携・キーストーンを複製します。下の節を見てください。 |

置き方と取り方の欄は次のとおりです。どれも任意です。

| 欄 | 内容 |
| --- | --- |
| `requires` | 同じ星図の星の `id` の一覧。どれか1つを取ると、この星へ進めます。空の一覧なら中心につながります。書かなければ自動でつなぎます。 |
| `center` | `true` なら中心にもつなぎます。`false` なら、空の `requires` でも中心にはつなぎません。 |
| `requiredStars`・`requiredAnyStars` | つながりとは別に、先に取っておく必要がある星（すべて／どれか1つ）。 |
| `position` | `{ "ring": 2, "angle": -45 }` か `{ "x": 120, "y": -30 }`。角度は 0 が右、90 が下です。書かなければ自動で配置します。 |
| `tier` | 自動配置のときの輪。`1`（内側。既定）か `2`（外側）。 |
| `cluster`・`clusterOrder` | `starTree.clusters`（それぞれ `id` と `name` を持つ）の星群の ID と、星群の中での順番。 |
| `isDreamRing` | 夢の輪の星として扱います。 |
| `rankCost` | 1段あたりのポイント。書かなければ既存と同じ費用です。 |

拡張の星の例です。「すべての欄を使った例」の `nodes` に足して使います。

```json
{ "id": "blink_damage", "link": "MemoryDamage", "memory": "St_Q_NovaBlink",
  "perRank": 1, "maxRank": 3, "requires": ["edge", "focus"],
  "position": { "ring": 2, "angle": -45 } },
{ "id": "aegis", "power": "Aegis", "perRank": 1, "maxRank": 3, "requires": ["blink_damage"] },
{ "id": "pick", "maxRank": 1, "requires": ["aegis"], "choices": [
    { "stat": "AttackPct", "perRank": 1, "maxRank": 1 },
    { "power": "Aegis", "perRank": 1, "maxRank": 1 } ] }
```

つながりは、既存の星図と同じく両向きです。つながりが循環している、ない `id` を指している、中心から届かない星がある、のどれかに当たると、その旅人は汎用の星図になり、理由が報告ファイルに書かれます。

### 既存の仕掛けを使う（`authoredEffect`）

既存の星の多くは、記憶を当てた・倒した・使ったときに発動する仕掛けや、2つの記憶のペア連携、仕掛け付きのキーストーンを持っています。新しい仕掛けは書けませんが、既存の星の仕掛けを複製して、自分の星と記憶に付けられます。

```json
{ "id": "ward", "authoredEffect": { "hero": "Hero_Vesper", "star": "outer.ward.a2" },
  "maxRank": 1, "requires": ["edge"] }
```

- `hero` と `star` で、複製する既存の星を指します。選択の星の選択肢を指すときは、親の星と `"option": 0`（0 から数える）を書きます。
- 複製した星の数値・発動条件・段数表は元のままです。`maxRank` は元以下、`rankCost` は元以上にできます。`perRank`・`value`・`gimmick` とは一緒に使えません。キーストーンを複製するときは `keystone: true` を書きます。
- 元の星が参照しているものを、`starTree.effectBindings` で自分の星図に付け替えます。
  - `stars`: 元の星の ID → 自分の星の ID。仕掛けが参照する星（持ち主の星、取得条件、ペア連携の両端、キーストーンの対象）はすべて書きます。
  - `memories`（任意）: 元の記憶 → 自分の記憶か本体の記憶。書かなかった記憶は元のままです。

```json
"effectBindings": {
  "stars": { "outer.ward.a2": "ward" }
}
```

- 仕掛けは、ゲームのふつうの記憶の出来事（使用・命中・撃破・自分の攻撃）で動きます。あなたの記憶が、これらの出来事を出さない独自の処理でダメージを与えたり召喚したりすると、複製した仕掛けが動かないことがあります。付け替えた記憶の一覧とこの注意は、報告ファイルに出ます。
- 特定の既存の記憶やキーストーンに結びついていて付け替えられない仕掛けもあります。その宣言は理由つきで断られます。

これで、既存のヴェスパーとビスマスの星図を宣言ファイルから組み直せます。キーストーンを含むすべての星を再現でき、例外はヴェスパーの遠征の鍛錬の星4つだけです。[examples](examples/) フォルダに2人分の宣言を見本として置いています。複製に使える星の ID は、この見本で確かめられます。

知らない欄は無視します。新しい形式で書いたファイルも、このバージョンが分かる部分は読み込みます。

## 星図の上限

上限の数値はコードに書いていません。Dreamforge が起動するときに、既存の旅人の星図から求めます。そのため、今後の調整に合わせて上限も変わります。

- 使えるのは、既存の星で使われている能力値・記憶の星の種類・Power・仕掛けのパラメータ・修飾だけです。
- 種類ごとに、「1段あたりの値」「段数」「1つの星の合計（値×段数）」の3つが、どれも同じ種類の既存の星の最大以下である必要があります。たとえば 1段 150.21% の記憶ダメージの星は、1段なら通りますが、3段にすると断られます。
- 星・キーストーン・選択の星・選択肢・星群の数と `rankCost` は、既存の旅人の中で最も多い旅人まで使えます。既存の旅人と同じ大きさ（約900個）の星図まで作れます。

上限を超えた値は、丸めて受け付けることはしません。旅人の登録はそのまま残り、星図だけが汎用になって、理由が報告ファイルに書かれます。今の上限はすべて報告ファイルに載っています。

## ファイルを確かめる

Dreamforge は宣言を読むたびに、報告ファイルを書き直します。

```
<persistentDataPath>/QuickSave/Mods/DreamforgeRPG/connector-report.txt
Windows: %USERPROFILE%/AppData/LocalLow/Lizard Smoothie/Shape of Dreams/QuickSave/Mods/DreamforgeRPG/connector-report.txt
```

読んだファイル、受け付けた旅人と断った旅人（理由つき）、能力値ごとの今の上限が載っています。`Player.log` にも、`[Dreamforge/Connector]` で始まる同じ内容が出ます。

よくある断られ方は次のとおりです。

- JSON として読めない、`dreamforgeApi` が無い、またはこの Dreamforge より新しい: ファイル全体を読みません。
- `key` が既存の旅人と同じ、または別の MOD が同じ `key` を先に宣言した: その旅人だけを読みません。同じ `key` が2つあるときは、ゲームの MOD の並びで先にある MOD が使われます。
- 星が上限を超えている: その旅人は汎用の星図になります。

## 協力プレイ

- 双方の Dreamforge がコネクタに対応していれば、宣言した旅人の一覧を交換します。古い Dreamforge や Dreamforge の無いプレイヤーには何も送らず、これまでと何も変わりません。
- 星の効果はホストの宣言で決まります。ホストに無い旅人、またはホストと宣言ファイルのバージョンが違う旅人を参加者が使うと、その部屋ではその旅人の星の効果が乗りません。装備はそのまま効きます。両側に1回だけ知らせが出ます。
- 協力プレイで同じ結果にするには、全員が同じバージョンのあなたの MOD を使ってください。

## セーブ

- あなたの旅人の進み具合は、ほかの旅人と同じく `key` の名前で保存されます。
- プレイヤーがあなたの MOD を外しても、Dreamforge はその旅人の進み具合をそのまま残します。MOD を入れ直せば元に戻ります。
- 新しいバージョンで星を削ったり `id` を変えたりすると、無くなった星への割り当ては効果を持たなくなり、そのポイントは未使用に戻ります。割り当ての記録は残るので、星を戻せば割り当ても戻ります。

## 任意: コードから使う API

宣言をコードで組み立てたいときや、MOD から Dreamforge の状態を見たいときだけ使います。型は `Dreamforge.Api.HeroConnector`（public static）です。

| メンバー | 内容 |
| --- | --- |
| `int ApiVersion` | `1` |
| `string DreamforgeVersion` | Dreamforge のバージョン |
| `bool RegisterHeroes(string json, string sourceModId, out string error)` | `dreamforge.json` と同じ JSON を登録します。遠征中は遠征が終わるまで保留し、`true` を返して `error` に保留したことを入れます。 |
| `bool IsHeroRegistered(string heroKey)` | その旅人が登録されているか |
| `string[] GetRegisteredHeroes()` | 宣言された旅人の `key` の一覧 |
| `string GetReport()` | 報告ファイルと同じ文章 |

どのメンバーも例外を投げません。本体は各 MOD のアセンブリを名前を変えて読み込むため、DLL を参照せずに型の完全な名前で探します。

```csharp
static System.Type FindDreamforgeConnector()
{
    foreach (var asm in System.AppDomain.CurrentDomain.GetAssemblies())
    {
        var t = asm.GetType("Dreamforge.Api.HeroConnector", false);
        if (t != null) return t;
    }
    return null; // Dreamforge が入っていない
}
```

あなたの MOD が Dreamforge より先に読み込まれると、その時点ではこの関数は `null` を返します。本体の `DewMod.onModLoadEnded` などで後から呼ぶか、読み込み順に左右されない `dreamforge.json` を使ってください。

## 互換の約束

- `dreamforgeApi: 1` の欄の意味は変えません。新しい機能は新しい欄として足し、古いファイルはそのまま読み込みます。
- どうしても意味を変えるときは形式を `2` にし、バージョン 1 のファイルも読み続けます。
- `Dreamforge.Api` の public メンバーは、その API のバージョンに対応しているあいだは削りません。

## 質問と要望

[Issues](https://github.com/Kling0012/dreamforge-rpg/issues/new/choose) から送ってください。記憶・本質・遺物を足す MOD など、連携できる範囲を広げる要望も歓迎します。
