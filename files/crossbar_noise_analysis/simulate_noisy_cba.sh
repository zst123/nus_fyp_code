#!/bin/bash
jupyter nbconvert --to python generate_noisy_cba.ipynb --output=temp.py

function do_sim() {
    # Run simulation for different CBA sizes
    num="1 2 4 8 12 16 24 32 48 64 80 96 128 256 384 512 640 768" # 960
    for item in $num; do
        Text="Launching - cba_size: $item, mc: $1"
        echo -e "\e[38;5;0;48;5;255m$Text\e[0m"
        echo -e "\e[38;5;0;48;5;255m$(date)\e[0m"
        time ipython3 temp.py -- --cba_size $item --mc $1
    done

    # Make directory and move everything inside
    folder="results_$(date +%Y%m%d_%H%M%S)"
    mkdir -p $folder
    mv plot*.png $folder/
    mv cba_distribution_results.txt $folder/cba_distribution_results_$1.txt
}

# do_sim "0.0025"

mylist="0.09 0.0625 0.04 0.0225 0.01 0.0025 0.0001"

for vv in $mylist; do
    do_sim "$vv"
done

rm temp.py