#!/bin/bash

REGION=australia-southeast1
PROJECT=anz-ml-engineer
PROJECT_ID=977770941525
SOURCE_DIR="."

gcloud projects add-iam-policy-binding ${PROJECT} \
    --member=serviceAccount:${PROJECT_ID}-compute@developer.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor \

gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
    --member="serviceAccount:${PROJECT_ID}-compute@developer.gserviceaccount.com \
    --role="roles/secretmanager.secretAccessor"


gcloud run deploy data_insight --project $PROJECT  --region=$REGION --allow-unauthenticated \
    --update-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest \
    --set-env-vars "MODEL=gpt-3.5-turbo" \
    --set-env-vars SERVER_URL=http://0.0.0.0:3000 \
    --source=$SOURCE_DIR \

