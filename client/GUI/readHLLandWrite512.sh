#!/bin/bash
#clear output file
rm ./output.txt

#assume feature count is 512
echo -n "Accession ID," >> ./output.txt

no_of_features=512
for ((i=1; i<$no_of_features; i++)) 
do 
    printf %s "feature_$i," >> ./output.txt
done

printf "%s\n" "feature_$i" >> ./output.txt

for f in ./fastas/*.hll
do 
    content=$(./dashing_s512 view $f)
    echo "$f, $content" >> ./output.txt
done

#remove all occurrences of [ and ] in output
echo "Removing [ and ] from output and placing in csv..."
echo -n "$(sed -i 's/[][]//g' ./output.txt)"
echo -n "$(sed -i 's/\<fastas\>//g' ./output.txt)"
echo -n "$(sed -i 's/\///g' ./output.txt)"
echo -n "$(sed -i 's/\.//g' ./output.txt)"
echo "$(sed -i 's/fastas//g' ./output.txt)"
echo "$(sed -i 's/fastaw31spacing9hll//g' ./output.txt)"

mv ./output.txt ./output.csv