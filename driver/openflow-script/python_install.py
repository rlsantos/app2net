import os
def install():
    url = "https://www.python.org/ftp/python/3.8.6/Python-3.8.6.tar.xz"
    os.system("sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev && cd /tmp && sudo wget "+url+" && sudo tar -xf Python-3.8.6.tar.xz && cd Python-3.8.6 && sudo ./configure --enable-optimizations && sudo make && sudo make altinstall")

