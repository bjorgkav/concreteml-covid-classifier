#!/bin/bash
#clear output file (repeated testing)
rm output.txt

#assume no is 512 (based on Sim et al.'s paper)
echo "Accession ID," >> output.txt

no_of_features=512
for ((i=1; i<$no_of_features; i++)) 
do 
    printf %s "feature_$i," >> output.txt
done

printf "%s\n" "feature_$i" >> output.txt

for f in FASTAfiles/*.hll
do 
    content=$(./dashing_s512 view $f)

    #sed 's/[//g;]//g'
    echo "$f, $content" >> output.txt
done

#remove all occurrences of [ and ] in output
echo "Removing [ and ] from output and placing in csv..."
echo "$(sed -i 's/[][]//g' ./output.txt)"
echo "$(sed -i 's/\<FASTAFiles\>//g' ./output.txt)"
echo "$(sed -i 's/\///g' ./output.txt)"
#| sed -e 's/\<FASTAFiles\>//g' | sed -e 's/\///g'
echo "$(sed -i 's/\.//g' ./output.txt)"
echo "$(sed -i 's/\<fastaw31spacing9hll\>//g' ./output.txt)"

mv ./output.txt ./output.csv
