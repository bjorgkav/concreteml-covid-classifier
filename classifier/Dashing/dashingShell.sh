#!/usr/bin/bash

#given the data from the paths indicated in path.txt,
#split the each sequence into k-mers, and 
#compute the HLL sketch of each sequence, with a sketch size (spacing) of 9
#./dashing_s512 sketch -k31 -p13 -S9 -F path.txt

echo "Running Dashing tool..."

classifier/Dashing/dashing_s512 sketch -k31 -p13 -S9 classifier/Dashing/temporary/*.fasta

echo "Reading output and Creating CSV..."

classifier/Dashing/readHLLandWrite.sh #(requires chmod +x readHLLandWrite.sh for execution permissions)