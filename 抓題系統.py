import re
import json

txt_path = r"C:\Users\user\Desktop\金融常識題庫\職業道德113.txt"
output_path = r"C:\Users\user\Desktop\金融常識題庫\職業道德題庫.json"

# 讀取 ANSI/CP950
with open(txt_path, "r", encoding="cp950", errors="ignore") as f:
    raw = f.read()

# 切成行並清理
lines = [line.strip() for line in raw.splitlines() if line.strip()]

questions = []
i = 0

while i < len(lines):
    # 抓答案 (例如：(4))
    ans_match = re.match(r"\((\d)\)", lines[i])
    if not ans_match:
        i += 1
        continue

    answer = ans_match.group(1)
    i += 1

    # 抓題號
    if i >= len(lines): break
    if not lines[i].isdigit():
        # 題號不在格式，跳過
        continue
    qid = int(lines[i])
    i += 1

    # 抓題目 + 選項（所有括號開頭的就是選項）
    if i >= len(lines): break
    full_text = lines[i]
    i += 1

    # 分離題目與選項
    # ex:  下列何者...？(1)xxx(2)yyy(3)zzz(4)aaa
    parts = re.split(r"\((\d)\)", full_text)
    # parts ⇒ ["題目", "1", "選項1", "2", "選項2", ...]

    title = parts[0].strip()
    options = {}

    for j in range(1, len(parts), 2):
        opt_key = parts[j]
        opt_text = parts[j+1].strip()
        options[opt_key] = opt_text

    questions.append({
        "題號": qid,
        "題目": title,
        "選項": options,
        "答案": answer
    })

# 輸出
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print("解析完成！共", len(questions), "題")





