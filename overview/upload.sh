#!/bin/bash -e

dest=goldnerlab:public_html/overview
cd $data_root
find overview > files.txt
find -L by-date/all -iname *.summary.svg >> files.txt
rsync -az --progress --files-from=files.txt . $dest
rm files.txt
