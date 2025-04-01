#!/bin/bash

# astroPhoto_stage2.bash

if [ $# != 1 ] ; then
    echo "bash astroPhoto_stage2.bash"
    echo "    \$1 : Flat rgb image"
    exit
else
    f_flat=$1
fi

PYTHON="python3"
d_script_home=$(cd $(dirname $0) && pwd)
tools_dir="${d_script_home}/scripts"
tool_mkflat="${tools_dir}/mkVignetRawImage.py"

f_flat_r=$(echo $f_flat | sed 's/\.tif/_r.tif/g')
f_flat_g=$(echo $f_flat | sed 's/\.tif/_g.tif/g')
f_flat_b=$(echo $f_flat | sed 's/\.tif/_b.tif/g')

echo "*** BEGIN :: Red Channel"
$PYTHON $tool_mkflat $f_flat --color r --output $f_flat_r
echo ""
echo "*** BEGIN :: Green Channel"
$PYTHON $tool_mkflat $f_flat --color g --output $f_flat_g
echo ""
echo "*** BEGIN :: Blue Channel"
$PYTHON $tool_mkflat $f_flat --color b --output $f_flat_b
