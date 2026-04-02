' Brasil Fut - Launcher Silencioso
' Execute este arquivo para abrir o jogo sem mostrar a janela do CMD

Dim shell, fso, gameDir, pythonPath, edgePath, chromePath, gameFile

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Pasta do jogo
gameDir = fso.GetParentFolderName(WScript.ScriptFullName)
gameFile = gameDir & "\brasil-fut.html"
launcher = gameDir & "\launcher.pyw"

' Tenta Python (janela oculta = 0, sem focar = false)
On Error Resume Next

' Verifica Python
shell.Run "cmd /c where python >nul 2>&1", 0, True
If Err.Number = 0 Then
    If shell.ExitCode = 0 Then
        shell.Run "pythonw """ & launcher & """", 0, False
        WScript.Quit
    End If
End If
Err.Clear

' Verifica Edge
edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
If Not fso.FileExists(edgePath) Then
    edgePath = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
End If
If fso.FileExists(edgePath) Then
    gameURL = Replace(gameFile, "\", "/")
    shell.Run """" & edgePath & """ --app=""file:///" & gameURL & """ --window-size=1400,900 --no-first-run --user-data-dir=""" & shell.ExpandEnvironmentStrings("%USERPROFILE%") & "\.brasilfut_edge""", 0, False
    WScript.Quit
End If

' Verifica Chrome
chromePath = shell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Google\Chrome\Application\chrome.exe"
If Not fso.FileExists(chromePath) Then
    chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
End If
If fso.FileExists(chromePath) Then
    gameURL = Replace(gameFile, "\", "/")
    shell.Run """" & chromePath & """ --app=""file:///" & gameURL & """ --window-size=1400,900 --no-first-run --user-data-dir=""" & shell.ExpandEnvironmentStrings("%USERPROFILE%") & "\.brasilfut_chrome""", 0, False
    WScript.Quit
End If

' Fallback: abre no navegador padrão
shell.Run """" & gameFile & """", 1, False
