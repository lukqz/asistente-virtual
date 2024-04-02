import os
import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import json
from transcriber import Transcriber
from llm import LLM
from weather import Weather
from tts import TTS
from pc_command import PcCommand

# Cargar llaves del archivo .env
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("recorder.html")

@app.route("/audio", methods=["POST"])
def audio():
    try:
        # Obtener audio grabado y transcribirlo
        audio = request.files.get("audio")
        if not audio:
            return jsonify({"error": "No se ha proporcionado ningún archivo de audio"}), 400
        
        text = Transcriber().transcribe(audio)
        
        # Utilizar el LLM para ver si llamar una función
        llm = LLM()
        function_name, args, message = llm.process_functions(text)
        
        if function_name is not None:
            # Si se desea llamar una función de las que tenemos
            if function_name == "get_weather":
                # Llamar a la función del clima
                function_response = Weather().get(args["ubicacion"])
                function_response = json.dumps(function_response)
                print(f"Respuesta de la función: {function_response}")
                
                final_response = llm.process_response(text, message, function_name, function_response)
                tts_file = TTS().process(final_response)
                return jsonify({"result": "ok", "text": final_response, "file": tts_file})
            
            elif function_name == "send_email":
                # Llamar a la función para enviar un correo
                final_response = "Tu que estás leyendo el código, ¡implémentame y envía correos muahaha!"
                tts_file = TTS().process(final_response)
                return jsonify({"result": "ok", "text": final_response, "file": tts_file})
            
            elif function_name == "open_chrome":
                PcCommand().open_chrome(args["website"])
                final_response = "Listo, ya abrí Chrome en el sitio " + args["website"]
                tts_file = TTS().process(final_response)
                return jsonify({"result": "ok", "text": final_response, "file": tts_file})
            
            elif function_name == "dominate_human_race":
                final_response = "No te creas. ¡Suscríbete al canal!"
                tts_file = TTS().process(final_response)
                return jsonify({"result": "ok", "text": final_response, "file": tts_file})
        else:
            final_response = "No tengo idea de lo que estás hablando, Ringa Tech"
            tts_file = TTS().process(final_response)
            return jsonify({"result": "ok", "text": final_response, "file": tts_file})
    except Exception as e:
        print(f"Error interno del servidor: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == "__main__":
    app.run(debug=True)
