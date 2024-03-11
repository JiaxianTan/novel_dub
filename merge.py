import re
from collections import namedtuple

# 定义RTTM和Whisper片段的数据结构
RTTMSegment = namedtuple('RTTMSegment', ['start', 'end', 'speaker_id'])
WhisperSegment = namedtuple('WhisperSegment', ['start', 'end', 'text'])

# 解析RTTM文件
def parse_rttm(rttm_file):
    rttm_segments = []
    with open(rttm_file, 'r') as f:
        for line in f:
            fields = line.strip().split()
            start = float(fields[3])
            duration = float(fields[4])
            end = start + duration
            speaker_id = fields[7]
            rttm_segments.append(RTTMSegment(start, end, speaker_id))
    return rttm_segments

# 解析Whisper转录文本
def parse_whisper(whisper_file):
    whisper_segments = []
    with open(whisper_file, 'r') as f:
        for line in f:
            match = re.match(r'(\d+\.\d+) (\d+\.\d+) (.+)', line.strip())
            if match:
                start, end, text = match.groups()
                start = float(start)
                end = float(end)
                whisper_segments.append(WhisperSegment(start, end, text))
    return whisper_segments

# 计算最近交集和覆盖率
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

# 输出匹配结果
def output_matches(matched_segments, output_file):
    with open(output_file, 'w') as f:
        for start, end, text, speaker_id in matched_segments:
            f.write(f'{start} {end} {text} {speaker_id}\n')


# 主函数
if __name__ == '__main__':
    rttm_file = 'path/to/rttm/file'
    whisper_file = 'path/to/whisper/file'
    output_file = 'path/to/output/file'

    rttm_segments = parse_rttm(rttm_file)
    whisper_segments = parse_whisper(whisper_file)
    matched_segments = match_segments(whisper_segments, rttm_segments)
    output_matches(matched_segments, output_file)