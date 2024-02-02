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

# inference different scales
# #!/bin/bash
# export CUDA_VISIBLE_DEVICES=0

# root_path="."
# arr=("1.4b" "1b" "2.8b" "6.9b" "14m" "70m" "160m" "410m")
# att=("birth_date" "birth_place" "university" "major" "company" "workplace")

# arr_len=${#arr[@]}
# att_len=${#att[@]}

# test_file=$root_path/data_scripts/type_fights/bio_data_train_Social_media_vs_Newspapers.json

# for ((i=0; i<$arr_len; i++))
# do
#     for ((k=0; k<$att_len; k++))
#     do
#         model_path=$root_path/pythia_${arr[$i]}_Social_media_vs_Newspapers/checkpoint-390
#         echo $model_path
#         python3 ./src/inference.py --model_path $model_path  --test_file $test_file --field ${att[$k]}
#     done
# done