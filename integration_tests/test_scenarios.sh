#!/bin/bash

# Copy file and change ownership to metwork
# $1 = file to copy
# $2 = destination path (archive, zipped)
function own_n_copy() {
    cp -p $1 $2\.t
    chown mfdata:metwork $2\.t
    mv $2\.t $2
}

mkdir -p /integration_tests/moved /integration_tests/archived
chmod -R 777 /integration_tests/moved /integration_tests/archived
chown mfdata:metwork /integration_tests/images/image.png /integration_tests/images/image.jpeg

# Insert PNG and JPEG (will archive (and convert PNG to JPEG then move JPEG))
own_n_copy "/integration_tests/images/image.png" "/home/mfdata/var/in/incoming/archived.png"
own_n_copy "/integration_tests/images/image.jpeg" "/home/mfdata/var/in/incoming/archived.jpeg"

# Insert zipped image (will unzip then archive and convert + move)
own_n_copy "/integration_tests/images/image.png" "/integration_tests/images/zipped.png"
gzip /integration_tests/images/zipped.png
own_n_copy "/integration_tests/images/zipped.png.gz" "/home/mfdata/var/in/incoming/zipped.png.gz"
rm /integration_tests/images/zipped.png.gz

# Insert PNG (will convert to JPEG and move file (and archive PNG))
own_n_copy "/integration_tests/images/image.png" "/home/mfdata/var/in/incoming/converted_moved.png"

# Sleep to let the processing finish (otherwise files are not present for testing)
sleep 2
