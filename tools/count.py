"""note記事の字数・反テンプレ上限を計測する。使い方: python3 tools/count.py articles/note_xxx.md [...]"""
import re
import sys
import unicodedata

CAPS = {"そのもの": 2, "静かに": 1, "皮肉なことに": 1, "皮肉にも": 1, "深夜": 2, "のかもしれません": 3}
HEDGES = ["言われています", "考えられています", "とされています", "伝えられています",
          "指摘されています", "浮上しています", "提唱されています"]


def strict(s):
    s = re.sub(r"https?://\S+", "", s)
    return sum(1 for ch in s if not ch.isspace() and unicodedata.category(ch)[0] not in "PSZ")


def report(path):
    t = open(path, encoding="utf-8").read()
    memo = t.find("<!-- 以下")
    article = t[:memo] if memo >= 0 else t
    start, omake = t.find("---"), t.find("## ■ おまけ")
    if start < 0 or omake < 0:
        print(f"{path}: 本文の区切り(--- / ## ■ おまけ)が見つかりません")
        return
    body = t[start + 3:omake]
    n = strict(body)
    print(f"== {path}")
    print(f"本文 {n}字" + ("  ※下限2,000字未満" if n < 2000 else "") +
          ("  (5,000字以上)" if n >= 5000 else ""))
    for ch in re.split(r"\n## ", body)[1:]:
        c = strict(ch)
        print(f"  {ch.splitlines()[0][:24]} {c}字" + ("  ※600字未満" if c < 600 else ""))
    tags = t.find("\n#", omake + 1)
    for item in re.split(r"\n\*\*", t[omake:tags if tags > 0 else memo])[1:]:
        c = strict(item.split("**", 1)[1])
        print(f"  おまけ{item[:1]} {c}字" + ("  ※100〜180字の範囲外" if not 100 <= c <= 180 else ""))
    for word, cap in CAPS.items():
        k = article.count(word)
        if k > cap:
            print(f"  ※「{word}」{k}回(上限{cap})")
    h = sum(article.count(w) for w in HEDGES)
    print(f"hedge {h}回" + ("  ※上限8回超" if h > 8 else ""))
    paras = [p.strip() for p in body.split("\n　\n") if p.strip() and not p.strip().startswith("#")]
    ends = [p.rstrip("*").endswith("のです。") for p in paras]
    if sum(ends) * 3 > len(paras) or any(a and b for a, b in zip(ends, ends[1:])):
        print(f"  ※「のです。」で終わる段落 {sum(ends)}/{len(paras)}(1/3まで・連続禁止)")
    if "実施予定" in t[memo:] if memo >= 0 else False:
        print("  ※内部メモに「ファクトチェック実施予定」が残っています")


for p in sys.argv[1:]:
    report(p)
