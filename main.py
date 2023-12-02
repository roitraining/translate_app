from __future__ import annotations

import os
import flask 
import uuid

from google.api_core.retry import Retry
from google.cloud import translate

app = flask.Flask(__name__)
app.secret_key = str(uuid.uuid4())

translate_client = translate.TranslationServiceClient()

@app.route('/', methods=['POST'])
def handle_translation():
    try:
        request_json = flask.request.get_json()
        calls = request_json["calls"]
        project =  os.getenv('PROJECT')
        target =  os.getenv('TARGET_LANGUAGE', 'fr')
        translated = translate_text([call[0] for call in calls], project, target)
        return flask.jsonify({"replies": translated})
    
    except Exception as err:
        return flask.make_response(
            flask.jsonify({"errorMessage": f"Unexpected error {type(err)}:{err}"}),
            400,
        )

def extract_project_from_caller(job: str) -> str:
    path = job.split("/")
    return path[4] if len(path) > 4 else None


def translate_text(
    calls: list[str], project: str, target_language_code: str
) -> list[str]:
    location = "us-central1"
    parent = f"projects/{project}/locations/{location}"
    response = translate_client.translate_text(
        request={
            "parent": parent,
            "contents": calls,
            "target_language_code": target_language_code,
            "mime_type": "text/plain",
        },
        retry=Retry(),
    )
    return [translation.translated_text for translation in response.translations]

if __name__ == '__main__':
    PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080
    app.run(host='127.0.0.1', port=PORT, debug=True)