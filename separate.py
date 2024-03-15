import os
import demucs.separate
import shlex

file_extension = ['.mp4', '.wav']
allowed_files = [file for file in os.listdir() if any(file.lower().endswith(ext) for ext in file_extension)]
input_file = max(allowed_files, key=lambda file: os.path.getctime(file))

demucs.separate.main(shlex.split(f'-n htdemucs --two-stems=vocals "{input_file}" -o "temp_outputs"'))
input_file = os.path.join(
        "temp_outputs", "htdemucs", os.path.basename(input_file[:-4]), "vocals.wav")

audio_file = "data/audio_16k.wav"
os.system(f"rm -rf {audio_file}")
os.system(f"ffmpeg -i {input_file} -ac 1 -ar 16000 {audio_file}")