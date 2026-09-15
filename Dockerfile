FROM nginx:1.27-alpine
ENV PORT=8080
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY . /usr/share/nginx/html
RUN rm -f /usr/share/nginx/html/Dockerfile /usr/share/nginx/html/nginx.conf.template /usr/share/nginx/html/build.py /usr/share/nginx/html/railway.json && rm -rf /usr/share/nginx/html/src /usr/share/nginx/html/.git
