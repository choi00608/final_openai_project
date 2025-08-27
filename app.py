from flask import Flask, request, Response, render_template, send_file
import yaml
from dotenv import load_dotenv
from openai import OpenAI
import base64
import json
import tempfile
import threading
from pathlib import Path

with open("config.yaml") as f:
    config = yaml.safe_load(f)

load_dotenv()
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# 임시 파일 저장 디렉토리
TEMP_DIR = Path(tempfile.gettempdir()) / "images"
TEMP_DIR.mkdir(exist_ok=True)

@app.route("/")
def index():
    title = "OpenAI API Agent School" 
    return render_template('index.html', title=title)

@app.route("/api/chat", methods=["POST"])
def chat_api():    
    data = request.get_json()
    input_message = data.get("input_message", [])
    previous_response_id = data.get("previous_response_id")

    print(f"Input message: {input_message}")
    print(f"Previous response ID: {previous_response_id}")

    def generate():
        nonlocal previous_response_id
        try:
            print("Starting chat API call...")

            # OpenAI API 호출
            try:
                response = client.responses.create(
                    input=input_message,
                    previous_response_id=previous_response_id,
                    stream=True,
                    **config
                )
                print("OpenAI API response created successfully")
            except Exception as api_error:
                error_message = f"OpenAI API 호출 중 오류 발생: {str(api_error)}"
                print(error_message)
                yield f"data: {json.dumps({'type': 'error', 'message': error_message})}\n\n"
                return

            max_repeats = 5
            for _ in range(max_repeats):
                function_call_outputs = []
                for event in response:
                    try:
                        print(f"Processing event type: {event.type}")
                        if event.type == "response.output_text.delta":
                            yield f"data: {json.dumps({'type': 'text_delta', 'delta': event.delta})}\n\n"
                    except Exception as stream_error:
                        error_message = f"스트리밍 처리 중 오류 발생: {str(stream_error)}"
                        print(error_message)
                        yield f"data: {json.dumps({'type': 'error', 'message': error_message})}\n\n"
                        break

                    if event.type == "response.completed":
                        previous_response_id = event.response.id

                    elif event.type == "response.image_generation_call.partial_image":
                        image_name = f"{event.item_id}.{event.output_format}"
                        file_path = TEMP_DIR / image_name
                        with open(file_path, 'wb') as f:
                            f.write(base64.b64decode(event.partial_image_b64))
                        threading.Timer(60.0, lambda: file_path.unlink(missing_ok=True)).start()
                        yield f"data: {json.dumps({'type': 'image_generated', 'image_url': f"/image/{image_name}", 'is_partial': True})}\n\n"

                    elif (event.type == "response.output_item.done") and (event.item.type == "function_call"):
                            try:
                                import function_call
                                func = getattr(function_call, event.item.name)
                                args = json.loads(event.item.arguments)
                                func_output = str(func(**args))
                            except Exception as e:
                                func_output = str(e)

                            function_call_outputs.append({"type": "function_call_output", "call_id": event.item.call_id, "output": func_output})

                # 함수 호출 결과가 있으면 다시 API 호출
                if function_call_outputs:
                    print(f"Making follow-up API call with {len(function_call_outputs)} outputs")
                    response = client.responses.create(
                        input=function_call_outputs,
                        previous_response_id=previous_response_id,
                        stream=True,
                        **config
                    )
                else:
                    print("No function calls, ending stream")
                    break

            yield f"data: {json.dumps({'type': 'done', 'response_id': previous_response_id})}\n\n"
            print("Stream completed successfully")

        except Exception as e:
            import traceback
            print(f"Error in chat API: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(generate(), mimetype='text/plain')

@app.route('/image/<image_name>')
def serve_image(image_name):
    return send_file(
        TEMP_DIR / image_name,
        mimetype=f'image/{image_name.split(".")[-1]}',
        as_attachment=False
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)