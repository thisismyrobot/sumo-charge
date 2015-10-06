# Notes about taking photos

## Some refs

 * http://www.ideasonboard.org/uvc/faq/
 * http://www.compulab.co.il/workspace/mediawiki/index.php5/CM-T3730:\_Linux:\_Camera

## Shell

Is "ash" as part of BusyBox v1.20.2.

## Commands

### Current

Kill main process:

    kill `pidof dragon-prog`

Capture and return image as base64-encoded data.

    echo '' > /dev/stdout
    yavta --skip=1 -s160x120 -c2 -F/dev/stdout -fMJPEG /dev/video0 > /dev/null
    base64 /dev/stdout

### Options

#### Ram disk

RAM is about 5MB free, 640x480 images is < 0.5MB.

    kill `pidof dragon-prog`
    mkdir /data/ftp/ram
    mount -t tmpfs -o size=1m tmpfs /data/ftp/ram
    rm -f /data/ftp/ram/snap.jpg; yavta --skip=1 -n1 -c2 -F/data/ftp/ram/snap.jpg -fMJPEG /dev/video0 > /dev/null

Takes 0.34 seconds for 640x480 (default) and 0.31 seconds for 160x120.

#### Pausing dragon-prog?

It's ugly-as-heck to kill the dragon-prog process. Would be really nice to
either share the camera or at least restart it afterwards.

    kill -l

    kill -SIGTSTP `pidof dragon-prog`
    kill -SIGSTOP `pidof dragon-prog`
    kill -SIGCONT `pidof dragon-prog`

This is one way to remove the camera temporarily - may crash dragon-prog
though?!?!

    kill -SIGSTOP `pidof dragon-prog`
    sudo rmmod -f uvcvideo
    sudo modprobe uvcvideo
    # Do stuff
    kill -SIGCONT `pidof dragon-prog`

Also this should show what is using the camera.

    fuser /dev/video0

Maybe can request parallel access via:


    http://www.linuxtv.org/downloads/legacy/video4linux/API/V4L2_API/spec/ch01s03.html
    http://www.linuxtv.org/downloads/legacy/video4linux/API/V4L2_API/spec/rn01re48.html

    ioctl VIDIOC_G_PRIORITY

### Fixing partial images

Apparently if I reduce the exposure (disable auto) I can get faster frames?!?

Might be nice to have it "fixed" anyway.

This may help with the speed of capture and the incomplete frames sent to the
socket server in get_frame.py.

Also, apparently "autosuspend" for USB can cause corrupt images...

Should be able to stop via:

    echo -1 > /sys/module/usbcore/parameters/autosuspend

## Timing

    [JS] $ rm -f /data/ftp/bob.jpg; time yavta --skip=1 -n1 -s640x480 -c2 -F/data/ftp/bob.jpg -fMJPEG /dev/video0 > /dev/null
    real    0m 0.34s
    user    0m 0.01s
    sys     0m 0.01s
    [JS] $ rm -f /data/ftp/bob.jpg; time yavta --skip=1 -n1 -s160x120 -c2 -F/data/ftp/bob.jpg -fMJPEG /dev/video0 > /dev/null
    real    0m 0.30s
    user    0m 0.01s
    sys     0m 0.01s
