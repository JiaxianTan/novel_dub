# -*- coding: utf-8 -*-
# @Author  : JiaXian Tan
# @Time    : 2024/03/24 13:56
# @Desc    : A variety of toos
import os
import demucs.separate
import shlex
from moviepy.editor import VideoFileClip
from scipy.io import wavfile


def convert_audio(video_path, format='wav'):
    if not os.path.exists(video_path):
        raise FileNotFoundError(video_path)
    # 获取 video_name
    video_name = os.path.splitext(video_path)[0]
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(f'{video_name}.{format}')


def split_audio(audio_path, output_file):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(audio_path)
    like = wavfile.read(audio_path)
    # print (like)
    # 音频结果将返回一个tuple。第一维参数是采样频率，单位为秒；第二维数据是一个ndarray表示歌曲，如果第二维的ndarray只有一个数据表示单声道，两个数据表示立体声。所以，通过控制第二维数据就能对歌曲进行裁剪。
    # 对like这个元组第二维数据进行裁剪，所以是like[1];第二维数据中是对音乐数据切分。 start_s表示你想裁剪音频的起始时间；同理end_s表示你裁剪音频的结束时间。乘44100 是因为每秒需要进行44100次采样
    # 这里表示对该音频的13-48秒进行截取
    for i, line in enumerate(open(output_file, 'r').readlines()):
        line = line.strip().split()
        t_start = int(line[0])
        t_end = int(line[1])
        text = line[2]
        speaker = line[3]
        lang = line[-1]
        sample_rate = 16000

        speaker_dir = os.path.join(os.getcwd(), '{}'.format(speaker))
        if not os.path.exists(speaker_dir):
            os.makedirs(speaker_dir)
        save_path = os.path.join(speaker_dir, f'{i}.wav')
        wavfile.write(save_path, sample_rate, like[1][t_start * sample_rate:t_end * sample_rate])


def separate_vocals(audio_path, sample_rate=16000):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(audio_path)
    input_file = os.path.basename(audio_path)
    demucs.separate.main(shlex.split(f'-n htdemucs_ft --two-stems=vocals "{input_file}" -o "temp_outputs"'))
    input_file = os.path.join(
        "temp_outputs", "htdemucs", os.path.basename(input_file[:-4]), "vocals.wav")

    audio_file = f"data/{input_file}_16k.wav"
    os.system(f"rm -rf {audio_file}")
    os.system(f"ffmpeg -i {input_file} -ac 1 -ar {sample_rate} {audio_file}")

