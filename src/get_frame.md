# Notes about taking photos

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

RAM is about 5MB free, 640x480 images is < 0.5MB.

    kill `pidof dragon-prog`
    mkdir /data/ftp/ram
    mount -t tmpfs -o size=1m tmpfs /data/ftp/ram
    rm -f /data/ftp/ram/snap.jpg; yavta --skip=1 -n1 -c2 -F/data/ftp/ram/snap.jpg -fMJPEG /dev/video0 > /dev/null

Takes 0.34 seconds for 640x480 (default) and 0.31 seconds for 160x120.

## Timing

    [JS] $ rm -f /data/ftp/bob.jpg; time yavta --skip=1 -n1 -s640x480 -c2 -F/data/ftp/bob.jpg -fMJPEG /dev/video0 > /dev/null
    real    0m 0.34s
    user    0m 0.01s
    sys     0m 0.01s
    [JS] $ rm -f /data/ftp/bob.jpg; time yavta --skip=1 -n1 -s160x120 -c2 -F/data/ftp/bob.jpg -fMJPEG /dev/video0 > /dev/null
    real    0m 0.30s
    user    0m 0.01s
    sys     0m 0.01s
