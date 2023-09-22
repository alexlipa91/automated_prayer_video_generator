from datetime import datetime

import firebase_admin
import flask as flask
from firebase_admin import firestore
import functions_framework

firebase_admin.initialize_app()

@functions_framework.http
def run(request):
    date_param = datetime.now().strftime("%Y-%m-%d")
    db = firestore.client()
    video_id = db.collection("video_uploads").document(date_param).get().to_dict()["video_id"]
    return flask.redirect("https://studio.youtube.com/video/{}/monetization/ads".format(video_id), code=302)
