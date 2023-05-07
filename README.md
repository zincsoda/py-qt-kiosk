To run on Raspbian Py.

1. Install PyQT

```
sudo apt-get install python3-pyqt5
```

2. Make script executable

```
chmod +x clock.py
```

3. Add script to LXDE autostart file

```
nano ~/.config/lxsession/LXDE-pi/autostart
```

Add call to your script:

```
<path_to>/clock.py
```

Recommend adding following lines also if not already there

```
## enable/disable screen saver
#@xscreensaver -no-splash  # comment this line out to disable screensaver

# Set the current xsession not to blank out the screensaver and then disables the screensaver altogether.
@xset s noblank
@xset s off
# disables the display power management system
@xset -dpms
```
