import os
import time
import traceback
import requests

LINE_TOKEN = os.environ.get("LINE_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

PROMPT = """
シャープの調理家電を使った、今日のおすすめレシピを2つ提案してください。
1つ目はホットクック、2つ目はヘルシオを使ったレシピにしてください。

条件：
- 簡単・時短（30分以内）
- 子どもも食べられる味付け
- それぞれの機器の機能を活かしたレシピ

以下のフォーマットで出力してください：

━━━━━━━━━━━━━━━
🍳 レシピ①：【料理名】
🔧 使用機器：ホットクック
⏱ 調理時間：【時間】
👨‍👩‍👧 対象：子どもも食べられる

【材料（2〜3人分）】
・材料を書く

【作り方】
1. 手順を書く

💡 ポイント：アドバイスを書く

━━━━━━━━━━━━━━━
🍳 レシピ②：【料理名】
🔧 使用機器：ヘルシオ
⏱ 調理時間：【時間】
👨‍👩‍👧 対象：子どもも食べられる

【材料（2〜3人分）】
・材料を書く

【作り方】
1. 手順を書く

💡 ポイント：アドバイスを書く
━━━━━━━━━━━━━━━
"""

GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

def generate_recipe_groq():
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": 1500
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Groq status: {response.status_code}")
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    print(f"Groq error: {response.text}")
    return None

def generate_recipe_openai():
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": 1000
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"OpenAI status: {response.status_code}")
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    print(f"OpenAI error: {response.text}")
    return None

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
                print(f"{model} クォータ超過。次へ...")
                return None
        elif response.status_code == 404:
            print(f"{model} は利用不可。次へ...")
            return None
        else:
            print(f"エラー応答: {response.text}")
            return None
    return None

def generate_recipe():
    # Groqを最初に試す（無料・高速）
    if GROQ_API_KEY:
        result = generate_recipe_groq()
        if result:
            return result
    # OpenAIをフォールバック
    if OPENAI_API_KEY:
        result = generate_recipe_openai()
        if result:
            return result
    # Geminiをフォールバック
    for model in GEMINI_MODELS:
        result = call_gemini(model)
        if result:
            return result
    raise Exception("全AIサービスが利用できません")

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
