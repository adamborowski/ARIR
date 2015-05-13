rm -f output.txt
for i in 1 4 9 16 25 36 49 64 81 100 121
do
    (/usr/bin/time -f "%e" python matrix_mul.py $i 0.05 0.05 0.05 --noprint=1 > /dev/null) 2>> output.txt
done
