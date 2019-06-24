# AI generating real-time football commentary
## [Project Video](https://www.youtube.com/watch?v=p9AmkiG8UeI)
This repo contains code for training and executing an AI-based soccer/football commentary engine using OpenAI GPT-2 language model running on top of Google's opensource Football Environment.

![project image](https://github.com/ChintanTrivedi/football_ai_commentary/blob/master/thumbnail.png)

### Setup instructions
This code has been tested on an Ubuntu 18.04 platform with access to an Nvidia GPU.
1. Install Google Football Environment (GPU version) from [this repository](https://github.com/google-research/football).
2. Install text-to-speech library [pyttsx3](https://pypi.org/project/pyttsx3/) using `pip install pyttsx3`.

### Train GPT-2
1. Use the notebook `src/train_commentary_gpt2.ipynb` on Google Colab to train the model.
2. Once trained, download the `checkpoint/run1/*` files under this directory `src/models/345M/`.

### Execute the commentary engine
1. Run `python src/generate_commentary.py` to start the game environment and the commentary engine.
