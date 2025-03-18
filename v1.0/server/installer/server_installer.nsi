# NSIS Script for Server Installer
Outfile "ServerInstaller.exe"
InstallDir "$PROGRAMFILES\DistributedImageServer"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "Install"
  SetOutPath "$INSTDIR"
  File "server.exe"
  File "ReadMe.txt"
  
  # Optional: Add shortcut
  CreateShortcut "$DESKTOP\Distributed Image Server.lnk" "$INSTDIR\server.exe"
  
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\server.exe"
  Delete "$INSTDIR\ReadMe.txt"
  Delete "$DESKTOP\Distributed Image Server.lnk"
  RMDir "$INSTDIR"
SectionEnd
