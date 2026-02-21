# UploadGate 🚀

Kubernetes üzerinde çalışan container tabanlı bir dosya yükleme (upload gateway) sistemidir.

## Mimari

Client
→ Nginx Router
→ Upload API (FastAPI)
→ Persistent Volume (PVC)

## Teknolojiler

- Kubernetes (k3s)
- Helm
- Nginx
- FastAPI
- Docker
- PVC Storage

## Authentication

Header:

X-Upload-Token: change-me-upload-token

## Kurulum

Namespace:
kubectl create namespace uploadgate --dry-run=client -o yaml | kubectl apply -f -

Secret:
kubectl -n uploadgate create secret generic uploadgate-auth \
--from-literal=UPLOAD_TOKEN="change-me-upload-token"

Deploy:
helm -n uploadgate upgrade --install uploadgate ./helm

## Demo

Upload:
curl -X PUT http://127.0.0.1:31880/upload/hello.txt \
-H "X-Upload-Token: change-me-upload-token" \
--data-binary @hello.txt

Listeleme:
curl http://127.0.0.1:31880/list \
-H "X-Upload-Token: change-me-upload-token"

Metrics:
curl http://127.0.0.1:31880/metrics

## Öğrenilenler

- Kubernetes networking
- Helm deployment
- Reverse proxy routing
- Secret management
- Persistent storage

## Geliştirici

Levent İnce
Backend & DevOps Developer
