#!/bin/bash

# delete_exif

if [ $# != 2 ] ; then
    echo "Usage : bash delete_exif.bash indir outdir"
    exit
else
    indir=$1
    outdir=$2
fi

### Check directories
if [ ! -e "$indir" ] ; then
    echo "$indir does not exist!"
    echo "abort."
    exit
fi
if [ ! -e "$outdir" ] ; then
    mkdir $outdir
fi

### Set directories
fullpath_indir=$(cd $indir && pwd)
fullpath_outdir=$(cd $outdir && pwd)
d_org=$(pwd)

cd $outdir

for file in $(ls -1 $fullpath_indir) ; do
    
    cp $fullpath_indir/$file .
    exiftool -Orientation= -n $file
    status=$?
    echo "status = $status"
    echo ""

done

rm -f *original*
cd $d_org
