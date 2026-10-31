# Firma del ejecutable y del instalador

Estado actual: **pendiente de aprobación de SignPath Foundation**. Sin las credenciales de
SignPath, el flujo [`.github/workflows/windows-release.yml`](.github/workflows/windows-release.yml)
compila y publica `TwitchDownloader.exe` y `TwitchDownloaderSetup.exe` sin firmar y lo indica en
las notas de la release. No se anuncia una firma que todavía no existe.

## Por qué SignPath Foundation

SignPath Foundation firma software open source de forma gratuita y verifica que el binario se
compila desde el repositorio público. La solicitud se presenta en <https://signpath.org/apply> y
requiere aprobación; no hay plazo garantizado. El proyecto ya cumple el requisito de licencia con
[`LICENSE`](LICENSE) (MIT).

La firma identifica al editor y evita el aviso de editor desconocido cuando Windows confía en la
cadena de certificados. **No elimina por sí sola las advertencias de SmartScreen**: la reputación
se acumula con descargas y análisis, así que las primeras versiones firmadas pueden seguir
mostrando el aviso.

## Qué hace el flujo de release

1. Compila el EXE con PyInstaller y el recurso de versión de [`version_info.txt`](version_info.txt).
2. Sube el binario como artefacto temporal.
3. Si existe `SIGNPATH_API_TOKEN`, firma el portable con
   [`signpath/artifact-configuration.xml`](signpath/artifact-configuration.xml).
4. Sustituye el portable por el firmado y comprueba `Get-AuthenticodeSignature` (debe ser `Valid`).
5. Genera el instalador con Inno Setup a partir del portable ya firmado, usando
   [`installer/TwitchDownloader.iss`](installer/TwitchDownloader.iss).
6. Sube el instalador como artefacto y lo firma con
   [`signpath/artifact-configuration-installer.xml`](signpath/artifact-configuration-installer.xml).
7. Sustituye el instalador por el firmado y vuelve a comprobar la firma. Si cualquiera de las dos
   firmas falla, el flujo falla y no se publica la release.
8. Genera `SHA256SUMS.txt` con ambos binarios y los publica en la release.

El instalador empaqueta el portable firmado, así que el EXE conserva su firma tras instalarlo.
Sin token, los pasos de firma se omiten y el flujo sigue funcionando en modo sin firmar.

## Solicitud a SignPath Foundation

La cuenta, la organización y el token solo los puede crear el titular del proyecto. Mientras
Foundation no apruebe la solicitud, las releases seguirán saliendo sin firmar.

Datos para el formulario de <https://signpath.org/apply>:

- Proyecto: Twitch VOD Downloader
- Repositorio: <https://github.com/Pausiar/TwitchDowloader>
- Licencia: MIT
- Tecnología: Python, PyInstaller e Inno Setup
- Build: GitHub Actions, `.github/workflows/windows-release.yml`, tags `v*`
- Artefactos: `TwitchDownloader.exe` y `TwitchDownloaderSetup.exe`
- Web: <https://pausiar.github.io/TwitchDowloader/>
- Descargas: <https://github.com/Pausiar/TwitchDowloader/releases>
- Mantenedor: Pausiar

Texto propuesto (en inglés):

> Twitch VOD Downloader is a free, open-source Windows application (MIT) for downloading Twitch
> VODs and clips. It is distributed as a portable PyInstaller executable and an Inno Setup
> installer, both built from tagged releases in public GitHub Actions. The app has no telemetry,
> no accounts and no bundled third-party binaries; yt-dlp is installed as a Python dependency at
> build time. We request code signing to protect users from tampered downloads and to establish
> the publisher identity of the releases.

## Activación tras la aprobación

1. En SignPath, crear el proyecto y subir las dos configuraciones de artefacto. La raíz de ambas es
   `<zip-file>` porque `actions/upload-artifact` comprime cada fichero en un ZIP. Crear también la
   política de firma de release.
2. Anotar el identificador de organización y los slugs de proyecto, política y ambas
   configuraciones.
3. Configurar GitHub desde la raíz del repositorio. El token se pega en el prompt, no en el
   historial:

```bash
gh secret set SIGNPATH_API_TOKEN
gh variable set SIGNPATH_ORGANIZATION_ID --body "<organization-id>"
gh variable set SIGNPATH_PROJECT_SLUG --body "<project-slug>"
gh variable set SIGNPATH_SIGNING_POLICY_SLUG --body "<signing-policy-slug>"
gh variable set SIGNPATH_ARTIFACT_CONFIGURATION_SLUG --body "<portable-config-slug>"
gh variable set SIGNPATH_INSTALLER_ARTIFACT_CONFIGURATION_SLUG --body "<installer-config-slug>"
```

4. Probar el flujo sin publicar release:

```bash
gh workflow run windows-release.yml --ref main
gh run watch
```

Los pasos `Sign EXE with SignPath` y `Sign installer with SignPath` deben ejecutarse, y
`Get-AuthenticodeSignature` debe devolver `Valid` para ambos binarios. Si el token existe pero
falta alguna variable, el flujo falla antes de compilar y dice cuáles faltan.

5. Publicar un tag `vX.Y.Z`. Al cambiar `APP_VERSION` en `twitch_downloader.py`, actualizar también
   las cuatro cifras de `version_info.txt`. El número de versión del instalador se toma de
   `APP_VERSION` en tiempo de compilación.

## Verificación manual

```powershell
Get-AuthenticodeSignature .\TwitchDownloader.exe | Format-List Status, SignerCertificate
Get-AuthenticodeSignature .\TwitchDownloaderSetup.exe | Format-List Status, SignerCertificate
Get-FileHash .\TwitchDownloader.exe, .\TwitchDownloaderSetup.exe -Algorithm SHA256
```

Los hashes deben coincidir con `SHA256SUMS.txt` de la release. Si `Status` no es `Valid`, no
ejecutes el binario y abre una incidencia en el repositorio.
