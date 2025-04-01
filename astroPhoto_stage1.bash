#!/bin/bash

# astroPhoto_stage1.bash

if [ $# != 4 ] ; then
    echo "bash astroPhoto_stage1.bash"
    echo "    \$1 : Light frame dir"
    echo "    \$2 : Dark frame of the light frame dir"
    echo "    \$3 : Flat frame dir"
    echo "    \$4 : Dark frame of the flat frame dir"
    exit
else
    d_light=$1
    d_dark_of_light=$2
    d_flat=$3
    d_dark_of_flat=$4
fi

PYTHON="python3"
d_script_home=$(cd $(dirname $0) && pwd)
tools_dir="${d_script_home}/scripts"
tool_composite_smpl="${tools_dir}/composite_simple.py"
tool_subtract="subtract.py"

f_dark_of_light="drk_light_16bit.tif"
f_dark_of_flat="drk_flat_16bit.tif"
f_flat="flat_16bit.tif"
d_light_subtract="./l_drk_subt"
d_flat_subtract="./f_drk_subt"

### Check files
if [ -e $f_dark_of_light ] ; then
    rm -f $f_dark_of_light
fi
if [ -e $f_dark_of_flat ] ; then
    rm -f $f_dark_of_flat
fi
if [ -e $f_flat ] ; then
    rm -f $f_flat
fi
### Check directories
if [ ! -e $d_light_subtract ] ; then
    mkdir $d_light_subtract
fi
if [ ! -e $d_flat_subtract ] ; then
    mkdir $d_flat_subtract
fi

### Composite the dark frame of flat frames
status=0
if [ "$d_dark_of_flat" != "NONE" ] ; then
    $PYTHON $tool_composite_smpl $d_dark_of_flat -o $f_dark_of_flat -m mean
    status=$?
fi
if [ "$status" != 0 ] ; then
    echo "abort."
    exit
fi

### Composite the dark frame of light frames
status=0
if [ "$d_dark_of_light" != "NONE" ] ; then
    $PYTHON $tool_composite_smpl $d_dark_of_light -o $f_dark_of_light -m mean
    status=$?
fi
if [ "$status" != 0 ] ; then
    echo "abort."
    exit
fi

### Composite the flat frames
status=0
if [ "$d_flat" != "NONE" ] ; then
    $PYTHON $tool_composite_smpl $d_flat -o $f_flat -m mean
    status=$?
fi
if [ "$status" != 0 ] ; then
    echo "abort."
    exit
fi

### Subtract the dark frame from flat frames
status=0
if [ "$d_dark_of_light" != "NONE" ] ; then
    $PYTHON $tool_subtract $d_flat $f_dark_of_flat $d_flat_subtract
    status=$?
fi
if [ "$status" != 0 ] ; then
    echo "abort."
    exit
fi

### Subtract the dark frame from light frames
status=0
if [ "$d_dark_of_light" != "NONE" ] ; then
    $PYTHON $tool_subtract $d_light $f_dark_of_light $d_light_subtract
    status=$?
fi
if [ "$status" != 0 ] ; then
    echo "abort."
    exit
fi
