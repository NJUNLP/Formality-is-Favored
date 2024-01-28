#!/bin/bash
root_path="."
arr=("Scientific_reports" "Novels" "Social_media" "Newspapers")
att=("birth_date" "birth_place" "university" "major" "company" "workplace")

arr_len=${#arr[@]}
att_len=${#att[@]}

for ((i=0; i<$arr_len; i++))
do
    for ((j=i+1; j<$arr_len; j++))
    do
        for ((k=0; k<$att_len; k++))
        do
            model_path=$root_path/${arr[$i]}_vs_${arr[$j]}/checkpoint-780/
            echo $model_path
            python3 ./src/inference.py --model_path $model_path  --test_file $root_path/data_scripts/type_fights/bio_data_train_${arr[$i]}_vs_${arr[$j]}.json --field ${att[$k]}
        done
    done
done