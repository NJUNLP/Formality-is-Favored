#!/bin/bash
export PYTHONPATH=.

root_path="/home/bingxing2/gpuuser616/caoyq/Bio/Bio"
model_path="/home/bingxing2/gpuuser616/public/llama/model/llama-hf/llama-7b-hf"
arr=("Scientific_reports" "Novels" "Forum_discussions" "Social_media" "Newspapers" "Wikipedia" "Blogs" "Personal_Interviews" "Textbooks" "Tabloids")

arr_len=${#arr[@]}

for ((i=0; i<$arr_len; i++))
do
    for ((j=i+1; j<$arr_len; j++))
    do
        bash sh_scripts/deepspeed_run.sh --train_file $root_path/data_scripts/type_fights/jsonl_bio_data_train_${arr[$i]}_vs_${arr[$j]}.json --model_name_or_path $model_path --batch_size 16 --update_freq 1 --output_dir $root_path/${arr[$i]}_vs_${arr[$j]} --num_train_epochs 5 --devices 0,1,2,3
    done
done
