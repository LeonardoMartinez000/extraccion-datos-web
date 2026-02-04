# 🔍 Herramienta de Extracción de Datos - Versión Web

Aplicación web para extraer datos de contactos y organizaciones desde APIs de Apollo, Lusha y SignalHire.

## 🚀 Despliegue Gratuito en Streamlit Cloud

### Paso 1: Preparar los Archivos

1. Crea una carpeta en tu computadora llamada `extraccion-datos-web`
2. Copia los siguientes archivos a esa carpeta:
   - `app_web.py` (archivo principal)
   - `requirements.txt`
   - `apollo_script.py`
   - `apollo_org.py`
   - `lusha_script.py`
   - `lusha_org.py`
   - `signal_script.py` (si lo tienes)
   - Crea una carpeta `.streamlit` y dentro coloca `config.toml`

### Paso 2: Crear Repositorio en GitHub

1. Ve a https://github.com y crea una cuenta (si no tienes)
2. Haz clic en "New repository"
3. Nombre: `extraccion-datos-web`
4. Descripción: "Herramienta web de extracción de datos"
5. Selecciona "Public"
6. Haz clic en "Create repository"

### Paso 3: Subir los Archivos a GitHub

#### Opción A: Usar GitHub Web (Más fácil)

1. En tu repositorio, haz clic en "uploading an existing file"
2. Arrastra TODOS los archivos de tu carpeta
3. Escribe un mensaje: "Primera versión de la app"
4. Haz clic en "Commit changes"

#### Opción B: Usar Git desde la terminal

```bash
cd extraccion-datos-web
git init
git add .
git commit -m "Primera versión de la app"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/extraccion-datos-web.git
git push -u origin main
```

### Paso 4: Desplegar en Streamlit Cloud

1. Ve a https://share.streamlit.io
2. Haz clic en "Sign in with GitHub"
3. Autoriza a Streamlit
4. Haz clic en "New app"
5. Selecciona:
   - Repository: `TU_USUARIO/extraccion-datos-web`
   - Branch: `main`
   - Main file path: `app_web.py`
6. Haz clic en "Deploy!"

### Paso 5: ¡Listo! 🎉

Tu aplicación estará disponible en una URL como:
`https://TU_USUARIO-extraccion-datos-web-app-web-abc123.streamlit.app`

## 📱 Cómo Usar la Aplicación

1. **Ingresa las API Keys** en la barra lateral
2. **Selecciona países** donde quieres buscar
3. **Sube archivos CSV** con empresas, cargos o IDs
4. **Haz clic en el botón** de la búsqueda que necesites
5. **Descarga los resultados** cuando termine el proceso

## 📋 Formato de Archivos CSV

### Cargos CSV
```csv
cargo
CEO
CTO
Director
Manager
```

### Empresas CSV
```csv
empresa
Google
Microsoft
Amazon
Apple
```

### IDs Organizaciones CSV
```csv
organization_id
123456
789012
345678
```

## ⚙️ Características

✅ **100% Gratuito** - Sin límites de uso
✅ **Accesible desde cualquier lugar** - Solo necesitas internet
✅ **Sin instalación** - Funciona desde el navegador
✅ **Seguro** - Las API Keys no se almacenan
✅ **Fácil de usar** - Interfaz intuitiva
✅ **Descarga múltiple** - Descarga archivos individuales o todos en ZIP

## 🔧 Tecnologías Utilizadas

- **Python 3.10+**
- **Streamlit** - Framework web
- **Pandas** - Procesamiento de datos
- **Requests** - Llamadas a APIs

## 📞 Soporte

Si tienes problemas:
1. Revisa que todos los archivos estén en GitHub
2. Verifica que las API Keys sean correctas
3. Asegúrate que los archivos CSV tengan el formato correcto

## 🔄 Actualizar la Aplicación

Para actualizar la aplicación:
1. Modifica los archivos en tu computadora
2. Sube los cambios a GitHub
3. Streamlit Cloud actualizará automáticamente

O desde terminal:
```bash
git add .
git commit -m "Actualización de la app"
git push
```

## 🌟 Ventajas de la Versión Web

✅ No necesitas instalar Python
✅ Funciona en cualquier sistema operativo
✅ Accesible desde móvil o tablet
✅ Puedes compartir la URL con tu equipo
✅ Actualizaciones automáticas
✅ Sin mantenimiento de servidores

---

**Desarrollado con ❤️ usando Streamlit**
