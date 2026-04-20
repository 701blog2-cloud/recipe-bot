import os
import time
import traceback
import requests

LINE_TOKEN = os.environ.get("LINE_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

MODELS = [
    "gemini-2.0-flash",
    "gemini-2.5-flash-preview-04-17",
    "gemini-2.0-flash-lite",
]

PROMPT = """
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

def call_gemini(model):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": PROMPT}]}]}
    for attempt in range(3):
        response = requests.post(url, json=payload)
        print(f"Gemini [{model}] attempt {attempt+1}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        if response.status_code == 429:
            if attempt < 2:
                wait = 20 * (attempt + 1)
                print(f"レート制限。{wait}秒待機...")
                time.sleep(wait)
            else:
                print(f"{model} クォータ超過。次のモデルへ...")
                return None
        elif response.status_code == 404:
            print(f"{model} は利用不可。次のモデルへ...")
            return None
        else:
            print(f"エラー応答: {response.text}")
            raise Exception(f"Gemini API error: {response.status_code}")
    return None

def generate_recipe():
    for model in MODELS:
        result = call_gemini(model)
        if result:
            return result
    raise Exception("全モデルが利用できません（クォータ超過または利用不可）")

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
