import speech_recognition as sr
r = sr.Recognizer()
with sr.AudioFile("Teste.wav") as src:
    audio = r.record(src)
print("Duracao (bytes):", len(audio.frame_data))
try:
    print("Transcricao:", r.recognize_google(audio, language="pt-BR"))
except sr.UnknownValueError:
    print("UnknownValueError -> reconhecedor não entendeu o audio.")
except Exception as e:
    print("Erro:", type(e).__name__, e)
