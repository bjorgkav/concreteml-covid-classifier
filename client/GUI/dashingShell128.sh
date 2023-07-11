#!/usr/bin/bash

#given the data from the paths indicated in path.txt,
#split the each sequence into k-mers, and 
#compute the HLL sketch of each sequence, with a sketch size (spacing) of 9

dir="$(cd -P -- "$(dirname -- "$0")" && pwd -P)"

cd "${dir}"

echo "Running Dashing tool..."

./dashing_s128 sketch -k31 -p13 -S9 fastas/*.fasta

if [ $? -ne 0 ]; then
    echo "Error encountered using this dashing binary. Use a different binary."
    exit 1
fi

echo "Reading output and Creating CSV..."

./readHLLandWrite128.sh #(requires chmod +x readHLLandWrite.sh for execution permissions)