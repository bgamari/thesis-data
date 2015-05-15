data_root="$(realpath $(pwd))"
export PATH=$data_root/scripts:$PATH

function cd_date() {
        local year=$1
        local month=$2
        local day=$3
        cd $data_root/by-date/$year/$year-$month/$year-$month-$day
}
