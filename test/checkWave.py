import wave

# WAV 파일 열기
with wave.open('data/output_mono.wav', 'rb') as wf:
    channels = wf.getnchannels()  # 채널 수 (1: 모노, 2: 스테레오) -> 채널이 1로 되게 해야함
    sample_width = wf.getsampwidth()  # 샘플 폭 (바이트 단위)
    frame_rate = wf.getframerate()  # 샘플링 레이트
    n_frames = wf.getnframes()  # 총 프레임 수

    print(f"Channels: {channels}")
    print(f"Sample Width: {sample_width * 8} bits")
    print(f"Frame Rate: {frame_rate} Hz")
    print(f"Total Frames: {n_frames}")
    print(f"Duration: {n_frames / frame_rate} seconds")