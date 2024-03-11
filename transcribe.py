from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch

# 加载预训练模型和处理器
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")

# 加载音频文件并预处理
audio_file = "./data/1462784738-1-192.wav"
speech, sample_rate = processor.read_audio(audio_file)

# 将音频输入到模型进行转录
input_values = processor(speech, return_tensors="pt", sampling_rate=sample_rate).input_values

# 生成预测的文本
with torch.no_grad():
    logits = model(input_values).logits

predicted_ids = torch.argmax(logits, dim=-1)
transcription = processor.batch_decode(predicted_ids)[0]

# 对齐转录文本和音频
alignment = model.wav2vec2.ctc.ctc_greedy_decode(logits, predict_offsets=True)
aligned_transcription = []
for i, token in enumerate(alignment[0][0]):
    aligned_transcription.append((token, alignment[1][0][i].item(), alignment[1][1][i].item()))

print("Transcription:", transcription)
print("Aligned Transcription:")
for token, start, end in aligned_transcription:
    print(f"{token}: {start/sample_rate:.2f}s - {end/sample_rate:.2f}s")