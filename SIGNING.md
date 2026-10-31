# Firma del ejecutable y del instalador

Estado actual: **pendiente**. Sin las credenciales de SignPath configuradas, el flujo
[`.github/workflows/windows-release.yml`](.github/workflows/windows-release.yml) compila y publica
`TwitchDownloader.exe` y `TwitchDownloaderSetup.exe` sin firmar y lo indica en las notas de la
release. No se anuncia una firma que todavía no existe.

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

## Activación

1. Solicitar acceso a SignPath Foundation y esperar la aprobación.
2. En SignPath, crear el proyecto y subir dos configuraciones de artefacto: la del portable y la
   del instalador. La raíz de ambas es `<zip-file>` porque `actions/upload-artifact` comprime cada
   fichero en un ZIP. Crear también la política de firma de release.
3. Anotar el identificador de organización y los slugs de proyecto, política y ambas
   configuraciones.
4. Configurar en GitHub:

| Nombre | Tipo | Valor |
| --- | --- | --- |
| `SIGNPATH_API_TOKEN` | Secret | Token de API de SignPath |
| `SIGNPATH_ORGANIZATION_ID` | Variable | ID de la organización |
| `SIGNPATH_PROJECT_SLUG` | Variable | Slug del proyecto |
| `SIGNPATH_SIGNING_POLICY_SLUG` | Variable | Slug de la política de firma |
| `SIGNPATH_ARTIFACT_CONFIGURATION_SLUG` | Variable | Slug de la configuración del portable |
| `SIGNPATH_INSTALLER_ARTIFACT_CONFIGURATION_SLUG` | Variable | Slug de la configuración del instalador |

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
