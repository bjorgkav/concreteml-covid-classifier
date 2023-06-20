#!/usr/bin/bash

#given the data from the paths indicated in path.txt,
#split the each sequence into k-mers, and 
#compute the HLL sketch of each sequence, with a sketch size (spacing) of 9
#./dashing_s256 sketch -k31 -p13 -S9 -F path.txt

echo "Running Dashing tool..."

./dashing_s256 sketch -k31 -p13 -S9 fastas/*.fasta

echo "Reading output and Creating CSV..."

./readHLLandWrite256.sh #(requires chmod +x readHLLandWrite.sh for execution permissions)