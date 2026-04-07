import os
import requests
from openai import OpenAI

LINE_TOKEN = os.environ.get("LINE_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def generate_recipe():
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = """
シャープのホットクックまたはヘルシオを使った、今日のおすすめレシピを1つ提案してください。

条件：
- 簡単・時短（30分以内）
- 子どもも食べられる味付け
- ホットクックまたはヘルシオの機能を活かしたレシピ

以下のフォーマットで出力してください：

🍳 今日のレシピ：【料理名】
🔧 使用機器：【ホットクック or ヘルシオ】
⏱ 調理時間：【時間】
👨‍👩‍👧 対象：子どもも食べられる

【材料（2〜3人分）】
・材料1
・材料2

【作り方】
1. 手順1
2. 手順2

💡 ポイント：【一言アドバイス】
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content

def send_line_message(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    data = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"LINE送信結果: {response.status_code}")
    return response.status_code == 200

def main():
    print("レシピ生成中...")
    recipe = generate_recipe()
    print(recipe)
    print("LINE送信中...")
    success = send_line_message(recipe)
    if success:
        print("✅ 送信成功！")
    else:
        print("❌ 送信失敗")

if __name__ == "__main__":
    main()
