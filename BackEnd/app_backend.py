# app_backend.py
from flask import Flask, request, jsonify
import speech_recognition as sr
import io
import time # Para simular um delay de processamento

app = Flask(__name__)

# Configuração da biblioteca de reconhecimento
r = sr.Recognizer()

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    # Verifica se um arquivo de áudio foi enviado
    if 'audio_file' not in request.files:
        return jsonify({"error": "Nenhum arquivo de áudio recebido"}), 400

    audio_file = request.files['audio_file']
    
    try:
        # Envelopa o arquivo recebido em um objeto AudioFile
        with sr.AudioFile(io.BytesIO(audio_file.read())) as source:
            # O processamento de ruído é feito aqui: 
            # adjust_for_ambient_noise é uma supressão de ruído básica da lib
            r.adjust_for_ambient_noise(source) 
            
            # Lê o áudio completo do buffer
            audio = r.record(source) 

        # Chama a API de reconhecimento de voz do Google (requer internet)
        # Você pode usar 'recognize_google(audio, language="pt-BR")'
        # para uma versão mais simples/gratuita, mas menos robusta.
        # Para real-time, essa abordagem deve ser substituída por WebSockets.
        transcription = r.recognize_google(audio, language="pt-BR")
        
        # Simula o tempo de processamento em tempo real
        time.sleep(0.5) 
        
        return jsonify({
            "success": True, 
            "transcription": transcription
        })

    except sr.UnknownValueError:
        return jsonify({"success": False, "transcription": "Não foi possível entender o áudio"}), 200
    except sr.RequestError as e:
        return jsonify({"success": False, "transcription": f"Erro de serviço de API; {e}"}), 500
    except Exception as e:
        return jsonify({"success": False, "transcription": f"Erro interno: {e}"}), 500


if __name__ == '__main__':
    # Este servidor Python rodará em paralelo ao app Electron/React
    app.run(port=5001, debug=True)