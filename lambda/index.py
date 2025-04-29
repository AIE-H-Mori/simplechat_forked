import json
import urllib.request
import os

# ngrok経由で公開されているFastAPIのエンドポイント
FASTAPI_URL = os.environ.get("FASTAPI_URL", "https://4fcb-34-169-148-165.ngrok-free.app/generate")  # 実際のURLをセット

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        prompt = body.get('prompt','') #promptを取得
        message = body.get('prompt', '')  # 'prompt' を取得し、存在しない場合は空文字列をセット
        conversation_history = body.get('conversationHistory', [])
        
        # 会話履歴を構築
        messages = conversation_history.copy()
        messages.append({"role": "user", "content": message})
        
        # FastAPI向けのリクエストペイロード
        #request_payload = json.dumps({"messages": messages}).encode("utf-8")
        request_payload = json.dumps({"prompt": prompt}).encode("utf-8")        
        # HTTPリクエストを作成
        request = urllib.request.Request(
            FASTAPI_URL,
            data=request_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        # APIを呼び出し
        with urllib.request.urlopen(request) as response:
            response_body = json.loads(response.read().decode("utf-8"))
        
        # Gemmaのレスポンスを処理
        assistant_response = response_body["response"]
        
        # 会話履歴に追加
        messages.append({"role": "assistant", "content": assistant_response})
        
        # 成功レスポンスを返す
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }

    except Exception as error:
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "body": json.dumps({"success": False, "error": str(error)})
        }