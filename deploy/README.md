# Deployment Setup

```
gcloud pubsub topics create collect-pollution

gcloud functions deploy collectPollution \
  --runtime python39 \
  --trigger-topic collect-pollution \
  --entry-point run

gcloud scheduler jobs create pubsub collect-pollution-cron \
  --schedule="*/30 * * * *" \
  --topic=collect-pollution \
  --message-body="{}"
```
