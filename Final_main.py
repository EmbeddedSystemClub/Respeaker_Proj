import time
import os
import pyaudio
import sqlite3
from google.cloud import speech
from usb_4_mic_array.tuning import Tuning
import usb.core
import usb.util

# Google Cloud 인증 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Dev/Respeaker_Project/data/plucky-sound-433806-d9-740f05cf36be.json"  # json파일 위치에 맞춰서 입력

# 특정 단어 리스트 (주제별로 그룹화)
call_words = ["종원아", "헤이", "어이"]
importance_4words = ["날씨", "음악", "사진", "주말"]
importance_5words = ["힘들어", "우울해", "행복해", "좋아"]

# 단어 그룹과 그에 해당하는 주제를 딕셔너리로 매핑
word_groups = {
    "호출": call_words,
    "중요도4": importance_4words,
    "중요도5": importance_5words
}

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# Google Cloud Speech-to-Text 클라이언트 생성
client = speech.SpeechClient()

def save_to_database(direction, group_name, word, recognized_text):
    conn = sqlite3.connect('data/wordDB.db')  # 데이터베이스 파일 위치에 맞춰서 넣기
    cursor = conn.cursor()

    # 테이블 이름을 wordDB로 수정
    cursor.execute('''
    INSERT INTO wordDB (direction, group_name, word, recognized_text)
    VALUES (?, ?, ?, ?)
    ''', (direction, group_name, word, recognized_text))

    conn.commit()
    conn.close()

    print(f"Saved: Direction={direction}, Group={group_name}, Word={word}, Text={recognized_text}")

def load_from_database():
    conn = sqlite3.connect('data/wordDB.db')  # 데이터베이스 파일 위치에 맞춰서 넣기
    cursor = conn.cursor()

    # 테이블 이름을 wordDB로 수정
    cursor.execute('SELECT direction, group_name, word, recognized_text, timestamp FROM wordDB')
    results = cursor.fetchall()

    conn.close()

    return results

def get_audio_stream():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    return stream, p

def detect_word_in_text(text):
    for group_name, words in word_groups.items():
        for word in words:
            if word in text:
                return group_name, word
    return None, None

def recognize_speech():
    stream, p = get_audio_stream()

    try:
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code="ko-KR",
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True
        )

        audio_generator = (stream.read(CHUNK) for _ in iter(int, 1))
        requests = (speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            recognized_text = result.alternatives[0].transcript.strip()
            print(f"Recognized text: {recognized_text}")

            group_name, detected_word = detect_word_in_text(recognized_text)
            
            if detected_word:
                print(f"주제 '{group_name}'에서 특정 단어 '{detected_word}'이(가) 발견되었습니다.")
                return 1, detected_word, group_name, recognized_text

    finally:
        # stream.stop_stream()
        # stream.close()
        # p.terminate()
        print("* Recording stopped and resources cleaned up.")
    
    return None, None, None, None

def detect_direction():
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

    if dev:
        print("hi")
        Mic_tuning = Tuning(dev)
        previous_direction = None
      
        try:
            while True:
                direction = Mic_tuning.direction

                if direction != previous_direction:
                    result, detected_word, group_name, recognized_text = recognize_speech()
                    if group_name == "호출" and result == 1: # 호출이면 방향과 들린 단어를 출력하도록 -> 나중에 앱이랑 연동할 때 수정해야할 곳
                        print(f"Direction detected: {direction}")
                        print(f"'{detected_word}'이(가) '{direction}'에서 들렸습니다.")
                        save_to_database(direction, group_name, detected_word, recognized_text)
                    elif group_name in ["중요도4", "중요도5"]: # 중요도와 관련된 단어가 감지됐을 때는 중요도와 들린 단어가 출력되도록 -> 이곳도 앱이랑 연동할 때 수정해야할 곳
                        print(f"'{group_name}'에서 '{detected_word}' 단어가 감지되었습니다.")
                        save_to_database(direction, group_name, detected_word, recognized_text)
                        
                    previous_direction = direction

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n* Stopping direction detection...")

    else: 
        print("bye")

if __name__ == "__main__":
    detect_direction()
