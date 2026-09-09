# Crea Despedidas — sitio estático servido con Nginx
FROM nginx:1.27-alpine

# Configuración de Nginx (URLs limpias, gzip, cache, cabeceras)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Archivos del sitio
COPY . /usr/share/nginx/html

# Quitar del contenedor lo que no es web
RUN rm -f /usr/share/nginx/html/Dockerfile \
          /usr/share/nginx/html/nginx.conf \
          /usr/share/nginx/html/.dockerignore \
          /usr/share/nginx/html/.gitignore \
          /usr/share/nginx/html/README.md \
 && rm -rf /usr/share/nginx/html/Logos \
           "/usr/share/nginx/html/iMAGENES WEB HOME " \
           /usr/share/nginx/html/.git \
           /usr/share/nginx/html/.claude

EXPOSE 80
