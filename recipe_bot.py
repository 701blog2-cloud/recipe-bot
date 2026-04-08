import os
import traceback
import requests
from google import genai

LINE_TOKEN = os.environ.get("LINE_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def generate_recipe():
    client = genai.Client(api_key=GEMINI_API_KEY)
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
・材料を書く
・材料を書く

【作り方】
1. 手順を書く
2. 手順を書く

💡 ポイント：アドバイスを書く
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
    )
    return response.text

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
    print(f"LINE応答: {response.text}")
    return response.status_code == 200

def main():
    print("レシピ生成中...")
    try:
        recipe = generate_recipe()
        print(recipe)
        print("LINE送信中...")
        success = send_line_message(recipe)
        if success:
            print("✅ 送信成功！")
        else:
            raise Exception("LINE送信失敗")
    except Exception as e:
        print(f"エラー: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
