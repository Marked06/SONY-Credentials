[Setup]
AppName=SONY Credentials Generator
AppVersion=1.0.0
AppPublisher=Special Olympics New York
AppPublisherURL=https://www.specialolympicsny.org
AppSupportURL=https://www.specialolympicsny.org
AppUpdatesURL=https://www.specialolympicsny.org
DefaultDirName={autopf}\SONY Credentials Generator
DefaultGroupName=SONY Credentials Generator
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README.md
OutputBaseFilename=SONYCredentialGeneratorSetup
OutputDir=dist\
Compression=lz4
SolidCompression=yes
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\SONY_Credentials.exe
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
RestartIfNeededByRun=no
ShowLanguageDialog=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "dist\SONY_Credentials.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "templates\Credential_Template.xlsx"; DestDir: "{app}\templates"; Flags: ignoreversion
Source: "templates\index.html"; DestDir: "{app}\templates"; Flags: ignoreversion
Source: "branding\*"; DestDir: "{app}\branding"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "Volunteers_Placeholder.xlsx"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SONY Credentials Generator"; Filename: "{app}\SONY_Credentials.exe"; Comment: "Generate credential PDFs for Special Olympics events"
Name: "{group}\{cm:UninstallProgram,SONY Credentials Generator}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\SONY Credentials Generator"; Filename: "{app}\SONY_Credentials.exe"; Tasks: desktopicon; Comment: "Generate credential PDFs for Special Olympics events"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\SONY Credentials Generator"; Filename: "{app}\SONY_Credentials.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\SONY_Credentials.exe"; Description: "{cm:LaunchProgram,SONY Credentials Generator}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: dirifempty; Name: "{app}\templates"
Type: dirifempty; Name: "{app}\branding"
Type: dirifempty; Name: "{app}"

[Code]
procedure InitializeWizard;
begin
  { Optional: Customize the installer appearance }
  WizardForm.MainPanel.Color := clWhite;
end;

function InitializeSetup(): Boolean;
begin
  { Optional: Check system requirements }
  Result := True;
end;
