# Guía: claves gratis para las voces de Azure y Google

Las dos capas gratis permiten **uso comercial**. Ambas piden una tarjeta solo para verificar identidad;
mientras no se pase del límite gratis, no cobran. Un reel usa ~400 caracteres, así que 16 reels al mes
quedan muy por debajo de los límites.

> **Seguridad:** las claves van directo al archivo `.env` (nunca en el chat, en correos ni en el código).
> El `.env` no se sube a GitHub.

---

## Opción 1 · Azure AI Speech (500 000 caracteres/mes gratis)

Voces candidatas: **es-GT-MartaNeural** (mujer, Guatemala), es-MX-DaliaNeural (México),
es-CO-SalomeNeural (Colombia), es-US-PalomaNeural (latina, EE. UU.).

1. Entrá a <https://azure.microsoft.com/free> y creá la cuenta gratuita (con el correo de la empresa).
2. En <https://portal.azure.com> hacé clic en **Crear un recurso**, buscá **Speech** (Servicios de voz / AI Speech) y dale **Crear**.
3. Completá:
   - **Grupo de recursos:** nuevo, `if-contenido`
   - **Región:** `East US`
   - **Nombre:** `if-voz` (o el que quieran)
   - **Plan de tarifa:** **Free F0** ← importante, es el gratis
4. **Revisar y crear** → **Crear**. Esperá a que termine y entrá al recurso.
5. En el menú del recurso abrí **Claves y punto de conexión**. Copiá **CLAVE 1** y la **Ubicación/Región** (por ejemplo `eastus`).
6. Abrí el archivo `.env` del proyecto y completá:
   ```
   AZURE_SPEECH_KEY=la_clave_que_copiaste
   AZURE_SPEECH_REGION=eastus
   ```

## Opción 2 · Google Cloud Text-to-Speech (1 000 000 caracteres/mes gratis en voces Chirp 3 HD)

Voces candidatas: **es-US-Chirp3-HD-Aoede**, -Kore, -Leda, -Zephyr (mujeres, español latino).

1. Entrá a <https://console.cloud.google.com> con la cuenta de Google de la empresa.
2. Arriba, en el selector de proyectos, creá uno nuevo: `if-contenido`.
3. Activá la facturación cuando lo pida (tarjeta para verificación).
4. **Recomendado:** en **Facturación → Presupuestos y alertas**, creá un presupuesto de **USD 1** con alerta por correo. Así se enteran si algo pasa del límite gratis.
5. Andá a **APIs y servicios → Biblioteca**, buscá **Cloud Text-to-Speech API** y dale **Habilitar**.
6. Andá a **APIs y servicios → Credenciales → Crear credenciales → Clave de API**.
7. Editá la clave nueva: en **Restricciones de API** elegí **Restringir clave** y marcá solo **Cloud Text-to-Speech API**. Guardá.
8. Copiá la clave y completá en `.env`:
   ```
   GOOGLE_TTS_API_KEY=la_clave_que_copiaste
   ```

---

## Probar las voces

Con una o las dos claves en `.env`, corré:

```bash
.venv/Scripts/python tools/probar_voces.py
```

Se generan los MP3 en `data/voz/comparacion/`: cada voz lee el guion del reel con la música de la campaña de fondo.
Los proveedores sin clave se saltan.

## Elegir la voz

En `config/settings.yaml`:

```yaml
engines:
  tts: azure        # o google
tts:
  azure:
    voice: es-GT-MartaNeural
  google:
    voice: es-US-Chirp3-HD-Aoede
```
