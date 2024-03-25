# -*- coding: utf-8 -*-
# @Author  : JiaXian Tan
# @Time    : 2024/03/24 13:56
# @Desc    : 将视频转成音频后提取每个speaker的音频片段并生成最后的标注文件

import os
import shlex
from collections import namedtuple

import demucs
import subprocess

import torch
import whisperx
from faster_whisper import WhisperModel
from moviepy.video.io.VideoFileClip import VideoFileClip
from pyannote.audio import Pipeline
from scipy.io import wavfile


def long_text_seg_speaker():
    """长文本依据角色内容进行切分"""
    # 1. 设定prompt
    # 2. 配置LLM
    # 3. 创建chain
    pass


class AudioProcess(object):
    def __init__(self):
        self.sr = 16000
        self.save_dir = 'output'

    def convert_audio(self, video_path,  format='wav'):
        """将mp4视频转换音频wav"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(video_path)
            # 获取 video_name
        video_name = os.path.splitext(video_path)[0]
        video = VideoFileClip(video_path)
        audio = video.audio
        audio_path = f'{video_name}.{format}'
        audio_path = os.path.join(self.save_dir, audio_path)
        audio.write_audiofile(audio_path)

    def separate_vocals(self, audio_path, model_name='htdemucs_ft'):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(audio_path)
        demucs.separate.main(shlex.split(f'-n {model_name} --two-stems=vocals "{audio_path}" -o "temp_outputs"'))
        input_file = os.path.basename(audio_path)
        input_file = os.path.join(
            "temp_outputs", "htdemucs", os.path.basename(input_file[:-4]), "vocals.wav")

        audio_file = f"data/{input_file}_16k.wav"
        subprocess.run(f"rm -rf {audio_file}")
        subprocess.run(f"ffmpeg -i {input_file} -ac 1 -ar {self.sr} {audio_file}")

    def transcribe(self, audio_path):
        device = "gpu" if torch.cuda.is_available() else "cpu"
        compute_type = "int8"
        whisper_model = "medium"

        model = WhisperModel(whisper_model, device=device, compute_type=compute_type)
        segments, info = model.transcribe(audio_path, beam_size=1, word_timestamps=False, vad_filter=True,
                                          vad_parameters=dict(min_silence_duration_ms=500))

        print(f"info.language = {info.language}")
        whisper_results = []

        for segment in segments:
            print("[%.2fs -> %.2fs] 「%s」\n" % (segment.start, segment.end, segment.text))
            whisper_results.append(segment._asdict())

        del model
        torch.cuda.empty_cache()

        alignment_model, metadata = whisperx.load_align_model(language_code=info.language, device=device)
        result_aligned = whisperx.align(whisper_results, alignment_model, metadata, audio_path, device)
        word_ts = result_aligned["segments"]

        WhisperSegment = namedtuple('WhisperSegment', ['start', 'end', 'text'])

        whisper_segments = []
        audio_file = os.path.basename(audio_path)
        file_name = os.path.splitext(audio_file)[0]
        with open(os.path.join(self.save_dir, f'Whisper_{file_name}.txt'), 'w') as f:
            for wrd_dict in word_ts:
                # ws, we, wrd = int(wrd_dict['start'] * 1000), int(wrd_dict['end'] * 1000), wrd_dict['text']
                ws, we, wrd = wrd_dict['start'], wrd_dict['end'], wrd_dict['text']
                whisper_segments.append(WhisperSegment(ws, we, wrd))
                f.write("{},{},{}\n".format(ws, we, wrd))

        return whisper_segments

    def speaker_diarization(self, audio_path):
        RTTMSegment = namedtuple('RTTMSegment', ['start', 'end', 'speaker_id'])
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token="")
        # apply pretrained pipeline
        diarization = pipeline(audio_path)
        # print the result
        rttm_segments = []
        audio_file = os.path.basename(audio_path)
        file_name = os.path.splitext(audio_file)[0]
        with open(os.path.join(self.save_dir, f"diarization_{file_name}.txt"), 'w') as f:
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
                rttm_segments.append(RTTMSegment(turn.start, turn.end, speaker))
                f.write("{},{},{}\n".format(turn.start, turn.end, speaker))

        return rttm_segments

    def merge(self, audio_path):

        whisper_segments = self.transcribe(audio_path)
        rttm_segments = self.speaker_diarization(audio_path)

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
                        matched_segments.append((whisper_segment.start, whisper_segment.end, whisper_segment.text,
                                                 best_rttm_segment.speaker_id))

            return matched_segments

        matched_segments = match_segments(whisper_segments, rttm_segments)

        output_file = os.path.join(self.save_dir, 'merge.txt')

        with open(output_file, 'w') as f:
            for start, end, text, speaker_id in matched_segments:
                f.write(f'{start} {end} {text} {speaker_id}\n')
        return matched_segments

    def split_audio(self, audio_path, output_file):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(audio_path)
        like = wavfile.read(audio_path)
        # print (like)
        with open(output_file, 'w') as f:
            for i, line in enumerate(open(output_file, 'r').readlines()):
                line = line.strip().split()
                t_start = int(line[0])
                t_end = int(line[1])
                text = line[2]
                speaker = line[3]
                lang = line[-1]
                sample_rate = 16000

                speaker_dir = os.path.join(self.save_dir, '{}'.format(speaker))
                if not os.path.exists(speaker_dir):
                    os.makedirs(speaker_dir)
                save_path = os.path.join(speaker_dir, f'{i}.wav')
                wavfile.write(save_path, sample_rate, like[1][t_start * sample_rate:t_end * sample_rate])

                f.write(f'{save_path}|{speaker}|{lang}|{text}\n')


if __name__ == '__main__':
    pass