# Labeling prompt — VinFast comment sentiment

Use this prompt in Cursor when labeling `data/comments_unlabeled.csv`.

---

## Task

Fill the `sentiment` column for each row in the CSV.

**Allowed values only:** `positive`, `negative`, `neutral`

After labeling, set `reviewed` to `true` for rows you checked. Save the file as `data/comments.csv`.

---

## Label rules

| Label | Use when |
|-------|----------|
| **positive** | Praise, satisfaction, recommend, pride in the car |
| **negative** | Complaint, disappointment, quality/service issues, criticism |
| **neutral** | Questions, specs, comparisons without clear opinion, off-topic but readable |

---

## Edge cases (VinFast comments)

- Mixed tone ("đẹp nhưng giá cao") → pick **dominant** tone, or `neutral` if balanced
- `"Xe đẹp quá... sạc ở đâu?"` → `neutral` (question), not positive
- Sarcasm with hidden complaint → `negative`
- Price/pin/sạc/bảo hành questions → `neutral`
- Spam rows → delete the row

---

## Examples

| Comment | Label |
|---------|-------|
| VF8 pin trâu, chạy sướng, đáng tiền | positive |
| VF3 giá rẻ, đi phố tiện, rất thích | positive |
| Xe lỗi nhiều, dịch vụ kém, thất vọng | negative |
| VF8 hao pin nhanh, chất lượng chưa ổn | negative |
| Giá VF9 bao nhiêu vậy? | neutral |
| VF7 so với VF8 thì nên chọn con nào? | neutral |
| Xe đẹp quá... mà sạc ở đâu nhỉ? | neutral |

---

## Review checklist

Before saving `comments.csv`:

- [ ] Every row has a valid sentiment
- [ ] No duplicate comments
- [ ] Rough balance: ~25–40% each for positive/negative, ~20–35% neutral
- [ ] All 5 models (VF3, VF5, VF7, VF8, VF9) still represented
