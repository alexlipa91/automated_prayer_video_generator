gcloud beta run jobs create prayer-channel-video-builder \
  --image europe-west4-docker.pkg.dev/prayers-channel-369405/images/prayer-channel-video-builder:latest \
  --region europe-west1 \
  --memory 2G \
  --task-timeout 60m \
  --set-env-vars SKIP_SUBS=1 \
  --execute-now

#GOOGLE_APPLICATION_CREDENTIALS=credentials.json
#REGION=europe-west1
#ENDPOINT=run.googleapis.com/apis/run.googleapis.com/v1
#PROJECT=prayers-channel-369405
#JOB=prayer-channel-video-builder
#
gcloud scheduler jobs create http video-builder-scheduled --schedule "0 2 * * *" \
   --http-method=POST \
   --uri=https://europe-west1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/prayers-channel-369405/jobs/prayer-channel-video-builder:run \
   --oauth-service-account-email=195611242118-compute@developer.gserviceaccount.com \
   --location europe-west1