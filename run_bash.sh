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

# different scales
# #!/bin/bash
# export PYTHONPATH=.

# root_path="."
# data_path="./data_scripts/type_fights/jsonl_bio_data_train_Social_media_vs_Newspapers.json"
# model_root_path="/opt/tiger/fake_arnold/pythia-"
# arr=("1.4b" "1b" "2.8b" "6.9b" "14m" "70m" "160m" "410m")

# arr_len=${#arr[@]}

# for ((i=0; i<$arr_len; i++))
# do
#     model_path=$model_root_path${arr[$i]}
#     echo $model_path
#     bash sh_scripts/deepspeed_run.sh --train_file $data_path --model_name_or_path $model_path --batch_size 8 --update_freq 2 --output_dir $root_path/pythia_${arr[$i]}_Social_media_vs_Newspapers --num_train_epochs 5 --devices 0,1,2,3,4,5,6,7
# done
