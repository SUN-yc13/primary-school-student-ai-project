; 学习效率助手 - Inno Setup 安装脚本
; 使用 Inno Setup 编译器编译此文件生成安装包

#define MyAppName "学习效率助手"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "StudyHelper"
#define MyAppExeName "学习效率助手.exe"

[Setup]
; 基本设置
AppId={{B2C3D4E5-F6A7-8901-BCDE-F12345678901}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; 安装包输出设置
OutputDir=installer
OutputBaseFilename=学习效率助手_Setup
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
Name: "autostart"; Description: "开机自动启动"; GroupDescription: "其他任务:"; Flags: unchecked

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
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "运行 {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时删除用户数据（可选，默认不删除）
; Type: filesandordirs; Name: "{userappdata}\.study_helper"
