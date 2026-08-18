"""Simple keyword sentiment for VinFast comments. ponytail: rules not ML."""
import csv
import re
from pathlib import Path

POS = re.compile(
    r"ngon|đẹp|sướng|thích|tuyệt|ủng hộ|đáng tiền|đáng mua|mê luôn|hài lòng|"
    r"chuẩn|rất ok|rất tốt|hay quá|yêu |tự hào|xịn|mạnh|bốc|đầm chắc|"
    r"tiết kiệm|đáng|ưng ý|khen|ngon nhất|đẹp nhất|mến |rất mến|"
    r"worth|beautiful|love|great car|recommend",
    re.I,
)
NEG = re.compile(
    r"chê|tệ|xấu|lỗi|thất vọng|kém|dở|rác|thua|chán|ghét|"
    r"đắt quá|giá đắt|giá cao|quá đắt|bỏ mẹ|vỡ mòm|ảo|lừa|"
    r"ế |anti|spam|nhạt nhẽo|thảm|điên|đau đớn|chán nhất|"
    r"không nên mua|đừng mua|ko nên mua|thất bại|treo|"
    r"ồn quá|hao pin|dịch vụ kém|bảo dưỡng kém|chuối|ngáo|"
    r"lùa gà|phản cảm|complaint|disappoint|ugly|broken|defect",
    re.I,
)
NEU = re.compile(
    r"\?|hỏi|bao nhiêu|bao vậy|có .* ko|hay ko|phải ko|"
    r"tipcar|kênh |video |review |clip |youtube|autopro|"
    r"subscribe|sub |follow|xem kênh|bác va|việt anh|"
    r"cảm ơn kênh|ủng hộ kênh|bài review|làm video",
    re.I,
)
STRONG_NEG = re.compile(r"xấu|tệ|lỗi|chê|ghét|đắt|kém|dở|rác|thất vọng|ồn|chán|chuối", re.I)
MIXED = re.compile(r"nhưng|tuy nhiên|mỗi tội", re.I)


def label(text: str) -> str:
    t = text.lower()
    if NEU.search(t):
        return "neutral"
    if STRONG_NEG.search(t) and not re.search(
        r"rất (thích|đẹp|ngon|ok|mến)|đẹp quá|ngon quá|quá ngon", t
    ):
        return "negative"
    p = len(POS.findall(t))
    n = len(NEG.findall(t))
    if MIXED.search(t) and p > 0 and n > 0:
        return "neutral"
    if p > n:
        return "positive"
    if n > p:
        return "negative"
    return "neutral"


def main():
    path = Path("data/comments.csv")
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    for i, r in enumerate(rows):
        if i < 300:
            continue
        r["sentiment"] = label(r["comment"])
        r["reviewed"] = "true"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["comment", "sentiment", "model", "video_id", "reviewed"])
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    batch = [r["sentiment"] for r in rows[300:]]
    print("labeled 301+", len(batch), Counter(batch))


if __name__ == "__main__":
    assert label("VF8 pin trâu, chạy sướng, đáng tiền") == "positive"
    assert label("Giá VF9 bao nhiêu vậy?") == "neutral"
    assert label("Xe lỗi nhiều, dịch vụ kém, thất vọng") == "negative"
    main()
