import pyaudio
import wave
import numpy as np

RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6  # 원본 채널 수
TARGET_CHANNELS = 1     # 저장할 채널 수 (모노)
RESPEAKER_WIDTH = 2
RESPEAKER_INDEX = 1  # refer to input device id
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "data/output_mono.wav"

p = pyaudio.PyAudio()

stream = p.open(
    rate=RESPEAKER_RATE,
    format=p.get_format_from_width(RESPEAKER_WIDTH),
    channels=RESPEAKER_CHANNELS,
    input=True,
    input_device_index=RESPEAKER_INDEX,
)

print("* recording")

frames = []

for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    # np.frombuffer를 사용하여 다중 채널 데이터를 numpy 배열로 변환
    audio_data = np.frombuffer(data, dtype=np.int16)
    # 다중 채널 데이터를 평균화하여 모노 채널로 변환
    mono_data = audio_data.reshape(-1, RESPEAKER_CHANNELS).mean(axis=1).astype(np.int16)
    frames.append(mono_data.tobytes())

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(TARGET_CHANNELS)
wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
wf.setframerate(RESPEAKER_RATE)
wf.writeframes(b''.join(frames))
wf.close()
