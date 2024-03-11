import librosa
import soundfile as sf


# 加载原始音频文件
audio_file = './data/1462784738-1-192.wav'
y, sr = librosa.load(audio_file, sr=None)

# 将采样率转换为16000Hz
y_16k = librosa.resample(y, orig_sr=sr, target_sr=16000)

# 使用librosa的深度学习模型分离人声和背景音
y_voice, y_bg = librosa.util.softmask(y_16k, model='demucs_thin')

# 保存分离后的人声音频
sf.write('1462784738-1-192_vocal.wav', y_voice, 16000)
