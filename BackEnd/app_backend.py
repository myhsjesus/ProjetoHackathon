# app_backend.py - VERSÃO FINAL CORRIGIDA (SEM ERRO DE SINTAXE)
from flask import Flask, request, jsonify
from flask_cors import CORS 
import speech_recognition as sr
import io
import time
import tempfile 

app = Flask(__name__)
CORS(app) 

r = sr.Recognizer()

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    audio_data = request.data
    
    if not audio_data:
        return jsonify({"success": False, "transcription": ""}), 200

    transcription = ""
    
    # *** 1. INÍCIO DO BLOCO TRY PRINCIPAL ***
    try:
        
        # --- TENTATIVA 1: WebM com arquivo temporário (Requer FFmpeg/Pydub) ---
        try:
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=True) as temp_audio_file:
                temp_audio_file.write(audio_data)
                temp_audio_file.seek(0)
                
                with sr.AudioFile(temp_audio_file) as source:
                    audio_segment = r.record(source) 

                transcription = r.recognize_google(audio_segment, language="pt-BR")
                
        # --- SE A TENTATIVA WEB M FALHAR (CAUSA MAIS PROVÁVEL) ---
        except Exception as e_webm:
            print(f"DEBUG: Tentativa 1 (WebM) falhou. Erro: {e_webm}")
            
            # --- TENTATIVA 2: Forçar tratamento como dados brutos (PCM/RAW) ---
            try:
                audio_segment = sr.AudioData(audio_data, sample_rate=44100, sample_width=2)
                transcription = r.recognize_google(audio_segment, language="pt-BR")
            
            except sr.UnknownValueError:
                # Silêncio ou áudio ininteligível na tentativa RAW
                transcription = ""
            except Exception as e_raw:
                # ERRO CRÍTICO NA LEITURA RAW/PCM
                print("-" * 50)
                print("🚨 ERRO CRÍTICO INTERNO NO PROCESSAMENTO DO ÁUDIO (RAW/PCM) 🚨")
                print(f"Tentativa 1 (WebM) falhou com: {e_webm}")
                print(f"Tentativa 2 (RAW/PCM) falhou com: {e_raw}")
                print("-" * 50)
                # Re-lança o erro para o except final (Rede/Geral)
                raise e_raw 

        # Se a transcrição chegou até aqui (seja pela Tentativa 1 ou 2)
        time.sleep(0.1) 
        
        return jsonify({
            "success": True, 
            "transcription": transcription
        })

    # *** 2. FIM DO BLOCO TRY PRINCIPAL E INÍCIO DOS EXCEPT GERAIS ***

    # Este é o primeiro except que o código Python encontra fora do TRY
    except sr.UnknownValueError:
        # Se ocorrer na Tentativa 2, retorna sucesso, mas sem texto (silêncio)
        return jsonify({"success": False, "transcription": ""}), 200 

    except Exception as e:
        # Captura erros de rede (sr.RequestError) ou erros relançados do bloco interno (e_raw)
        print("-" * 50)
        print("🚨 ERRO EXTERNO OU FINAL NO RECONHECIMENTO 🚨")
        print(f"Causa: {e}")
        print("-" * 50)
        # Retorna o erro 500 para o Frontend
        return jsonify({"success": False, "transcription": f"[ERRO NO SERVIDOR: {type(e).__name__}]"}), 500


if __name__ == '__main__':
    # Esta linha é a ÚNICA que fica fora dos blocos try/except da função
    app.run(port=5001, debug=False)