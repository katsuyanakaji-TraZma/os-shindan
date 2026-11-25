"""DTDの見張り番：Mac miniのChromeに頼らず、公開情報だけを確かめて watch/status.json に書く。
- note：最新の公開記事一覧と、見張りリスト（watch/note_keys.txt）の記事が公開済みか
- Amazon：見張りリスト（watch/amazon_queries.txt）の本が検索に出ているか
ログインは使わない。読むだけ。"""
import json, urllib.request, urllib.parse, datetime, re, pathlib
ROOT = pathlib.Path(__file__).parent
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
      "Accept-Language": "ja-JP,ja;q=0.9"}
def get(url, raw=False):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            b = r.read()
            return r.status, (b if raw else b.decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return -1, str(e)[:200]
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="minutes")
out = {"checkedAt": now, "note": {}, "amazon": {}}
# note 最新一覧
st, body = get("https://note.com/api/v2/creators/katsuya_nakajima/contents?kind=note&page=1")
latest = []
if st == 200:
    try:
        for c in json.loads(body)["data"]["contents"]:
            latest.append({"key": c.get("key"), "name": c.get("name"), "publishAt": c.get("publishAt")})
    except Exception as e:
        out["note"]["error"] = str(e)[:200]
out["note"]["listStatus"] = st
out["note"]["latest"] = latest[:10]
pub = {x["key"] for x in latest}
watch = {}
kf = ROOT / "note_keys.txt"
for line in (kf.read_text(encoding="utf-8").splitlines() if kf.exists() else []):
    k = line.split("#")[0].strip()
    if not k:
        continue
    if k in pub:
        watch[k] = "公開済み"
    else:
        s, b = get(f"https://note.com/api/v3/notes/{k}")
        watch[k] = "公開済み" if (s == 200 and '"status":"published"' in b) else f"未公開（{s}）"
out["note"]["watch"] = watch
# Amazon 検索
qf = ROOT / "amazon_queries.txt"
for line in (qf.read_text(encoding="utf-8").splitlines() if qf.exists() else []):
    q = line.split("#")[0].strip()
    if not q:
        continue
    s, b = get("https://www.amazon.co.jp/s?k=" + urllib.parse.quote(q) + "&i=digital-text")
    asins = sorted(set(re.findall(r'data-asin="(B0[A-Z0-9]{8})"', b)))[:10]
    out["amazon"][q] = {"httpStatus": s, "found": q.replace(" ", "")[:12] in b.replace(" ", ""), "asins": asins}
(ROOT / "status.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False)[:1500])
