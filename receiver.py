import subprocess
import socket
import time
import sys
import os
system = ""
if os.name == "nt":
    system = "win32"
if os.name == "posix":
    if os.path.exists('/data/data/com.termux'):
        system = "android"
    else:
        system = "linux"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 1235))
server.listen()
hostname = ""
if len(sys.argv) == 2 or 2 < len(sys.argv):
    hostname = sys.argv[1]
else:
    hostname = socket.gethostname()
print("The receiver is ready to connect")
while True:
    user, adress = server.accept()
    data = user.recv(1024)
    if data.decode("utf-8") == "name":
        user.send(hostname.encode("utf-8"))
        user.close()
    if data.decode("utf-8") == "connect":

        user.send("connect".encode("utf-8"))
        data = user.recv(1024)
        url = data.decode("utf-8")
        if system == "android":
            time.sleep(0.3)
            subprocess.Popen(["am", "start", "-n" ,"org.videolan.vlc/.gui.video.VideoPlayerActivity", "-d", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            if system == "win32":
                time.sleep(1.5)
                vlc = subprocess.Popen(["C:/Program Files/VideoLAN/VLC/vlc.exe", url, "--fullscreen"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                time.sleep(1.5)
                vlc = subprocess.Popen(["vlc", url, "--fullscreen"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        while True:
            try:
                data = user.recv(1024)
                if data.decode("utf-8") == "disconnect":
                    if system == "android":
                        user.close()
                        break
                    if system == "linux":
                        vlc.kill()
                        user.close()
                        break
                    if system == "win32":
                        vlc.kill()
                        user.close()
                        break
            except:
                break
