#!/bin/bash

# astroPhoto_stage3.bash

if [ $# != 4 ] ; then
    echo "bash astroPhoto_stage3.bash"
    echo "    \$1 : Light frame dir"
    echo "    \$2 : Flat frame of red channel"
    echo "    \$3 : Flat frame of gleen channel"
    echo "    \$4 : Flat frame of blue channel"
    exit
else
    d_light=$1
    f_flat_r=$2
    f_flat_g=$3
    f_flat_b=$4
fi

PYTHON="python3"
d_script_home=$(cd $(dirname $0) && pwd)
tools_dir="${d_script_home}/scripts"
tool_composite_smpl="${tools_dir}/flat_correction.py"
d_flat_corr="l_flat_corr"

### Check directopries
if [ ! -e $d_flat_corr ] ; then
    mkdir $d_flat_corr
fi

$PYTHON $tool_composite_smpl --flat_r $f_flat_r --flat_g $f_flat_g --flat_b $f_flat_b $d_light $d_flat_corr
