import time
import shutil
import tempfile
from pathlib import Path
import subprocess
import socket
import os
import sys
from pywebio.input import actions #pip install pywebio
from pywebio.input import input as web_input
from pywebio.output import put_text
from pywebio import start_server
home = os.getcwd()
webui = False
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
        data = client.recv(8192)
        if webui:
            pass
        else:
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
    data = client.recv(8192)
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
        if os.name == "nt":
            time.sleep(0.3)
        shutil.rmtree(tmp, ignore_errors=True)

def screenshare():
    global cast, ffmpeg, tmp
    if system == "android":
        if webui:
            put_text("Open ScreenStream for screenshare")
        else:
            print("Open ScreenStream for screenshare")
        subprocess.run(["am", "start", "-n", "info.dvkr.screenstream/.SingleActivity"])
        if webui:
            actions(buttons=["Tap to start screenshare"])
        else:
            input("Press enter to start screenshare:")
        return "http://"+address+":1234/mjpeg"
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

def mediacast(filepath=None):
    global cast, tmp
    if system == "android":
        if filepath == None:
            if webui:
                put_text("Select video from explorer")
            else:
                print("Select video from explorer and press enter")
            tmp = os.path.join(tempfile.gettempdir(), "media")
            os.makedirs(tmp, exist_ok=True)
            os.chdir(tmp)
            subprocess.run(["termux-storage-get", "video.mp4"])
            if webui:
                actions(buttons=["Tap to continue"])
            else:
                input()
            file = "video.mp4"
        else:
            tmp = os.path.join(tempfile.gettempdir(), "media")
            os.makedirs(tmp, exist_ok=True)
            os.chdir(tmp)
            filepath = str(filepath).strip('"')
            shutil.copy2(filepath, "video.mp4")
            file = "video.mp4"
        cast = subprocess.Popen(["python3", "-m", "RangeHTTPServer", "1234"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        return "http://"+address+":1234/video.mp4"
    if system == "win32" or system == "linux":
        from file_picker_py import pick_file_blocking #pip install file-picker-py
        if filepath == None:
            if webui:
                actions(buttons=["Select file"])
                filepath = pick_file_blocking()
            else:
                filepath = str(input("Enter file path:")).strip('"')
        filepath = os.path.abspath(filepath).replace("\\", "/")
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

def streamcast(streamurl=None):
    if streamurl == None:
        if webui:
            stream = web_input("Enter stream link")
        else:
            stream = input("Enter stream link:")
        return stream
    else:
        return streamurl

address = netip()
index = address.rfind('.')
net = address[:index + 1]
if len(sys.argv) >= 3:
    autotime = False
    if "--time" in sys.argv:
        autotime = True
        wait = sys.argv.index("--time")
        wait = float(sys.argv[wait+1])
    mode = sys.argv[1]
    if mode == "1":
        connect(sys.argv[2], screenshare())
        if system == "linux":
            sys.stdin.flush()
        if autotime:
            time.sleep(wait)
        else:
            input("Press enter to disconnect")
        disconnect("screenshare")
    if mode == "2":
        connect(sys.argv[2], mediacast(sys.argv[3]))
        if system == "linux":
            sys.stdin.flush()
        if autotime:
            time.sleep(wait)
        else:
            input("Press enter to disconnect")
        disconnect("media")
    if mode == "3":
        connect(sys.argv[2], streamcast(sys.argv[3]))
        if system == "linux":
            sys.stdin.flush()
        if autotime:
            time.sleep(wait)
        else:
            input("Press enter to disconnect")
        disconnect("stream")
else:
    if "--web" in sys.argv:
        webui = True
        def web():
            ips.clear()
            receivers.clear()
            mode = actions("Select:", buttons=["Screenshare", "Media cast", "Stream cast"])
            put_text("Searching for a receiver")
            for ping in range(1, 255):
                ip = net + str(ping)
                search(ip, port)
            
            if not receivers:
                put_text("No receivers found")
                return
                
            if mode == "Screenshare":
                receiver = actions("Select TV", buttons=receivers)
                index = receivers.index(receiver)
                connect(ips[index], screenshare())
                if system == "linux":
                    sys.stdin.flush()
                actions(buttons=["Disconnect"])
                disconnect("screenshare")
                put_text("Exit")
            if mode == "Media cast":
                receiver = actions("Select TV", buttons=receivers)
                index = receivers.index(receiver)
                connect(ips[index], mediacast())
                if system == "linux":
                    sys.stdin.flush()
                actions(buttons=["Disconnect"])
                disconnect("media")
                put_text("Exit")
            if mode == "Stream cast":
                receiver = actions("Select TV", buttons=receivers)
                index = receivers.index(receiver)
                connect(ips[index], streamcast())
                if system == "linux":
                    sys.stdin.flush()
                actions(buttons=["Disconnect"])
                disconnect("stream")
                put_text("Exit")

        if system == "android":
            subprocess.Popen(["termux-open-url", "http://localhost:8080/"])
            start_server(web, port=8080, auto_open_webbrowser=False)
        else:
            start_server(web, port=8080, auto_open_webbrowser=True)
    else:
        print("Select:\n[1]use screenshare\n[2]use media cast\n[3]use stream cast")
        mode = str(input())
        print("Searching for a receiver")
        for ping in range(1,255):
            ip = net + str(ping)
            search(ip, port)
            
        if not receivers:
            print("No receivers found")
            sys.exit()
            
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
