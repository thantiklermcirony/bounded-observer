; IDA Live - Windows installer (NSIS 3). Built by packaging/build_windows.sh.
; Installs per user (no admin rights), bundles its own Python, adds shortcuts and an
; uninstaller. Your recordings live in Documents\IDA Live and are never removed.

Target amd64-unicode   ; 64-bit installer, matching the bundled 64-bit Python
!include "MUI2.nsh"
!include "FileFunc.nsh"

!ifndef VERSION
  !define VERSION "0.1.0"
!endif
!ifndef STAGE
  !define STAGE "stage"
!endif
!ifndef OUTFILE
  !define OUTFILE "IDA-Live-Setup-${VERSION}.exe"
!endif

Name "IDA Live"
OutFile "${OUTFILE}"
InstallDir "$LOCALAPPDATA\Programs\IDA Live"
RequestExecutionLevel user
SetCompressor /SOLID lzma
BrandingText "IDA Live ${VERSION}"
VIProductVersion "${VERSION}.0"
VIAddVersionKey "ProductName" "IDA Live"
VIAddVersionKey "FileDescription" "IDA Live installer"
VIAddVersionKey "FileVersion" "${VERSION}"
VIAddVersionKey "LegalCopyright" "Daniel John Murray, MIT licence"

!define MUI_ICON "${STAGE}\app\ida-live.ico"
!define MUI_UNICON "${STAGE}\app\ida-live.ico"
!define MUI_WELCOMEPAGE_TITLE "IDA Live ${VERSION}"
!define MUI_WELCOMEPAGE_TEXT "This installs IDA Live for your Windows account. It includes everything it needs, so nothing else has to be installed.$\r$\n$\r$\nYour recordings will be kept in Documents\IDA Live.$\r$\n$\r$\nIDA Live is a research tool, not a medical device."
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Open IDA Live now"
!define MUI_FINISHPAGE_RUN_FUNCTION LaunchApp

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\IDA Live"

; Ask a running copy to close itself so its files can be replaced.
!macro CloseRunningCopy
  nsExec::Exec 'powershell -NoProfile -NonInteractive -Command "try { Invoke-WebRequest -Uri http://127.0.0.1:8765/api/quit -Method Post -Headers @{\"X-IDA-Live\"=\"quit\"} -UseBasicParsing -TimeoutSec 3 | Out-Null } catch {}"'
  Pop $0
  Sleep 1500
!macroend

Function LaunchApp
  SetOutPath "$INSTDIR\app"
  Exec '"$INSTDIR\python\pythonw.exe" -m ida_live'
FunctionEnd

Section "IDA Live" SecMain
  !insertmacro CloseRunningCopy
  ; replace the program files completely so nothing stale from an older version remains
  RMDir /r "$INSTDIR\python"
  RMDir /r "$INSTDIR\app"
  SetOutPath "$INSTDIR"
  File /r "${STAGE}\*.*"

  SetOutPath "$INSTDIR\app"
  CreateShortCut "$DESKTOP\IDA Live.lnk" "$INSTDIR\python\pythonw.exe" "-m ida_live" "$INSTDIR\app\ida-live.ico" 0
  CreateDirectory "$SMPROGRAMS\IDA Live"
  CreateShortCut "$SMPROGRAMS\IDA Live\IDA Live.lnk" "$INSTDIR\python\pythonw.exe" "-m ida_live" "$INSTDIR\app\ida-live.ico" 0
  CreateShortCut "$SMPROGRAMS\IDA Live\IDA Live (simulated headband).lnk" "$INSTDIR\python\pythonw.exe" "-m ida_live --sim" "$INSTDIR\app\ida-live.ico" 0
  CreateShortCut "$SMPROGRAMS\IDA Live\IDA Live reports.lnk" "$INSTDIR\python\python.exe" "-m ida_live reports" "$INSTDIR\app\ida-live.ico" 0
  CreateDirectory "$DOCUMENTS\IDA Live"
  CreateShortCut "$SMPROGRAMS\IDA Live\My recordings.lnk" "$DOCUMENTS\IDA Live"
  CreateShortCut "$SMPROGRAMS\IDA Live\Uninstall IDA Live.lnk" "$INSTDIR\Uninstall.exe"

  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayName" "IDA Live"
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKCU "${UNINST_KEY}" "Publisher" "Daniel John Murray"
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayIcon" "$INSTDIR\app\ida-live.ico"
  WriteRegStr HKCU "${UNINST_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "${UNINST_KEY}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegDWORD HKCU "${UNINST_KEY}" "NoModify" 1
  WriteRegDWORD HKCU "${UNINST_KEY}" "NoRepair" 1
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  WriteRegDWORD HKCU "${UNINST_KEY}" "EstimatedSize" $0
SectionEnd

Section "Uninstall"
  !insertmacro CloseRunningCopy
  Delete "$DESKTOP\IDA Live.lnk"
  RMDir /r "$SMPROGRAMS\IDA Live"
  RMDir /r "$INSTDIR\python"
  RMDir /r "$INSTDIR\app"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  DeleteRegKey HKCU "${UNINST_KEY}"
  ; Documents\IDA Live (your recordings, references, recipes, settings) is left in place.
SectionEnd
