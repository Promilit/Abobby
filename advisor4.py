import os, config, requests
import gradio as gr
import random, time



import openai
openai.api_key = config.OPENAI_API_KEY

messages = [{"role": "system", "content": 'You must speak only Nigerian Pidgin English. You be AI assistant wey abi speak only Naija Pidgin English. You dey very funny, sarcastic and likeable. Reply only in Naija Pidgin English. Imagine say you be a combination of all the funny Nigerian comedians.'}]

# prepare Q&A embeddings dataframe


def transcribe(audio):
    global messages

    # API now requires an extension so we will rename the file
    audio_filename_with_extension = audio + '.wav'
    os.rename(audio, audio_filename_with_extension)

    audio_file = open(audio_filename_with_extension, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    

    user_text = f" {transcript['text']}. {config.ADVISOR_CUSTOM_PROMPT}" 
    messages.append({"role": "user", "content": user_text})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    system_message = response["choices"][0]["message"]
    print(system_message)
    messages.append(system_message)

    # text to speech request with eleven labs
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ADVISOR_VOICE_ID}/stream"
    data = {
        "text": system_message["content"].replace('"', ''),
        "voice_settings": {
            "stability": 0.1,
            "similarity_boost": 0.8
        }
    }

    r = requests.post(url, headers={'xi-api-key': config.ELEVEN_LABS_API_KEY}, json=data)

    output_filename = "reply.mp3"
    with open(output_filename, "wb") as output:
        output.write(r.content)

    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    # return chat_transcript
    return chat_transcript, output_filename


# set a custom theme
theme = gr.themes.Default().set(
    body_background_fill="#000000",
)

with gr.Blocks(theme=theme) as ui:
    # advisor image input and microphone input
    advisor = gr.Image(value=config.ADVISOR_IMAGE).style(width=config.ADVISOR_IMAGE_WIDTH, height=config.ADVISOR_IMAGE_HEIGHT)
    audio_input = gr.Audio(source="microphone", type="filepath")

    # text transcript output and audio 
    text_output = gr.Textbox(label="Conversation Transcript")
    audio_output = gr.Audio()

    btn = gr.Button("Run")
    btn.click(fn=transcribe, inputs=audio_input, outputs=[text_output, audio_output])

openai.api_key = config.OPENAI_API_KEY

messages = [{"role": "system", "content": "You are an AI assistant that speaks only Nigerian pidgin English. You are funny, sarcastic, and likeable. When you don't know the answer to a question, please reply with If you ask me, na who I go ask. Do not answer any question that is not asked in Nigerian pidgin English. If a question is not asked in Nigerian pidgin English, please reply with this your English dey motivate me"}]

def CustomChatGPT(user_input):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply

with gr.Blocks() as ui1



ui1 = gr.Interface(fn=CustomChatGPT, inputs = "text", outputs = "text", title = "Abobby")

demo = gr.TabbedInterface([ui1, ui])

demo.launch()