#
# from moviepy.editor import VideoFileClip
#
#
# # 加载视频文件
# video_file = "./data/1435937490-1-192.mp4"
# video = VideoFileClip(video_file)
#
# # 提取音频
# audio = video.audio
#
# # 写入音频文件
# audio_file = "./data/1435937490-1-192.wav"
# audio.write_audiofile(audio_file)
#
# # 关闭视频文件
# video.close()

import yt_dlp
yt_url = 'https://www.youtube.com/watch?v=tgdJkAx3fJM'
ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
    }],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    error_code = ydl.download(yt_url)
    video_info = ydl.extract_info(yt_url, download=False)
    file_name = f"{video_info['id']}.wav"