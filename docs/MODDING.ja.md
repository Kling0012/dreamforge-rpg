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
- 専用の星図（能力値の星とキーストーン）。上限は既存の旅人の星図から決まります。

宣言では、既存の9人の旅人とその星は変えられません。旅人ごとの難易度・報酬の倍率、ペア連携、記憶のルート、特殊な効果を持つ星も宣言できません。宣言した旅人の倍率は、常に既定の値です。

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

| 欄 | 必須 | 内容 |
| --- | --- | --- |
| `dreamforgeApi` | 必須 | 形式のバージョン。`1` を書きます。 |
| `heroes` | 必須 | 旅人の一覧。1つのファイルに複数の旅人を書けます。 |
| `key` | 必須 | Hero のサブクラスの型名。`Hero_` で始まる英数字と `_` で、64文字まで。 |
| `name` | 任意 | 表示名（`en`・`ja`・`zh`）。足りない言語は `en`、次に `key` から `Hero_` を除いた名前になります。 |
| `melee` | 任意 | 近接の旅人なら `true`。既定は `false`。 |
| `memories` | 任意 | その旅人の記憶の表示名（`key` は記憶の型名）。表示だけに使い、Dreamforge の報酬やリンクには入りません。 |
| `starTree` | 任意 | 専用の星図。無ければ汎用の星図を使います。 |
| `nodes[].id` | 必須 | 英小文字・数字・`_` で32文字まで。旅人の中で重ならないようにします。保存される星の ID は `x.<key>.<id>` です。 |
| `nodes[].stat` | 必須 | 能力値の名前（例 `AttackPct`）。「星図の上限」を見てください。 |
| `nodes[].perRank`, `maxRank` | 通常の星で必須 | 1段あたりの値と段数。 |
| `nodes[].tier` | 任意 | `1`（内側の輪。既定）か `2`（外側の輪）。 |
| `nodes[].keystone`, `value`, `description` | キーストーンで必須 | キーストーン。熟練度の条件と費用は既存のキーストーンと同じです。 |
| `nodes[].name` | 任意 | 表示名。無ければ `id` を表示します。 |

知らない欄は無視します。新しい形式で書いたファイルも、このバージョンが分かる部分は読み込みます。

## 星図の上限

上限の数値はコードに書いていません。Dreamforge が起動するときに、既存の旅人の基本の星図から求めます。そのため、今後の調整に合わせて上限も変わります。

- 使える能力値は、既存の通常の星にあるものだけです。
- `perRank` と `maxRank` は、同じ能力値の既存の星で使われている最大の値までです。
- キーストーンの `value` は、同じ能力値の既存の星1つを最後の段まで上げたときの値までです。
- 通常の星とキーストーンの数は、既存の旅人の中で最も多い旅人の数までです。

上限を超えた値は、丸めて受け付けることはしません。旅人の登録はそのまま残り、星図だけが汎用になって、理由が報告ファイルに書かれます。星の位置は自動で決まり、バージョン 1 では指定できません。

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
