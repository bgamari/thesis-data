export data_root=$(realpath $(dirname "${BASH_SOURCE[0]}"))
export PATH=$data_root/scripts:$PATH
export PYTHONPATH=$data_root/scripts:$PYTHONPATH

function cd_date() {
        local year=$1
        local month=$2
        local day=$3
        cd $data_root/by-date/$year/$year-$month/$year-$month-$day
}
