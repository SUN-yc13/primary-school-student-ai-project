; 桌面文件智能管理助手 - Inno Setup 安装脚本
; 使用 Inno Setup 编译器编译此文件生成安装包

#define MyAppName "桌面文件智能管理助手"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "FileManager"
#define MyAppExeName "桌面文件智能管理助手.exe"

[Setup]
; 基本设置
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; 安装包输出设置
OutputDir=installer
OutputBaseFilename=桌面文件智能管理助手_Setup
SetupIconFile=NONE
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; 安装界面设置
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
; 支持的系统
MinVersion=10.0.14393
; 安装包样式
WizardStyle=modern
WizardImageStretch=no
; 卸载程序
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallFilesDir={app}\uninstall

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "创建快速启动图标"; GroupDescription: "附加图标:"; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "associate"; Description: "关联文件类型"; GroupDescription: "其他任务:"; Flags: unchecked

[Files]
; 主程序
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; 可选：添加其他文件
; Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "运行 {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时删除用户数据（可选）
; Type: filesandordirs; Name: "{app}\data"
