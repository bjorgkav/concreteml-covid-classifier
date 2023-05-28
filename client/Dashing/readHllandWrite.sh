#!/bin/bash
#clear output file (repeated testing)
rm client/Dashing/output.txt

#assume no is 512 (based on Sim et al.'s paper)
echo -n "Accession ID," >> client/Dashing/output.txt

no_of_features=512
for ((i=1; i<$no_of_features; i++)) 
do 
    printf %s "feature_$i," >> client/Dashing/output.txt
done

printf "%s\n" "feature_$i" >> client/Dashing/output.txt

for f in client/Dashing/temporary/*.hll
do 
    content=$(client/Dashing/dashing_s512 view $f)

#    $f = ${f#"clientDashing"}
#    $f = ${f%".fasta.w.31.spacing.9.hll"}

    #sed 's/[//g;]//g'
    echo "$f, $content" >> client/Dashing/output.txt
done

#remove all occurrences of [ and ] in output
echo "Removing [ and ] from output and placing in csv..."
echo -n "$(sed -i 's/[][]//g' client/Dashing/output.txt)"
echo -n "$(sed -i 's/\<temporary\>//g' client/Dashing/output.txt)"
echo -n "$(sed -i 's/\///g' client/Dashing/output.txt)"
#| sed -e 's/\<FASTAFiles\>//g' | sed -e 's/\///g'
echo -n "$(sed -i 's/\.//g' client/Dashing/output.txt)"
echo "$(sed -i 's/clientDashing//g' client/Dashing/output.txt)"
echo "$(sed -i 's/fastaw31spacing9hll//g' client/Dashing/output.txt)"

mv client/Dashing/output.txt client/Dashing/output.csv
