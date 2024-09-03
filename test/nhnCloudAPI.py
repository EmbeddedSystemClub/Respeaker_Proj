import hashlib
import hmac
import time
import requests
import json

# NHN Cloud API 키 및 URL
api_url = "https://speech.api.nhncloudservice.com"
access_key = "q0rdNDmW0OLA069O"  # 여기에 자신의 Access Key를 입력하세요
secret_key = "UtBmk8ZECQMa2s1llF2h5bBUq0hWTYgQ"  # 여기에 자신의 Secret Key를 입력하세요

# 현재 시간 (Unix 타임스탬프)
timestamp = str(int(time.time() * 1000))

# 서명 생성
message = f"{timestamp}.{access_key}"
signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

# 요청 헤더
headers = {
    "Content-Type": "application/json",
    "x-ncp-apigw-timestamp": timestamp,
    "x-ncp-iam-access-key": access_key,
    "x-ncp-apigw-signature-v2": signature
}

# 요청 바디
body = {
    "text": "안녕하세요, NHN Cloud TTS를 사용하고 있습니다.",
    "speaker": "mijin",  # 음성 합성에 사용할 음성 (예: mijin, clara, jinho 등)
    "format": "mp3",  # 출력 포맷 (mp3, wav 등)
    "volume": "0",  # 볼륨 (기본값: 0)
    "speed": "0",  # 속도 (기본값: 0)
    "pitch": "0"  # 음 높이 (기본값: 0)
}

# API 요청
response = requests.post(api_url, headers=headers, data=json.dumps(body))

# 결과 확인
if response.status_code == 200:
    # 응답 데이터에서 음성 파일 URL 또는 base64 인코딩된 데이터를 추출
    result = response.json()
    audio_url = result.get("audioUrl")
    print(f"Audio URL: {audio_url}")
else:
    print(f"Error: {response.status_code}")
    print(f"Message: {response.text}")
