import os
import pyaudio
from google.cloud import speech

# Google Cloud 인증 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Dev/Respeaker_Project/data/plucky-sound-433806-d9-740f05cf36be.json"

# 특정 단어 리스트 (주제별로 그룹화)
call_words = ["종원아", "헤이", "어이"]
hobby_words = ["날씨", "음악", "사진", "주말"]
mood_words = ["힘들어", "우울해", "행복해", "좋아"]

# 단어 그룹과 그에 해당하는 주제를 딕셔너리로 매핑
word_groups = {
    "호출": call_words,
    "취미": hobby_words,
    "기분": mood_words
}

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# Google Cloud Speech-to-Text 클라이언트 생성
client = speech.SpeechClient()

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
    # 각 단어 그룹을 순회하며 단어를 감지
    for group_name, words in word_groups.items():
        for word in words:
            if word in text:
                return group_name, word
    return None, None

def recognize_speech():
    # 음성 스트림 설정
    stream, p = get_audio_stream()

    try:
        # Google Cloud Speech-to-Text 요청 설정
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

            # 인식된 텍스트 추출
            recognized_text = result.alternatives[0].transcript.strip()

            # 인식된 텍스트 출력
            print(f"Recognized text: {recognized_text}")

            # 특정 단어 감지
            group_name, detected_word = detect_word_in_text(recognized_text)
            if detected_word:
                print(f"주제 '{group_name}'에서 특정 단어 '{detected_word}'이(가) 발견되었습니다.")
                break  # 단어가 감지되면 루프 종료

    except KeyboardInterrupt:
        print("\n* Stopping speech recognition...")

    finally:
        # 자원 해제
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("* Recording stopped and resources cleaned up.")
