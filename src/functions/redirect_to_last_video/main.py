from datetime import datetime

import firebase_admin
import flask as flask
from firebase_admin import firestore
import functions_framework

firebase_admin.initialize_app()


@functions_framework.http
def run(request):
    date_param = datetime.now().strftime("%Y-%m-%d")
    lang = request.args.get("lang", "it")
    db = firestore.client()

    if lang == "es":
        field = "video_id_es"
    else:
        field = "video_id"

    video_id = db.collection("video_uploads").document(date_param).get().to_dict()[field]
    return flask.redirect("https://studio.youtube.com/video/{}/monetization/ads".format(video_id), code=302)
