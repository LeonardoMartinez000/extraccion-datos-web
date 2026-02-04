# 🎯 TUTORIAL VISUAL: DE APP DE ESCRITORIO A APP WEB

## 📚 ÍNDICE RÁPIDO
1. [Introducción](#introducción)
2. [Preparación (5 min)](#paso-1-preparación)
3. [GitHub (10 min)](#paso-2-github)
4. [Streamlit Cloud (5 min)](#paso-3-streamlit)
5. [Uso de la App](#paso-4-uso)
6. [Solución de Problemas](#problemas-comunes)

---

## 🌟 INTRODUCCIÓN

### ¿Qué lograremos?

```
ANTES                          DESPUÉS
┌────────────────┐            ┌────────────────┐
│  💻 Desktop    │            │  🌐 Web App    │
│  Solo Windows  │    →→→     │  Anywhere      │
│  Instalar .exe │            │  URL Pública   │
└────────────────┘            └────────────────┘
```

### Beneficios

✅ **Accesible desde cualquier lugar**
✅ **Sin instalación** - Solo navegador
✅ **Funciona en móviles** 📱
✅ **100% Gratis** 💰
✅ **Fácil de compartir** 🔗
✅ **Auto-actualización** 🔄

---

## 📦 PASO 1: PREPARACIÓN (5 minutos)

### 1.1 Estructura de carpetas

Crea esta estructura en tu escritorio:

```
📁 extraccion-datos-web/
├── 📄 app_web.py                 ← Archivo principal (NUEVO)
├── 📄 requirements.txt           ← Dependencias (NUEVO)
├── 📄 README.md                  ← Documentación (NUEVO)
├── 📄 .gitignore                 ← Configuración Git (NUEVO)
├── 📄 apollo_script.py           ← Tu script existente
├── 📄 apollo_org.py              ← Tu script existente
├── 📄 lusha_script.py            ← Tu script existente
├── 📄 lusha_org.py               ← Tu script existente
├── 📄 signal_script.py           ← Tu script existente
└── 📁 .streamlit/
    └── 📄 config.toml            ← Configuración Streamlit (NUEVO)
```

### 1.2 Lista de verificación

- [ ] Carpeta principal creada
- [ ] Todos los archivos copiados
- [ ] Carpeta `.streamlit` creada
- [ ] Archivo `config.toml` dentro de `.streamlit`

---

## 🐙 PASO 2: GITHUB (10 minutos)

### 2.1 Crear cuenta GitHub

#### Paso A: Registro

1. Abre tu navegador
2. Ve a: **https://github.com**
3. Haz clic en **"Sign up"**

```
┌─────────────────────────────────────┐
│  GitHub                             │
├─────────────────────────────────────┤
│  Email:    [tu_email@example.com ] │
│  Password: [●●●●●●●●●●●●●●●●●●●●] │
│  Username: [tu-nombre-usuario     ] │
│                                     │
│  [✓] I agree to the terms          │
│                                     │
│  [  Sign up  ]                      │
└─────────────────────────────────────┘
```

4. **Revisa tu email** y confirma la cuenta
5. **Completa el perfil** básico

#### Paso B: Crear Repositorio

1. En GitHub, arriba a la derecha: **"+" → "New repository"**

```
┌─────────────────────────────────────┐
│  Create a new repository            │
├─────────────────────────────────────┤
│  Owner: tu-usuario                  │
│                                     │
│  Repository name:                   │
│  [ extraccion-datos-web ]           │
│                                     │
│  Description (optional):            │
│  [ Herramienta de extracción ]      │
│                                     │
│  ○ Public   ● Private               │
│  ☑ Public                           │
│                                     │
│  Initialize this repository:        │
│  ☐ Add a README                     │
│  ☐ Add .gitignore                   │
│  ☐ Choose a license                 │
│                                     │
│  [ Create repository ]              │
└─────────────────────────────────────┘
```

2. Selecciona **"Public"** (obligatorio para plan gratuito de Streamlit)
3. **NO** marques ningún checkbox de inicialización
4. Haz clic en **"Create repository"**

### 2.2 Subir archivos

#### Método Fácil: Drag & Drop

1. En la página del repositorio recién creado
2. Haz clic en: **"uploading an existing file"**

```
┌─────────────────────────────────────┐
│  📤 Upload files                     │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐  │
│   │                             │  │
│   │  Drag files here            │  │
│   │  or click to browse         │  │
│   │                             │  │
│   └─────────────────────────────┘  │
│                                     │
│  Commit message:                    │
│  [ Primera versión ]                │
│                                     │
│  [ Commit changes ]                 │
└─────────────────────────────────────┘
```

3. **Arrastra TODOS los archivos** de tu carpeta
4. Escribe mensaje: **"Primera versión de la aplicación web"**
5. Haz clic en **"Commit changes"**

⏳ **Espera 10-20 segundos...**

✅ **¡Archivos subidos!**

### 2.3 Verificar

Tu repositorio debe verse así:

```
extraccion-datos-web/
├── .gitignore
├── .streamlit/
│   └── config.toml
├── README.md
├── app_web.py
├── apollo_org.py
├── apollo_script.py
├── lusha_org.py
├── lusha_script.py
├── requirements.txt
└── signal_script.py
```

---

## 🚀 PASO 3: STREAMLIT CLOUD (5 minutos)

### 3.1 Acceder a Streamlit Cloud

1. Abre nueva pestaña
2. Ve a: **https://share.streamlit.io**

```
┌─────────────────────────────────────┐
│  🎈 Streamlit Cloud                  │
├─────────────────────────────────────┤
│                                     │
│  Build and share data apps          │
│  powered by Python                  │
│                                     │
│  [ Continue with GitHub ]           │
│                                     │
│  [ Continue with Google ]           │
│                                     │
│  [ Sign up with email ]             │
└─────────────────────────────────────┘
```

3. Haz clic en **"Continue with GitHub"**

### 3.2 Autorizar Streamlit

```
┌─────────────────────────────────────┐
│  GitHub                             │
├─────────────────────────────────────┤
│  Authorize Streamlit                │
│                                     │
│  Streamlit wants to:                │
│  ✓ Access your repositories         │
│  ✓ Read user data                   │
│                                     │
│  [ Authorize streamlit ]            │
└─────────────────────────────────────┘
```

1. Haz clic en **"Authorize streamlit"**
2. Te redirigirá a tu dashboard de Streamlit

### 3.3 Crear nueva app

1. En el dashboard, haz clic: **"New app"**

```
┌─────────────────────────────────────┐
│  Deploy an app                      │
├─────────────────────────────────────┤
│  Repository:                        │
│  [ tu-usuario/extraccion-datos-web ]│
│                                     │
│  Branch:                            │
│  [ main                        ▼ ] │
│                                     │
│  Main file path:                    │
│  [ app_web.py                     ] │
│                                     │
│  App URL (optional):                │
│  [ mi-app-extraccion              ] │
│                                     │
│  [ Deploy! ]                        │
└─────────────────────────────────────┘
```

2. Completa:
   - **Repository**: Selecciona tu repo `extraccion-datos-web`
   - **Branch**: Deja `main`
   - **Main file path**: Escribe `app_web.py`
   - **App URL**: (Opcional) Personaliza la URL

3. Haz clic en **"Deploy!"**

### 3.4 Esperar despliegue

```
┌─────────────────────────────────────┐
│  🔄 Deploying your app...            │
├─────────────────────────────────────┤
│                                     │
│  ⏳ Installing dependencies...       │
│  ⏳ Starting app...                  │
│                                     │
│  This may take 2-3 minutes          │
└─────────────────────────────────────┘
```

⏳ **Espera 2-3 minutos...**

### 3.5 ¡App lista!

```
┌─────────────────────────────────────┐
│  ✅ Your app is live!                │
├─────────────────────────────────────┤
│                                     │
│  🔗 https://tu-usuario-extraccion   │
│     -datos-web-app-web-abc.         │
│     streamlit.app                   │
│                                     │
│  [ Open app ] [ Share ] [ Settings ]│
└─────────────────────────────────────┘
```

✅ **¡TU APP ESTÁ EN LÍNEA!**

---

## 🎮 PASO 4: USO DE LA APP WEB

### 4.1 Interfaz Principal

```
┌─────────────────────────────────────────────────────────────┐
│  🔍 Herramienta de Extracción de Datos v4.0                 │
├────────────────────┬────────────────────────────────────────┤
│  SIDEBAR           │  ÁREA PRINCIPAL                        │
│                    │                                        │
│  🔑 API Keys       │  📊 Extracción de Contactos            │
│  ───────────       │  ────────────────────────────          │
│  Apollo: [●●●●●]   │                                        │
│  Lusha:  [●●●●●]   │  📁 Archivos de Entrada               │
│  Signal: [●●●●●]   │  ┌──────┐ ┌──────┐ ┌──────┐          │
│                    │  │Cargos│ │Empre │ │ IDs  │          │
│  🌎 Países         │  │Browse│ │Browse│ │Browse│          │
│  ───────────       │  └──────┘ └──────┘ └──────┘          │
│  ☑ United States   │                                        │
│  ☑ Mexico          │  🚀 Ejecutar Extracción               │
│  ☑ Colombia        │  ┌────────┬────────┬────────┐         │
│  ☐ Argentina       │  │Apollo  │Apollo  │Lusha   │         │
│  ☐ Brazil          │  │Contact │  Org   │Contact │         │
│  ...               │  └────────┴────────┴────────┘         │
│                    │                                        │
│                    │  📋 Consola de Ejecución              │
│                    │  ┌──────────────────────────┐         │
│                    │  │[10:30:15] 🚀 Iniciando...│         │
│                    │  │[10:30:16] ✅ Validado    │         │
│                    │  │[10:30:20] 📊 Procesando..│         │
│                    │  └──────────────────────────┘         │
│                    │                                        │
│                    │  💾 Descargar Resultados              │
│                    │  [ 📥 resultados_apollo.csv ]         │
└────────────────────┴────────────────────────────────────────┘
```

### 4.2 Flujo de trabajo

#### Paso A: Configurar

1. **Ingresa API Keys** en la barra lateral
2. **Selecciona países** (marca los checkboxes)

#### Paso B: Cargar datos

1. Haz clic en **"Browse"** de cada archivo
2. Selecciona tu CSV correspondiente
3. Verás el nombre del archivo cargado

#### Paso C: Ejecutar

1. Haz clic en el botón de la búsqueda que necesites:
   - **🟡 Apollo Contactos** → Buscar contactos en empresas
   - **🟡 Apollo Organizaciones** → Info de organizaciones por ID
   - **🟣 Lusha Contactos** → Buscar contactos en empresas
   - **🟣 Lusha Organizaciones** → Info de organizaciones por ID

#### Paso D: Monitorear

Observa la consola en tiempo real:

```
[10:30:15] 🚀 Iniciando bÃºsqueda de contactos en Apollo...
[10:30:16] ✅ Validado. 10 empresas y 5 cargos.
[10:30:20] 🔎 Buscando en Apollo: Google...
[10:30:22]   -> Se encontraron 15 contactos en este lote.
[10:30:25] 🔎 Buscando en Apollo: Microsoft...
...
[10:31:00] ✅ Proceso completado. 45 contactos encontrados.
```

#### Paso E: Descargar

1. Aparecerán botones de descarga
2. Haz clic en **"📥 Descargar resultados_apollo.csv"**
3. El archivo se descargará a tu computadora

---

## 🔧 PROBLEMAS COMUNES

### ❌ "App failed to start"

**Causa**: Error en `requirements.txt` o archivos faltantes

**Solución**:
1. Ve a tu repositorio en GitHub
2. Verifica que estos archivos estén presentes:
   - `app_web.py`
   - `requirements.txt`
   - Todos los scripts `.py`
3. Revisa los logs en Streamlit Cloud

### ❌ "ModuleNotFoundError: No module named 'apollo_script'"

**Causa**: Falta el archivo `apollo_script.py`

**Solución**:
1. Ve a GitHub
2. Sube el archivo faltante
3. Streamlit se actualizará automáticamente

### ❌ "API Key inválida"

**Causa**: La API Key es incorrecta o expiró

**Solución**:
1. Verifica que la API Key sea correcta
2. Revisa que no tenga espacios al inicio/final
3. Confirma que la API Key esté activa

### ❌ "No se encontraron resultados"

**Causas posibles**:
- CSV mal formateado
- Países no seleccionados
- Sin coincidencias en las búsquedas

**Solución**:
1. Revisa el formato del CSV
2. Confirma que hay países seleccionados
3. Verifica en la consola los mensajes de error

---

## 🎓 TIPS PRO

### 💡 Tip 1: Compartir con equipo

Simplemente comparte la URL de tu app:
```
https://tu-usuario-extraccion-datos-web.streamlit.app
```

### 💡 Tip 2: Usar en móvil

1. Abre el navegador de tu celular
2. Ingresa la URL de tu app
3. Agrega a pantalla de inicio

### 💡 Tip 3: Actualizar la app

Para actualizar la aplicación:
1. Modifica archivos en tu computadora
2. Sube a GitHub (mismo proceso)
3. Streamlit detecta cambios y actualiza automáticamente

### 💡 Tip 4: Ver logs en vivo

En Streamlit Cloud:
1. Haz clic en **"Manage app"**
2. Ve a la pestaña **"Logs"**
3. Verás errores en tiempo real

### 💡 Tip 5: Pausar/Reanudar app

Si no usas la app por un tiempo:
- Streamlit la "duerme" automáticamente
- Al abrir la URL se "despierta" sola
- Tarda ~10 segundos en cargar

---

## 📊 COMPARATIVA FINAL

| Aspecto | Desktop | Web App |
|---------|---------|---------|
| **Instalación** | Python + librerías | ✅ Solo navegador |
| **Acceso** | Una computadora | ✅ Cualquier lugar |
| **Compartir** | Enviar .exe | ✅ Enviar URL |
| **Actualizar** | Manual | ✅ Automático |
| **Móvil** | ❌ No | ✅ Sí |
| **Costo** | $0 | ✅ $0 |
| **Mantenimiento** | Alto | ✅ Mínimo |

---

## 🎉 ¡FELICITACIONES!

Has completado exitosamente la migración de tu aplicación de escritorio a una aplicación web moderna, accesible desde cualquier lugar del mundo.

### Próximos pasos

1. **Comparte** la URL con tu equipo
2. **Prueba** todas las funciones
3. **Reporta** cualquier problema
4. **Disfruta** de tu nueva app web

---

## 📞 AYUDA ADICIONAL

### Recursos útiles

- 📖 [Documentación Streamlit](https://docs.streamlit.io)
- 📖 [GitHub Guides](https://guides.github.com)
- 💬 [Streamlit Forum](https://discuss.streamlit.io)
- 🎥 [YouTube Tutorials](https://youtube.com/c/streamlit)

### Comunidad

- **Streamlit Discord**: https://discord.gg/streamlit
- **GitHub Discussions**: En tu repositorio

---

**🚀 Tu app está lista. ¡A producir!**

*Última actualización: Febrero 2026*
