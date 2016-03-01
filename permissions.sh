#!/bin/bash
set -u

ROOTDIR="/the/dir/with/upload_sievee"
READ_WRITE_DIRS="repo"

# Set everything to root/read-only by default
chown -v -R root:root $ROOTDIR
chmod -v -R 644 $ROOTDIR

# Set all the directory permissions
find $ROOTDIR -type d -exec chmod 755 {} \;

# Set permissions for writing
for i in $READ_WRITE_DIRS; do
        chown -v -R www-upload-cv:www-upload-cv $ROOTDIR/$i
        find $ROOTDIR/$i -type f -exec chmod -v 664 {} \;
        find $ROOTDIR/$i -type d -exec chmod -v 775 {} \;
done

