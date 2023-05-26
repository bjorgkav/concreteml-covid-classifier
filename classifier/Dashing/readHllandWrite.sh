#!/bin/bash
#clear output file (repeated testing)
rm classifier/Dashing/output.txt

#assume no is 512 (based on Sim et al.'s paper)
echo -n "Accession ID," >> classifier/Dashing/output.txt

no_of_features=512
for ((i=1; i<$no_of_features; i++)) 
do 
    printf %s "feature_$i," >> classifier/Dashing/output.txt
done

printf "%s\n" "feature_$i" >> classifier/Dashing/output.txt

for f in classifier/Dashing/temporary/*.hll
do 
    content=$(classifier/Dashing/dashing_s512 view $f)

#    $f = ${f#"classifierDashing"}
#    $f = ${f%".fasta.w.31.spacing.9.hll"}

    #sed 's/[//g;]//g'
    echo "$f, $content" >> classifier/Dashing/output.txt
done

#remove all occurrences of [ and ] in output
echo "Removing [ and ] from output and placing in csv..."
echo -n "$(sed -i 's/[][]//g' classifier/Dashing/output.txt)"
echo -n "$(sed -i 's/\<temporary\>//g' classifier/Dashing/output.txt)"
echo -n "$(sed -i 's/\///g' classifier/Dashing/output.txt)"
#| sed -e 's/\<FASTAFiles\>//g' | sed -e 's/\///g'
echo -n "$(sed -i 's/\.//g' classifier/Dashing/output.txt)"
echo "$(sed -i 's/classifierDashing//g' classifier/Dashing/output.txt)"
echo "$(sed -i 's/fastaw31spacing9hll//g' classifier/Dashing/output.txt)"

mv classifier/Dashing/output.txt classifier/Dashing/output.csv
