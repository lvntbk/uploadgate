FROM nginx:1.27.4-alpine

COPY nginx.conf /etc/nginx/nginx.conf

# uploads için klasör (K8s'te PVC mount gelecek)
RUN mkdir -p /data/uploads

EXPOSE 80
