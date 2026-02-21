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

---

## 🔐 Security

UploadGate güvenlik odaklı tasarlanmıştır.

### Authentication
- Upload endpoint'leri token tabanlı authentication ile korunur
- Token uygulama içinde hardcode edilmez
- Kubernetes Secret üzerinden environment variable olarak mount edilir

### Token Security
- Production ortamında token'ın **SHA256 hash** değeri saklanır
- Plain-text token saklanması engellenmiştir
- Constant-time karşılaştırma (`hmac.compare_digest`) kullanılır  
  → timing attack riskini azaltır

### Runtime Safety
- AUTH_DISABLED flag yalnızca development ortamı içindir
- Production ortamında token zorunludur
- Path traversal koruması uygulanmıştır
- Upload boyutu limitlenmiştir

Bu yaklaşım gerçek production Kubernetes sistemlerindeki secret yönetimi ve güvenlik pratiklerini simüle eder.

