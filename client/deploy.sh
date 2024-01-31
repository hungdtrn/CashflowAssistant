#!/bin/bash

REGION=australia-southeast1
PROJECT=anz-ml-engineer
PROJECT_ID=977770941525

BUILD_DIR="../client_build"
rm -fr $BUILD_DIR
mkdir $BUILD_DIR

cp -r * $BUILD_DIR
cp ../requirements.txt $BUILD_DIR


gcloud run deploy client --project $PROJECT  --region=$REGION --allow-unauthenticated \
    --set-env-vars "SERVER_URL=$1" \
    --source=$BUILD_DIR \

rm -fr $BUILD_DIR