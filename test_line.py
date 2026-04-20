import os
import requests

LINE_TOKEN = os.environ.get("LINE_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

print("=== LINE接続テスト ===")
print(f"LINE_USER_ID設定: {'あり' if LINE_USER_ID else 'なし'}")
print(f"LINE_TOKEN設定: {'あり' if LINE_TOKEN else 'なし'}")

# ボット情報確認（トークンの有効性チェック）
r = requests.get(
    "https://api.line.me/v2/bot/info",
    headers={"Authorization": f"Bearer {LINE_TOKEN}"}
)
print(f"\nBot info status: {r.status_code}")
print(f"Bot info: {r.text}")

# テストメッセージ送信
print("\n--- テストメッセージ送信 ---")
msg = "🧪 LINEボット接続テスト\nレシピBOTの設定確認中です！\n\n✅ この通知が届いていれば設定OK！"
r2 = requests.post(
    "https://api.line.me/v2/bot/message/push",
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {LINE_TOKEN}"},
    json={"to": LINE_USER_ID, "messages": [{"type": "text", "text": msg}]}
)
print(f"Push status: {r2.status_code}")
print(f"Push response: {r2.text}")

if r2.status_code == 200:
    print("\n✅ LINE送信成功！")
else:
    print("\n❌ LINE送信失敗")
    import sys
    sys.exit(1)
