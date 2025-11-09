#!/usr/bin/env python
import asyncio
import json
import websockets
import os
import sys
from vosk import Model, KaldiRecognizer

# Auto-detect model path inside BackEnd/models/pt
BASE_DIR = os.path.dirname(__file__)
MODEL_BASE = os.path.join(BASE_DIR, 'models', 'pt')
SAMPLE_RATE = 16000

def find_model_path(base):
    if not os.path.isdir(base):
        return None
    entries = [e for e in os.listdir(base) if os.path.isdir(os.path.join(base, e))]
    # If base itself looks like a model (contains typical files/folders), use it
    base_contents = set(os.listdir(base))
    if {'am', 'conf'}.intersection(base_contents) or 'model.conf' in base_contents or 'HCLG.fst' in base_contents:
        return base

    # Prefer a subdirectory that looks like a model (contains model indicators)
    for sub in entries:
        subpath = os.path.join(base, sub)
        try:
            contents = set(os.listdir(subpath))
        except Exception:
            contents = set()
        if {'am', 'conf'}.intersection(contents) or 'model.conf' in contents or 'HCLG.fst' in contents:
            return subpath

    # If none of the subfolders look like a model, try common model-named folders
    for sub in entries:
        if sub.lower().startswith('vosk-model') or sub.lower().startswith('model'):
            return os.path.join(base, sub)

    # Fallback: pick first subdirectory if available
    if entries:
        return os.path.join(base, entries[0])
    return None

MODEL_PATH = find_model_path(MODEL_BASE)
if not MODEL_PATH:
    print(f"ERROR: Vosk model not found. Expected files under: {MODEL_BASE}")
    print("Please download a Vosk model (e.g. vosk-model-small-pt) and extract it under BackEnd/models/pt")
    sys.exit(1)

print("Loading Vosk model from:", MODEL_PATH)
model = Model(MODEL_PATH)

async def handler(websocket, path):
    print("Client connected")
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    try:
        async for message in websocket:
            # texto de controle
            if isinstance(message, str):
                try:
                    msg = json.loads(message)
                except Exception:
                    continue
                if msg.get("command") == "reset":
                    rec.Reset()
                    await websocket.send(json.dumps({"type":"reset"}))
                continue

            # mensagem binária: PCM16 little-endian
            data = message
            if not data:
                continue
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                await websocket.send(json.dumps({"type":"final","text":res.get("text","")}))
            else:
                pres = json.loads(rec.PartialResult())
                await websocket.send(json.dumps({"type":"partial","partial":pres.get("partial","")}))
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    async with websockets.serve(handler, "127.0.0.1", 2700):
        print("Vosk WS server running on ws://127.0.0.1:2700")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
