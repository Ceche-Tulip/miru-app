; Miru（fork 版）Windows 安装器
; 编译：D:\Tools\InnoSetup\ISCC.exe installer\miru.iss
; 产物：client\dist\miru-setup-<版本>.exe

#define MyAppName "Miru"
#define MyAppVersion "1.8.1-rune.1"
#define MyAppExeName "miru.exe"
#define MyAppPublisher "Ceche-Tulip"
#define MyAppURL "https://github.com/Ceche-Tulip/miru-app"
#define MySource "..\..\dist\miru-1.8.1-rune-win64-r2"

[Setup]
; AppId 一经发布不可更改，否则新版本会被当成另一个程序
AppId={{0467439D-A8B4-484B-B2DA-4B41143FB013}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; 默认按当前用户安装（不弹 UAC）；用户可在安装方式对话框里选择"为所有用户安装"
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\..\dist
OutputBaseFilename=miru-setup-{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
DisableWelcomePage=no

[Languages]
Name: "chinesesimplified"; MessagesFile: "ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "{#MySource}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 只删程序目录；用户数据在 %USERPROFILE%\Documents\miru，不动
Type: filesandordirs; Name: "{app}"
