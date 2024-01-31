REGION=australia-southeast1
PROJECT=anz-ml-engineer
PROJECT_ID=977770941525
SOURCE_DIR="."

gcloud projects add-iam-policy-binding ${PROJECT} \
    --member=serviceAccount:${PROJECT_ID}-compute@developer.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor \

gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
    --member=serviceAccount:${PROJECT_ID}-compute@developer.gserviceaccount.com \
    --role="roles/secretmanager.secretAccessor"
