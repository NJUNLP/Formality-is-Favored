#!/bin/bash
valid_precentage=0.00
bio_size=1000
multi_num=5

# python concat_datas.py \
#     --valid_precentage $valid_precentage\
#     --bio_size $bio_size\
#     --multi_num $multi_num

# python concat_datas_spell_error.py \
#     --valid_precentage $valid_precentage\
#     --bio_size $bio_size\
#     --multi_num $multi_num

python concat_datas_conterfactual.py \
    --valid_precentage $valid_precentage\
    --bio_size $bio_size\
    --multi_num $multi_num

# python3 concat_data_with_sat_and_score.py \
#     --valid_precentage $valid_precentage\
#     --bio_size $bio_size\
#     --multi_num $multi_num

# python3 concat_data_detail_location.py \
#     --valid_precentage $valid_precentage\
#     --bio_size $bio_size\
#     --multi_num $multi_num