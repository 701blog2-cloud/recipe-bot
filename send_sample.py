import os
import requests

LINE_TOKEN = os.environ.get("LINE_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

sample = """🍳 今日のレシピ：鶏むね肉の塩麹蒸し

🔧 使用機器：ホットクック
⏱ 調理時間：25分
👨‍👩‍👧 対象：子どもも食べられる

【材料（2〜3人分）】
・鶏むね肉　1枚（約300g）
・塩麹　大さじ2
・酒　大さじ1
・ごま油　小さじ1
・にんにく（チューブ）　2cm

【作り方】
1. 鶏むね肉を一口大に切り、塩麹・酒・ごま油・にんにくをもみ込む
2. ホットクックの内鍋に入れ、まぜ技ユニットをセット
3. 「手動」→「蒸す」→「15分」でスタート
4. 完成したら器に盛り、お好みでレモンを添える

💡 ポイント：塩麹に漬ける時間が長いほど（一晩がベスト）しっとり柔らかに！お弁当にも◎"""

r = requests.post(
    "https://api.line.me/v2/bot/message/push",
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"},
    json={"to": LINE_USER_ID, "messages": [{"type": "text", "text": sample}]}
)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
