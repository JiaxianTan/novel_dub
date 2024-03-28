# novel_dub 基于TTS模型开发的一款逼近真人配音小说的仓库

## 一、简介
    -- 借助超强AI配音算法库完成逼近真人的小说配音
    
## 二、开发部分
    -- 1、读取音频生成各种角色的训练集
    -- 2、对每个训练使用Gpt-sovits进行训练、推理、部署
    -- 3、对超长文本进行分段,进行角色配置
    -- 4、开发小程序+后端模式进行服务器端部署
    
    **要办事项**
        -- 办理停保做失业登记，注册初创公司领取创业补贴
        -- 小程序企业注册+域名备案+ICP备案
        -- 申请出版物经营许可证 ==》网上卖书

## 三、产品特色
    -- 截取片段(吸引人)--》在考虑推全书。或者短片散文这类的
    -- 走线下出版社合作  《==》 TOB
    -- 自己开店铺   《==》 TOC
## 三、结论
    -- 

## 竞品 
    1. 番茄精听 - 字节
    2. 懒人听书 - 腾讯阅文
    -- https://zenvideo.qq.com/

## 四、附录
    -- UI 设计: https://www.visily.ai/ai-ui-design-generator/
    -- 人声伴奏分离: 
        - demucs: https://github.com/adefossez/demucs
            - https://www.fosshub.com/Demucs-GUI.html
        - Uvr5: https://github.com/Anjok07/ultimatevocalremovergui
        - RipX DeepAudio: https://link.zhihu.com/?target=https%3A//www.aliyundrive.com/s/e6kfr5wjcRX
    -- 语音对齐和转录
        - fast-whisper: https://github.com/SYSTRAN/faster-whisper
        - whisperX: https://github.com/m-bain/whisperX
    -- speaker diarization
        - pyannote-audio: https://github.com/pyannote/pyannote-audio
        - nemo: https://github.com/NVIDIA/NeMo/tree/main/examples/speaker_tasks/diarization
    -- tts:
        - GPT-SoVITS:https://github.com/RVC-Boss/GPT-SoVITS
    -- 音频ai:
        - https://www.suno.ai/
    
    -- gpt 插件: https://github.com/openai-translator/openai-translator