# Desplegar en EasyPanel

Sitio 100 % estático (HTML/CSS/JS). Se sirve con Nginx dentro de un contenedor.
Ya están listos: `Dockerfile`, `nginx.conf`, `.dockerignore`.

---

## 1. Subir el código a GitHub

EasyPanel despliega desde un repositorio Git. Crea un repo vacío en GitHub
(privado vale) y luego:

```bash
cd "/Users/pablosaez/web crea despedidas"
git remote add origin https://github.com/TU_USUARIO/crea-despedidas.git
git push -u origin main
```

## 2. Crear el servicio en EasyPanel

1. Entra en tu panel → abre (o crea) un **Project**.
2. **+ Service → App**.
3. Pestaña **Source**:
   - Provider: **GitHub** (conéctalo si es la primera vez).
   - Repository: `TU_USUARIO/crea-despedidas`  ·  Branch: `main`.
4. Pestaña **Build**:
   - Method: **Dockerfile**
   - Dockerfile path: `Dockerfile`  (raíz del repo)
5. Pestaña **Deploy** → **Deploy**. EasyPanel construye la imagen y arranca el contenedor.

## 3. Puerto

El contenedor Nginx escucha en el **puerto 80**. EasyPanel suele detectarlo por el
`EXPOSE 80`. Si te pide el puerto en la pestaña **Domains** / **Proxy**, pon `80`.

## 4. Dominio y HTTPS

1. Pestaña **Domains → Add Domain**.
   - Para probar sin tocar la web actual: usa un subdominio, p. ej. `nueva.creadespedidas.com`.
   - Para producción: `creadespedidas.com` y `www.creadespedidas.com`.
2. En tu proveedor de DNS crea un registro **A** apuntando el (sub)dominio a la
   **IP pública del servidor de EasyPanel**.
3. Marca **HTTPS / SSL** — EasyPanel emite el certificado Let's Encrypt automáticamente
   en cuanto el DNS resuelve.

## 5. Actualizaciones

Cada `git push` a `main` puedes redeployarlo desde EasyPanel (o activa **Auto Deploy**
en la pestaña Source para que sea automático).

---

## Alternativa sin Dockerfile (build "Static" de EasyPanel)

Si prefieres no usar Docker:

1. **+ Service → App** → Source = GitHub (igual que arriba).
2. **Build → Method: Static**.
   - Output/Public directory: `.` (raíz)
   - SPA / History API fallback: **desactivado**.
3. Deploy.

EasyPanel lo sirve con su propio Nginx. Pierdes el control fino de cache/cabeceras
que da `nginx.conf`, pero funciona igual.

---

## Notas

- **Tailwind** se carga por CDN (`cdn.tailwindcss.com`). Funciona en producción, pero
  para máximo rendimiento conviene compilar Tailwind a un CSS estático más adelante
  (no bloquea el despliegue).
- Las carpetas `Logos/` e `iMAGENES WEB HOME/` **no se despliegan** (están en
  `.gitignore` y `.dockerignore`); las fotos usadas ya están optimizadas en `assets/`.
- URLs limpias ya resueltas: `/restaurantes-despedidas-cumpleanos-valencia/`, etc.
