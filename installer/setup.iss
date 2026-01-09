; Script Inno Setup pour "Aux petits oignons"
; Bot Traducteur - Deployment Container

#define MyAppName "Aux petits oignons"
#define MyAppVersion "1.0"
#define MyAppPublisher "Be-Cloud"
#define MyAppURL "https://be-cloud.fr"
#define MyAppExeName "start.bat"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\AuxPetitsOignons
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=output
OutputBaseFilename=AuxPetitsOignons_Setup
SetupIconFile=..\icone\oignon.ico
UninstallDisplayIcon={app}\oignon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Files]
; Fichiers du projet
Source: "..\src\*"; DestDir: "{app}\src"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\clients\*"; DestDir: "{app}\clients"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "..\Solution\*"; DestDir: "{app}\Solution"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\conf_opencode\*"; DestDir: "{app}\conf_opencode"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\Dockerfile"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docker-compose.yml"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\doc_server.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\start.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\icone\oignon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\oignon.ico"; WorkingDir: "{app}"
Name: "{group}\Documentation (Web)"; Filename: "http://localhost:5545/procedure"; IconFilename: "{app}\oignon.ico"
Name: "{group}\Solution Power Platform"; Filename: "{app}\Solution"; IconFilename: "{app}\oignon.ico"
Name: "{group}\Rapports Clients"; Filename: "{app}\clients"; IconFilename: "{app}\oignon.ico"
Name: "{group}\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\oignon.ico"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Créer une icône sur le Bureau"; GroupDescription: "Icônes supplémentaires:"

[Run]
; Build l'image Docker après installation
Filename: "cmd.exe"; Parameters: "/c cd /d ""{app}"" && docker-compose build"; StatusMsg: "Construction de l'image Docker (cela peut prendre plusieurs minutes)..."; Flags: runhidden waituntilterminated
; Proposer de lancer l'application
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer {#MyAppName}"; Flags: postinstall nowait skipifsilent shellexec

[Code]
function IsDockerInstalled(): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/c docker --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

function IsDockerRunning(): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/c docker info', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := True;

  if not IsDockerInstalled() then
  begin
    if MsgBox('Docker Desktop n''est pas installé sur votre système.' + #13#10 + #13#10 +
              'Docker est nécessaire pour faire fonctionner "Aux petits oignons".' + #13#10 + #13#10 +
              'Voulez-vous ouvrir la page de téléchargement de Docker Desktop ?',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://www.docker.com/products/docker-desktop/', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
      MsgBox('Veuillez installer Docker Desktop, puis relancez cet installeur.' + #13#10 + #13#10 +
             'IMPORTANT: Après l''installation de Docker, redémarrez votre ordinateur.',
             mbInformation, MB_OK);
      Result := False;
    end
    else
    begin
      MsgBox('L''installation ne peut pas continuer sans Docker Desktop.', mbError, MB_OK);
      Result := False;
    end;
  end
  else if not IsDockerRunning() then
  begin
    MsgBox('Docker Desktop est installé mais n''est pas démarré.' + #13#10 + #13#10 +
           'Veuillez démarrer Docker Desktop avant de continuer l''installation.',
           mbError, MB_OK);
    Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Créer les dossiers s'ils n'existent pas
    ForceDirectories(ExpandConstant('{app}\clients'));
    ForceDirectories(ExpandConstant('{app}\Solution'));
  end;
end;
