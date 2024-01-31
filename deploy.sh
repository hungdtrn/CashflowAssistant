#!/bin/bash

REGION=australia-southeast2
PROJECT=anz-ml-engineer
SOURCE_DIR="."
glcoud run deploy data_insight --project $PROJECT  --region=$REGION --allow-unauthenticated \
    --update-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest \
    --set-env-vars "MODEL=gpt-3.5-turbo" \
    --set-env-vars SERVER_URL=http://0.0.0.0:3000 \
    --source=$SOURCE_DIR \
