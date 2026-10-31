; Inno Setup script for Twitch VOD Downloader.
; CI passes /DAppVersion=<version> from APP_VERSION in twitch_downloader.py.

#ifndef AppVersion
  #define AppVersion "1.1.0"
#endif

#define AppName "Twitch VOD Downloader"
#define AppPublisher "Pausiar"
#define AppURL "https://pausiar.github.io/TwitchDowloader/"
#define AppExeName "TwitchDownloader.exe"

[Setup]
AppId={{BF720425-F698-42E5-A26D-284A5094FD38}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}faq.html
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
MinVersion=10.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
CloseApplications=yes
OutputDir=..\dist
OutputBaseFilename=TwitchDownloaderSetup
SetupIconFile=..\assets\logo.ico
VersionInfoCompany={#AppPublisher}
VersionInfoDescription=Instalador de {#AppName}
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
Source: "..\dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent
