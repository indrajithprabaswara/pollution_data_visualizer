# Deployment Setup

```
gcloud pubsub topics create collect-pollution

gcloud functions deploy collectPollution \
  --runtime python311 \
  --trigger-topic collect-pollution \
  --entry-point pubsub_collect \
  --set-env-vars WAQI_TOKEN=$WAQI_TOKEN,SECRET_KEY=$SECRET_KEY \
  --source ..

gcloud scheduler jobs create pubsub pollution-schedule \
  --schedule="*/30 * * * *" \
  --topic=collect-pollution \
  --message-body="{}"
```
