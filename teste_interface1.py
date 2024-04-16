from dotenv import load_dotenv
from datetime import datetime
import os
import azure.cognitiveservices.speech as speech_sdk
import PySimpleGUI as sg

def main():
    try:
        global speech_config
        global translation_config

        load_dotenv()
        cog_key = os.getenv('COG_SERVICE_KEY')
        cog_region = os.getenv('COG_SERVICE_REGION')

        translation_config = speech_sdk.translation.SpeechTranslationConfig(cog_key, cog_region)
        translation_config.speech_recognition_language = 'pt-BR'
        translation_config.add_target_language('fr')
        translation_config.add_target_language('es')
        translation_config.add_target_language('en')
        print('Pronto para traduzir de: ',translation_config.speech_recognition_language)

        speech_config = speech_sdk.SpeechConfig(cog_key, cog_region)

        layout = [
            [sg.Text('Para qual idioma deseja traduzir?')],
            [sg.InputText(size=(20, 1), key='-LANGUAGE-'), sg.Button('Traduzir'), sg.Button('Sair')]
        ]

        window = sg.Window('Tradutor de Fala', layout)

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == 'Sair':
                break
            elif event == 'Traduzir':
                target_language = values['-LANGUAGE-'].lower()
                if target_language in translation_config.target_languages:
                    Translate(target_language)
                else:
                    sg.popup('Por favor, insira um idioma válido (fr/es/en)')

    except Exception as ex:
        print(ex)

def Translate(targetLanguage):
    translation = ''

    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    translator = speech_sdk.translation.TranslationRecognizer(translation_config, audio_config=audio_config)
    print("Fale agora...")
    result = translator.recognize_once_async().get()
    print('Traduzindo "{}"'.format(result.text))
    translation = result.translations[targetLanguage]
    print(translation)

    voices = {
        "fr": "fr-FR-HenriNeural",
        "es": "es-ES-ElviraNeural",
        "en": "en-GB-RyanNeural"
    }
    speech_config.speech_synthesis_voice_name = voices.get(targetLanguage)
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)
    speak = speech_synthesizer.speak_text_async(translation).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)

    sg.popup(f'Translation: {translation}')


if __name__ == "__main__":
    main()
