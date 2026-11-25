# DTDの見張り番（dtd-watch）
Mac miniのChromeがつながらない日でも止まらないように、GitHub Actionsで20分ごとに公開情報だけを読み、`watch/status.json` に書きます。
- note：最新の公開記事と、`note_keys.txt` の記事が公開済みか
- Amazon：`amazon_queries.txt` の本が検索に出ているか（販売開始の見張り）
ログイン情報は一切使いません。持ち主：DTD 経営企画室（Claude）。
