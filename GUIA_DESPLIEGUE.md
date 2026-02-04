# GUÍA PASO A PASO: MIGRAR TU APP A LA WEB - 100% GRATIS

## 🎯 ¿Qué vamos a lograr?

Convertir tu aplicación de escritorio en una aplicación web accesible desde cualquier navegador, sin costo alguno.

---

## 📦 PASO 1: PREPARAR LOS ARCHIVOS (5 minutos)

### 1.1 Crea una carpeta en tu escritorio
- Nombre sugerido: `extraccion-datos-web`

### 1.2 Copia estos archivos a la carpeta:
- ✅ `app_web.py` (el nuevo archivo principal web)
- ✅ `apollo_script.py` (tu archivo existente)
- ✅ `apollo_org.py` (tu archivo existente)
- ✅ `lusha_script.py` (tu archivo existente)
- ✅ `lusha_org.py` (tu archivo existente)
- ✅ `signal_script.py` (tu archivo existente)
- ✅ `requirements.txt` (nuevo)
- ✅ `README.md` (nuevo)
- ✅ `.gitignore` (nuevo)

### 1.3 Crea una subcarpeta `.streamlit`
Dentro de la carpeta principal, crea una carpeta llamada `.streamlit` y coloca:
- ✅ `config.toml` (nuevo)

---

## 🌐 PASO 2: CREAR CUENTA EN GITHUB (5 minutos)

### 2.1 Ve a https://github.com
- Haz clic en "Sign up" (Registrarse)
- Ingresa tu email
- Crea una contraseña
- Elige un nombre de usuario (ejemplo: juan-perez)
- Verifica tu cuenta (revisa tu email)

### 2.2 Confirma tu cuenta
- Revisa tu correo electrónico
- Haz clic en el enlace de verificación

✅ **¡Ya tienes cuenta en GitHub!**

---

## 📤 PASO 3: CREAR REPOSITORIO Y SUBIR ARCHIVOS (10 minutos)

### 3.1 Crear el repositorio
1. En GitHub, haz clic en el botón verde "New" (arriba a la izquierda)
2. Nombre del repositorio: `extraccion-datos-web`
3. Descripción: `Herramienta web de extracción de datos`
4. Selecciona "Public" (Público)
5. NO marques "Add a README file"
6. Haz clic en "Create repository"

### 3.2 Subir los archivos (Método Fácil - Arrastrar y Soltar)

1. En la página del repositorio, haz clic en "uploading an existing file"
2. Arrastra TODOS los archivos de tu carpeta `extraccion-datos-web`
   - Incluye la carpeta `.streamlit` completa
3. En el cuadro de mensaje escribe: `Primera versión de la aplicación web`
4. Haz clic en "Commit changes" (botón verde)

⏳ **Espera unos segundos...** GitHub procesará los archivos.

✅ **¡Archivos subidos correctamente!**

---

## 🚀 PASO 4: DESPLEGAR EN STREAMLIT CLOUD (5 minutos)

### 4.1 Ve a https://share.streamlit.io

### 4.2 Inicia sesión con GitHub
1. Haz clic en "Continue with GitHub"
2. Autoriza a Streamlit (botón verde "Authorize")
3. Te redirigirá a tu panel de Streamlit

### 4.3 Crear nueva aplicación
1. Haz clic en "New app" (botón azul)
2. Completa los campos:
   - **Repository:** Selecciona `TU_USUARIO/extraccion-datos-web`
   - **Branch:** Deja `main`
   - **Main file path:** Escribe `app_web.py`
3. Haz clic en "Deploy!" (botón rojo)

⏳ **Espera 2-3 minutos...** Streamlit instalará las dependencias y lanzará tu app.

---

## 🎉 PASO 5: ¡TU APP ESTÁ LISTA!

### Tu aplicación estará en una URL como:
```
https://TU_USUARIO-extraccion-datos-web-app-web-abc123.streamlit.app
```

### 🔗 Comparte esta URL con quien quieras
- Funciona en computadoras, tablets y celulares
- No necesita instalación
- Acceso 24/7 desde cualquier lugar

---

## 🎮 CÓMO USAR TU NUEVA APP WEB

### Interfaz de Usuario

```
┌─────────────────────────────────────────┐
│  BARRA LATERAL (Izquierda)             │
├─────────────────────────────────────────┤
│  🔑 API Keys                            │
│  - Apollo API Key                       │
│  - Lusha API Key                        │
│  - SignalHire API Key                   │
│                                         │
│  🌎 Países                              │
│  - Norteamérica                         │
│  - Centroamérica                        │
│  - Suramérica                           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  ÁREA PRINCIPAL (Centro)                │
├─────────────────────────────────────────┤
│  📁 Subir archivos CSV                  │
│  - Cargos                               │
│  - Empresas                             │
│  - IDs Organizaciones                   │
│                                         │
│  🚀 Botones de acción                   │
│  [Apollo Contactos] [Apollo Orgs]       │
│  [Lusha Contactos] [Lusha Orgs]         │
│                                         │
│  📋 Consola de ejecución                │
│  (Muestra el progreso en tiempo real)   │
│                                         │
│  💾 Descargar resultados                │
│  (Aparece cuando termina el proceso)    │
└─────────────────────────────────────────┘
```

### Flujo de Uso

1. **Ingresa tus API Keys** en la barra lateral izquierda
2. **Selecciona países** (expande las regiones y marca los países)
3. **Sube archivos CSV** usando los botones de carga
4. **Haz clic en el botón** de la búsqueda que necesites
5. **Observa el progreso** en la consola
6. **Descarga los resultados** cuando aparezcan los botones de descarga

---

## 🔄 ACTUALIZAR LA APLICACIÓN

### Si necesitas hacer cambios:

1. Modifica los archivos en tu computadora
2. Ve a tu repositorio en GitHub
3. Haz clic en "Add file" → "Upload files"
4. Arrastra los archivos modificados
5. Haz clic en "Commit changes"

⚡ **Streamlit detectará los cambios y actualizará automáticamente**

---

## ❓ SOLUCIÓN DE PROBLEMAS COMUNES

### La app no carga / Error 404
- ✅ Verifica que `app_web.py` esté en GitHub
- ✅ Revisa que el nombre del archivo sea exacto (con minúsculas)

### Error "ModuleNotFoundError"
- ✅ Asegúrate que `requirements.txt` esté en GitHub
- ✅ Verifica que todos los scripts (.py) estén subidos

### La búsqueda no funciona
- ✅ Revisa que la API Key sea correcta
- ✅ Verifica que hayas seleccionado países
- ✅ Confirma que los archivos CSV tengan el formato correcto

### Archivos CSV no se procesan
- ✅ Verifica que tengan encabezados
- ✅ Revisa que no tengan caracteres especiales raros
- ✅ Usa encoding UTF-8

---

## 💰 COSTO TOTAL: $0 (GRATIS)

| Servicio | Plan | Costo Mensual |
|----------|------|---------------|
| GitHub | Free | $0 |
| Streamlit Cloud | Community | $0 |
| **TOTAL** | | **$0** |

### Límites del Plan Gratuito (Muy generosos):

**Streamlit Cloud Free:**
- ✅ Apps ilimitadas
- ✅ 1GB de recursos por app
- ✅ Sin límite de usuarios
- ✅ SSL/HTTPS incluido
- ✅ Dominio personalizado (próximamente)

**GitHub Free:**
- ✅ Repositorios públicos ilimitados
- ✅ 500MB de almacenamiento
- ✅ Colaboradores ilimitados

---

## 🌟 VENTAJAS DE LA VERSIÓN WEB

| Antes (Desktop) | Ahora (Web) |
|----------------|-------------|
| Instalar Python | ✅ Navegador solamente |
| Solo Windows/Mac | ✅ Cualquier dispositivo |
| Actualizar manualmente | ✅ Auto-actualización |
| Una computadora | ✅ Desde cualquier lugar |
| Compartir archivos .exe | ✅ Compartir URL |
| Sin respaldo | ✅ Código en la nube |

---

## 📱 ACCESO MÓVIL

Tu app funciona perfectamente en:
- 📱 iPhone / iPad
- 📱 Android
- 💻 Mac / Windows / Linux
- 🌐 Cualquier navegador moderno

---

## 🔐 SEGURIDAD

- ✅ Las API Keys se ingresan por sesión (no se guardan)
- ✅ Los archivos se procesan temporalmente
- ✅ Conexión HTTPS segura
- ✅ Sin almacenamiento permanente de datos sensibles

---

## 📧 SOPORTE

Si tienes dudas o problemas:
1. Revisa esta guía completa
2. Verifica la consola de errores en la app
3. Revisa los logs en Streamlit Cloud

---

## 🎓 RECURSOS ADICIONALES

- 📖 Documentación de Streamlit: https://docs.streamlit.io
- 📖 Guías de GitHub: https://guides.github.com
- 💬 Comunidad Streamlit: https://discuss.streamlit.io

---

## ✨ ¡FELICIDADES!

Has migrado exitosamente tu aplicación de escritorio a la web, completamente gratis y accesible desde cualquier lugar del mundo.

**🚀 Tu app está lista para usar. ¡Comparte la URL con tu equipo!**

---

*Última actualización: Febrero 2026*
*Versión de la guía: 1.0*
