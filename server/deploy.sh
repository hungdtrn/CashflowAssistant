#!/bin/bash

REGION=australia-southeast1
PROJECT=anz-ml-engineer
PROJECT_ID=977770941525

BUILD_DIR="../server_build"
rm -fr $BUILD_DIR
mkdir $BUILD_DIR

cp -r * $BUILD_DIR
cp ../requirements.txt $BUILD_DIR


gcloud run deploy server --project $PROJECT  --region=$REGION --allow-unauthenticated \
    --update-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest \
    --set-env-vars "OPENAI_MODEL=gpt-3.5-turbo" \
    --source=$BUILD_DIR \

rm -fr $BUILD_DIR