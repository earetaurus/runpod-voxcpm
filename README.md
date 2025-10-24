# VoxCPM Runpod Serverless Implementation

fair warning this is 80% vibecoding
check out
https://github.com/earetaurus/tts-apibridge

## Usage Example 

```json
{
  "input": {
    "text": "Hello World"
  }
}
```


## Usage Example voice cloning

```json
{
  "input": {
    "text": "Hello World",
    "prompt_text": "the text spoken in the wav",
    "prompt_wav_url": "link to wav file use copyparty"
  }
}
```

This repository contains a serverless implementation of VoxCPM designed to run on RunPod. It allows for text-to-speech synthesis using the VoxCPM model.

## Features

*   **Serverless Architecture**: Deployable on RunPod serverless for scalable audio generation.
*   **VoxCPM Integration**: Leverages the VoxCPM model for high-quality speech synthesis.

## Acknowledgements

This project is inspired by and built upon the following resources:

*   [VoxCPM](https://github.com/OpenBMB/VoxCPM/)
*   [jords1755/VibeVoice](https://github.com/jords1755/VibeVoice)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
[![Runpod](https://api.runpod.io/badge/earetaurus/runpod-voxcpm)](https://console.runpod.io/hub/earetaurus/runpod-voxcpm)

if you want to help my runpod Balance  survive the month, please use my referal link
https://runpod.io?ref=akghcny7
