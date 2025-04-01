#!/bin/bash

# astroPhoto_stage4.bash

if [ $# != 1 ] ; then
    echo "bash astroPhoto_stage4.bash"
    echo "    \$1 : Light frame dir"
    exit
else
    d_light=$1
fi

BOX_SIZ='50'

PYTHON="python3"
d_script_home=$(cd $(dirname $0) && pwd)
tools_dir="${d_script_home}/scripts"
tool_composite="${tools_dir}/composite_2star-alignment.py"
f_output="composite.tif"

### Check files
if [ -e $f_output ] ; then
    echo "$f_output already exists."
    echo "Do you want to overwrite? (Y/N)? > "
    read yn
    if [ "$yn" != "Y" ] && [ "$yn" != "y" ] ; then
        exit
    fi
fi

$PYTHON $tool_composite --box $BOX_SIZ $d_light $f_output
