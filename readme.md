## Install on raspberry
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install opencv-python
pip install websockets
```


## auto startup 

edit `/etc/rc.local`

**change server or client accordingly**

```bash
sudo -H -u pi -s -- bash "/home/pi/Desktop/pyvideosync/start_server.sh" &

exit 0

```