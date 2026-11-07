import shutil
import tempfile
from pathlib import Path
import subprocess
import socket
import os
import sys
home = os.getcwd()
cast = None
ffmpeg = None
tmp = None
ips = []
receivers = []
system = ""
port = 1235
if os.name == "nt":
    system = "win32"
if os.name == "posix":
    if os.path.exists('/data/data/com.termux'):
        system = "android"
    else:
        system = "linux"
        
def netip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        localip = s.getsockname()[0]
    except:
        localip = '127.0.0.1'
    finally:
        s.close()
    return localip

def search(ip, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(0.2)
    try:
        client.connect((ip, port))
        client.send(b'name')
        data = client.recv(1024)
        print(data.decode("utf-8"))
        ips.append(ip)
        receivers.append(data.decode("utf-8"))
    except:
        client.close()
        
def connect(ip, url):
    global cast, ffmpeg, tmp, client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))
    client.send(b'connect')
    data = client.recv(1024)
    print(data.decode("utf-8"))
    client.send(url.encode("utf-8"))

            
def disconnect(mode):
    global cast, ffmpeg, tmp, client
    client.send(b"disconnect")
    if mode == "screenshare":
        try:
            cast.kill()
            ffmpeg.kill()
        except:
            pass
    if mode == "stream":
        pass
    if mode == "media":
        cast.kill()
    if tmp != None:
        os.chdir(home)
        import time
        if os.name == "nt":
            time.sleep(0.3)
        shutil.rmtree(tmp, ignore_errors=True)
        
def screenshare():
    global cast, ffmpeg, tmp
    if system == "android":
        print("Open ScreenSream for screenshare")
        subprocess.run(["am", "start", "-n", "info.dvkr.screenstream/.SingleActivity"])
        input("Press enter to start screenshare:")
        return "http://"+address+":1234/stream.mjpeg"
    if system == "win32":
        tmp = os.path.join(tempfile.gettempdir(), "media")
        os.makedirs(tmp, exist_ok=True)
        ffmpeg = subprocess.Popen(["ffmpeg", "-f", "gdigrab", "-framerate", "30", "-i", "desktop", "-an", "-vcodec", "libx264", "-preset","ultrafast", "-tune", "zerolatency", "-crf", "28", "-g", "15", "-f", "hls", "-hls_time", "1", "-hls_list_size", "3", "-hls_flags", "delete_segments", "stream.m3u8"], cwd=tmp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chdir(tmp)
        cast = subprocess.Popen([
            "python", "-c", 
            "import socketserver; from RangeHTTPServer import RangeRequestHandler; "
            "ThreadedServer = type('ThreadedServer', (socketserver.ThreadingMixIn, socketserver.TCPServer), {'allow_reuse_address': True}); "
            "ThreadedServer(('0.0.0.0', 1234), RangeRequestHandler).serve_forever()"
        ], cwd=tmp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

        return "http://"+address+":1234/stream.m3u8"
    if system == "linux":
        tmp = os.path.join(tempfile.gettempdir(), "media")
        os.makedirs(tmp, exist_ok=True)
        display = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if "wayland" in display or "WAYLAND_DISPLAY" in os.environ:
            ffmpeg = subprocess.Popen(["ffmpeg", "-f", "libpipewire", "-i", "default", "-an", "-vcodec", "libx264", "-preset","ultrafast", "-tune", "zerolatency", "-crf", "28", "-g", "15", "-f", "hls", "-hls_time", "1", "-hls_list_size", "3", "-hls_flags", "delete_segments", str(tmp+"/stream.m3u8")], stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        if "x11" in display:
            ffmpeg = subprocess.Popen(["ffmpeg", "-f", "x11grab", "-i", ":0.0", "-an", "-vcodec", "libx264", "-preset","ultrafast", "-tune", "zerolatency", "-crf", "28", "-g", "15", "-f", "hls", "-hls_time", "1", "-hls_list_size", "3", "-hls_flags", "delete_segments", str(tmp+"/stream.m3u8")], stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        os.chdir(tmp)
        cast = subprocess.Popen(["python3", "-m", "RangeHTTPServer", "1234"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        return "http://"+address+":1234/stream.m3u8"

def mediacast():
    global cast, tmp
    if system == "android":
        print("Select video from explorer and press enter")
        tmp = os.path.join(tempfile.gettempdir(), "media")
        os.makedirs(tmp, exist_ok=True)
        os.chdir(tmp)
        subprocess.run(["termux-storage-get", "video.mp4"])
        input()
        file = "video.mp4"
        cast = subprocess.Popen(["python3", "-m", "RangeHTTPServer", "1234"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        return "http://"+address+":1234/video.mp4"
    if system == "win32" or system == "linux":
        filepath = str(input("Enter file path:")).strip('"')
        filepath = filepath.replace("\\", "/")
        index = filepath.rfind("/")
        filedir = filepath[:index]
        file = filepath[index + 1:]
        os.chdir(filedir)
        if system == "linux":
            cast = subprocess.Popen(["python3", "-m", "RangeHTTPServer", "1234"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        if system == "win32":
            cast = subprocess.Popen([
            "python", "-c", 
            "import socketserver; from RangeHTTPServer import RangeRequestHandler; "
            "ThreadedServer = type('ThreadedServer', (socketserver.ThreadingMixIn, socketserver.TCPServer), {'allow_reuse_address': True}); "
            "ThreadedServer(('0.0.0.0', 1234), RangeRequestHandler).serve_forever()"
        ], cwd=filedir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

        url = "" 
        for char in file:
            if char == " ":
                url += "%20"
            else:
                url += char
        return "http://"+address+":1234/"+url

def streamcast():
    stream = input("Enter stream link:")
    return stream

address = netip()
index = address.rfind('.')
print("Select:\n[1]use screen share\n[2]use media cast\n[3]use stream cast")
mode = str(input())
net = address[:index + 1]
for ping in range(1,255):
    ip = net + str(ping)
    search(ip, port)
if mode == "1":
    receiver = input("Enter TV:")
    index = receivers.index(receiver)
    connect(ips[index], screenshare())
    if system == "linux":
        sys.stdin.flush()
    input("Press enter to disconnect")
    disconnect("screenshare")
if mode == "2":
    receiver = input("Enter TV:")
    index = receivers.index(receiver)
    connect(ips[index], mediacast())
    if system == "linux":
        sys.stdin.flush()
    input("Press enter to disconnect")
    disconnect("media")
if mode == "3":
    receiver = input("Enter TV:")
    index = receivers.index(receiver)
    connect(ips[index], streamcast())
    if system == "linux":
        sys.stdin.flush()
    input("Press enter to disconnect")
    disconnect("stream")

