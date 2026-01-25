; Script Inno Setup pour "Aux petits oignons"
; Bot Traducteur - Deployment Container
; Version 1.4 - Fork OpenCode Custom (simplifié)

#define MyAppName "Aux petits oignons"
#define MyAppVersion "1.4"
#define MyAppPublisher "Be-Cloud"
#define MyAppURL "https://be-cloud.fr"
#define MyAppExeName "start.bat"
#define MyDataDir "{%USERPROFILE}\AuxPetitsOignons"

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
PrivilegesRequired=lowest

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Dirs]
; Creer le dossier de donnees a la racine de C:
Name: "{#MyDataDir}"; Permissions: users-full
Name: "{#MyDataDir}\clients"; Permissions: users-full
Name: "{#MyDataDir}\Solution"; Permissions: users-full
; src/ sera cree par git clone au premier demarrage

[Files]
; Fichiers du projet (dans Program Files) - PAS de src/ !
; Configuration OpenCode
Source: "..\conf_opencode\opencode.json"; DestDir: "{app}\conf_opencode"; Flags: ignoreversion
Source: "..\conf_opencode\.env.example"; DestDir: "{app}\conf_opencode"; Flags: ignoreversion
Source: "..\conf_opencode\CLAUDE.md"; DestDir: "{app}\conf_opencode"; Flags: ignoreversion

; Scripts
Source: "..\scripts\*"; DestDir: "{app}\scripts"; Flags: ignoreversion recursesubdirs createallsubdirs

; Dockerfile (Fork Aux-petits-Oignons)
Source: "..\Dockerfile"; DestDir: "{app}"; Flags: ignoreversion

; Docker config
Source: "..\docker-compose.yml"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\entrypoint.sh"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\doc_server.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\repo-config.txt"; DestDir: "{app}"; Flags: ignoreversion

; Scripts principaux
Source: "..\start.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\configure.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\rebuild-fast.bat"; DestDir: "{app}"; Flags: ignoreversion

; Scripts PowerShell
Source: "..\test-opencode.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\test-quick.bat"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "..\test-opencode-guide.md"; DestDir: "{app}"; Flags: ignoreversion

; Icône
Source: "..\icone\oignon.ico"; DestDir: "{app}"; Flags: ignoreversion

; Les dossiers clients/ et Solution/ seront crees par start.bat
; et remplis automatiquement par le container via les volumes Docker

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\oignon.ico"; WorkingDir: "{app}"
Name: "{group}\Documentation (Web)"; Filename: "http://localhost:5545/procedure"; IconFilename: "{app}\oignon.ico"
Name: "{group}\Build Docker"; Filename: "{app}\rebuild-fast.bat"; IconFilename: "{app}\oignon.ico"; WorkingDir: "{app}"
Name: "{group}\Test OpenCode"; Filename: "{app}\test-quick.bat"; IconFilename: "{app}\oignon.ico"; WorkingDir: "{app}"
Name: "{group}\Solution Power Platform"; Filename: "{#MyDataDir}\Solution"; IconFilename: "{app}\oignon.ico"
Name: "{group}\Rapports Clients"; Filename: "{#MyDataDir}\clients"; IconFilename: "{app}\oignon.ico"
Name: "{group}\Configuration"; Filename: "{app}\configure.bat"; IconFilename: "{app}\oignon.ico"; WorkingDir: "{app}"
Name: "{group}\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\oignon.ico"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Créer une icône sur le Bureau"; GroupDescription: "Icônes supplémentaires:"

[Run]
; Note: La configuration se fait maintenant depuis le menu Demarrer

[UninstallRun]
; Supprimer les exclusions Defender a la desinstallation
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -Command ""try {{ Remove-MpPreference -ExclusionPath '{app}', '$env:LOCALAPPDATA\Programs\AuxPetitsOignons', '{#MyDataDir}', '$env:USERPROFILE\AppData\AuxPetitsOignons', '$env:USERPROFILE\.opencode'; Remove-MpPreference -ExclusionProcess 'docker.exe', 'dockerd.exe', 'com.docker.backend.exe' }} catch {{}}"""; RunOnceId: "RemoveDefenderExclusions"; Flags: runhidden waituntilterminated

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

function IsGitInstalled(): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/c git --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := True;

  // Verifier Docker
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
    Exit;
  end;

  if not IsDockerRunning() then
  begin
    MsgBox('Docker Desktop est installé mais n''est pas démarré.' + #13#10 + #13#10 +
           'Veuillez démarrer Docker Desktop avant de continuer l''installation.',
           mbError, MB_OK);
    Result := False;
    Exit;
  end;

  // Verifier Git (avertissement seulement)
  if not IsGitInstalled() then
  begin
    if MsgBox('Git n''est pas installé sur votre système.' + #13#10 + #13#10 +
              'Git est recommandé pour les mises à jour automatiques du code source.' + #13#10 + #13#10 +
              'Voulez-vous ouvrir la page de téléchargement de Git ?' + #13#10 +
              '(Vous pouvez aussi continuer sans Git)',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://git-scm.com/download/win', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
      MsgBox('Après l''installation de Git, relancez cet installeur.' + #13#10 + #13#10 +
             'Ou cliquez OK pour continuer sans Git.',
             mbInformation, MB_OK);
    end;
    // On continue meme sans Git - le code source sera telecharge au premier demarrage
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Creer un fichier README dans le dossier de donnees
    SaveStringToFile(ExpandConstant('{#MyDataDir}\README.txt'),
      'Dossier de données "Aux Petits Oignons"' + #13#10 +
      '========================================' + #13#10 + #13#10 +
      'clients/   - Rapports de déploiement par client' + #13#10 +
      'Solution/  - Solutions Power Platform à importer' + #13#10 + #13#10 +
      'Application installée dans: ' + ExpandConstant('{app}') + #13#10 + #13#10 +
      'Le code source est intégré dans le container Docker.' + #13#10 +
      'Seules les données utilisateur sont stockées ici.' + #13#10,
      False);

    // Message informatif apres installation
    MsgBox('Installation terminée avec succès !' + #13#10 + #13#10 +
           'Prochaines étapes :' + #13#10 +
           '1. Lancez "Build Docker (Menu)" pour choisir votre option' + #13#10 +
           '   - Option 1-3 : OpenCode standard' + #13#10 +
           '   - Option 4 : Fork sécurisé (recommandé pour clients)' + #13#10 +
           '2. Configurez vos clés API Azure dans conf_opencode\.env' + #13#10 +
           '3. Lancez "Aux petits oignons" pour démarrer' + #13#10 + #13#10 +
           'Documentation :' + #13#10 +
           '- Guide Rapide Option 4 : Installation en 11 minutes' + #13#10 +
           '- Documentation Option 4 : Guide complet du fork custom' + #13#10 + #13#10 +
           'Tous les raccourcis sont disponibles dans le menu Démarrer.',
           mbInformation, MB_OK);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Demander si on doit supprimer le dossier de donnees
    if MsgBox('Voulez-vous supprimer le dossier de données ?' + #13#10 +
              ExpandConstant('{#MyDataDir}') + #13#10 + #13#10 +
              'Ce dossier contient les rapports clients, les solutions Power Platform' + #13#10 +
              'et le code source téléchargé.',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{#MyDataDir}'), True, True, True);
    end;
  end;
end;
