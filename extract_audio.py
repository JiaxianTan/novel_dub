
from moviepy.editor import VideoFileClip



# 加载视频文件
video_file = "./data/1462784738-1-192.mp4"
video = VideoFileClip(video_file)

# 提取音频
audio = video.audio

# 写入音频文件
audio_file = "./data/1462784738-1-192.wav"
audio.write_audiofile(audio_file)

# 关闭视频文件
video.close()