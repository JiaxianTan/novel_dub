from faster_whisper import WhisperModel
import whisperx
import torch
from pyannote.audio import Pipeline

device = "cpu"
compute_type = "int8"
whisper_model = "medium"
audio_file = "data/audio_16k.wav"

model = WhisperModel(whisper_model, device=device, compute_type=compute_type)
segments, info = model.transcribe(audio_file, beam_size=1, word_timestamps=False,vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500))

print(f"info.language = {info.language}")
whisper_results = []

for segment in segments:
  print("[%.2fs -> %.2fs] 「%s」\n" % (segment.start, segment.end, segment.text))
  whisper_results.append(segment._asdict())


del model
torch.cuda.empty_cache()

alignment_model, metadata = whisperx.load_align_model(language_code=info.language, device=device)
result_aligned = whisperx.align(whisper_results, alignment_model, metadata, audio_file, device)
word_ts = result_aligned["segments"]

del alignment_model
torch.cuda.empty_cache()

# speaker diarization

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="")
# apply pretrained pipeline
diarization = pipeline(audio_file)

# from pyannote.core import Annotation, Segment
#
# annotation = Annotation()
# for turn, _, speaker in diarization.itertracks(yield_label=True):
#     start = turn.start
#     stop = turn.end
#     segment = Segment(start, stop)
#     annotation[segment, None] = speaker
#
#

import re
from collections import namedtuple
# 定义RTTM和Whisper片段的数据结构
RTTMSegment = namedtuple('RTTMSegment', ['start', 'end', 'speaker_id'])
WhisperSegment = namedtuple('WhisperSegment', ['start', 'end', 'text'])


# print the result
rttm_segments = []
with open('output/audio_16k.txt', 'w') as f:
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
        rttm_segments.append(RTTMSegment(turn.start, turn.end, speaker))
        f.write("{},{},{}\n".format(turn.start, turn.end, speaker))


whisper_segments = []
with open('output/whisper_16k.txt', 'w') as f:
    for wrd_dict in word_ts:
        # ws, we, wrd = int(wrd_dict['start'] * 1000), int(wrd_dict['end'] * 1000), wrd_dict['text']
        ws, we, wrd = wrd_dict['start'], wrd_dict['end'], wrd_dict['text']
        whisper_segments.append(WhisperSegment(ws, we, wrd))
        f.write("{},{},{}\n".format(ws, we, wrd))


def match_segments(whisper_segments, rttm_segments, threshold=0.5):
    matched_segments = []
    for whisper_segment in whisper_segments:
        best_overlap = 0
        best_rttm_segment = None
        for rttm_segment in rttm_segments:
            start = max(whisper_segment.start, rttm_segment.start)
            end = min(whisper_segment.end, rttm_segment.end)
            overlap = end - start
            if overlap > best_overlap:
                best_overlap = overlap
                best_rttm_segment = rttm_segment

        if best_rttm_segment is not None:
            overlap_ratio = best_overlap / (whisper_segment.end - whisper_segment.start)
            if overlap_ratio >= threshold:
                matched_segments.append((whisper_segment.start, whisper_segment.end, whisper_segment.text, best_rttm_segment.speaker_id))

    return matched_segments


speakers = ["鍋島さん", "ハルクさん"]

matched_segments = match_segments(whisper_segments, rttm_segments)


def output_matches(matched_segments, output_file):
    with open(output_file, 'w') as f:
        for start, end, text, speaker_id in matched_segments:
            f.write(f'{start} {end} {text} {speaker_id}\n')


output_file = 'output/file.txt'
output_matches(matched_segments, output_file)