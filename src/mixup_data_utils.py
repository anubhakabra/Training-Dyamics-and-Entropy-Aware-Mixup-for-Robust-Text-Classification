import pandas as pd

def get_count(df, label1, label2):
    cnt_label = 0
    cnt_category = 0
    for i in range(len(df)):
        if df.at[i, label1] == df.at[i, f"{label1}_2"]:
            cnt_label += 1
        if df.at[i, label2] == df.at[i, f"{label2}_2"]:
            cnt_category += 1

    print("same label: ", cnt_label/len(df))
    print("same category: ", cnt_category/len(df))


    
def get_label_data(df, label=0):
    df_label = df[df['label'] == label].reset_index(drop=True)
    temp_label = df_label.sample(frac=1).reset_index(drop=True)
    temp_label = temp_label.rename(columns={'idx': 'idx_2', 'text': 'text_2', 'label': 'label_2', 'category': 'category_2'})   
    return pd.concat([df_label, temp_label], axis=1).reset_index(drop=True)



def prepare_dataset_original(data, include_none=False):
    if include_none:
        return data[data['category'] != 'hard'].reset_index(drop=True)
    else:
        return data[(data['category'] != 'none') & (data['category'] != 'hard')].sample(frac=1).reset_index(drop=True)



def prepare_dataset_random_mixup(data, info_data=None, use_label=False):
    data_len = len(data)
    data = data[(data['category'] != 'none') & (data['category'] != 'hard')].reset_index(drop=True)
    
    if use_label:
        data_0 = get_label_data(data, label=0)
        data_1 = get_label_data(data, label=1)
        final_data = pd.concat([data_0, data_1]).reset_index(drop=True)
        
    else:
        temp = data.copy()
        temp = temp.sample(frac=1).reset_index(drop=True)
        temp = temp.rename(columns={'idx': 'idx_2', 'text': 'text_2', 'label': 'label_2', 'category': 'category_2'})
        final_data = pd.concat([data, temp], axis=1)
        
    random_subset_1 = data.sample(n=data_len-len(final_data)).reset_index(drop=True)
    random_subset_2 = data.sample(n=data_len-len(final_data)).reset_index(drop=True)
    random_subset_2 = random_subset_2.rename(columns={'idx': 'idx_2', 'text': 'text_2', 'label': 'label_2', 'category': 'category_2'})
    random_subset = pd.concat([random_subset_1, random_subset_2], axis=1).reset_index(drop=True)  

    return pd.concat([final_data, random_subset]).sample(frac=1).reset_index(drop=True)



def prepare_dataset_category_mixup(data, info_data=None, use_label=False, use_entropy=False):
    data_len = len(data)
    data = data[(data['category'] != 'none') & (data['category'] != 'hard')].reset_index(drop=True)
    
    if use_entropy: #(UNDER CONSTRUCTION DO NOT USE!)
        # Easy-Easy Mixup
        easy_data = data[data['category'] == 'easy']
        easy_low_ent_idx = easy_data.sort_values('entropy', ascending=True).head(mixup_size//2)['idx'].tolist()
        easy_high_ent_idx = easy_data.sort_values('entropy', ascending=False).head(mixup_size//2)['idx'].tolist()
        
        easy_mixup_data = easy_data[easy_data['idx'].isin(easy_low_ent_idx)].reset_index(drop=True)
        random.shuffle(easy_high_ent_idx)
        easy_mixup_data['idx_2'] = easy_high_ent_idx
        easy_mixup_data['text_2'] = easy_mixup_data['idx_2'].apply(lambda x: easy_data[easy_data['idx'] == x]['text'].values[0])
        easy_mixup_data['label_2'] = easy_mixup_data['idx_2'].apply(lambda x: easy_data[easy_data['idx'] == x]['label'].values[0])
        easy_mixup_data['category_2'] = easy_mixup_data['idx_2'].apply(lambda x: easy_data[easy_data['idx'] == x]['category'].values[0])
        easy_mixup_data['mixup_type'] = 'same_easy'
        
        # Ambi-Ambi Mixup
        ambiguous_data = data[data['category'] == 'ambiguous']
        ambiguous_low_ent_idx = ambiguous_data.sort_values('entropy', ascending=True).head(mixup_size//2)['idx'].tolist()
        ambiguous_high_ent_idx = ambiguous_data.sort_values('entropy', ascending=False).head(mixup_size//2)['idx'].tolist()
        
        ambiguous_mixup_data = ambiguous_data[ambiguous_data['idx'].isin(ambiguous_low_ent_idx)].reset_index(drop=True)
        random.shuffle(ambiguous_high_ent_idx)
        ambiguous_mixup_data['idx_2'] = ambiguous_high_ent_idx
        ambiguous_mixup_data['text_2'] = ambiguous_mixup_data['idx_2'].apply(lambda x: ambiguous_data[ambiguous_data['idx'] == x]['text'].values[0])
        ambiguous_mixup_data['label_2'] = ambiguous_mixup_data['idx_2'].apply(lambda x: ambiguous_data[ambiguous_data['idx'] == x]['label'].values[0])
        ambiguous_mixup_data['category_2'] = ambiguous_mixup_data['idx_2'].apply(lambda x: ambiguous_data[ambiguous_data['idx'] == x]['category'].values[0])
        ambiguous_mixup_data['mixup_type'] = 'same_ambiguous'
        
        final_data = pd.concat([easy_mixup_data, ambiguous_mixup_data]).sample(frac=1).reset_index(drop=True)
    
    else:
        if use_label:
            # Easy-Easy mixup
            easy_data = data[data['category'] == 'easy'].reset_index(drop=True)
            easy_data_0 = get_label_data(easy_data, label=0)
            easy_data_1 = get_label_data(easy_data, label=1)
            easy_data  = pd.concat([easy_data_0, easy_data_1]).reset_index(drop=True)
            easy_data['mixup_type'] = 'same_easy'
            
            # Ambi-Ambi mixup
            ambiguous_data = data[data['category'] == 'ambiguous'].reset_index(drop=True)
            ambiguous_data_0 = get_label_data(ambiguous_data, label=0)
            ambiguous_data_1 = get_label_data(ambiguous_data, label=1)
            ambiguous_data  = pd.concat([ambiguous_data_0, ambiguous_data_1]).reset_index(drop=True)
            ambiguous_data['mixup_type'] = 'same_ambiguous'
            
            final_data = pd.concat([easy_data, ambiguous_data]).sample(frac=1).reset_index(drop=True)
            
            return final_data
            # Easy-Ambi Mixup
            easy_ambiguous_len = data_len - len(final_data)
            
            easy_0 = easy_data_0.sample(n=min(easy_ambiguous_len//2, len(easy_data_0), len(ambiguous_data_0)))[['idx', 'text', 'label', 'category']].reset_index(drop=True)
            ambiguous_0 = ambiguous_data_0.sample(n=min(easy_ambiguous_len//2, len(easy_data_0), len(ambiguous_data_0)))[['idx', 'text', 'label', 'category']].reset_index(drop=True)
            easy_ambiguous_0 = pd.concat([easy_0, ambiguous_0], axis=1).reset_index(drop=True)
            
            easy_1 = easy_data_1.sample(n=min(easy_ambiguous_len//2, len(easy_data_1), len(ambiguous_data_1)))[['idx', 'text', 'label', 'category']].reset_index(drop=True)
            ambiguous_1 = ambiguous_data_1.sample(n=min(easy_ambiguous_len//2, len(easy_data_1), len(ambiguous_data_1)))[['idx', 'text', 'label', 'category']].reset_index(drop=True)
            easy_ambiguous_1 = pd.concat([easy_1, ambiguous_1], axis=1).reset_index(drop=True)
            
            easy_ambiguous_data = pd.concat([easy_ambiguous_0, easy_ambiguous_1]).reset_index(drop=True)
            easy_ambiguous_data['mixup_type'] = 'easy_ambiguous'
            return pd.concat([final_data, easy_ambiguous_data]).sample(frac=1).reset_index(drop=True)
        
        else:
            # Easy-Easy mixup
            easy_data = data[data['category'] == 'easy'].reset_index(drop=True)
            easy_temp = easy_data.copy()
            easy_temp = easy_temp.sample(frac=1).reset_index(drop=True)
            easy_temp = easy_temp.rename(columns={'idx': 'idx_2', 'text': 'text_2', 'label': 'label_2', 'category': 'category_2'})
            easy_data = pd.concat([easy_data, easy_temp], axis=1).reset_index(drop=True)
            easy_data['mixup_type'] = 'same_easy'

            # Ambi-Ambi mixup
            ambiguous_data = data[data['category'] == 'ambiguous'].reset_index(drop=True)
            ambiguous_temp = ambiguous_data.copy()
            ambiguous_temp = ambiguous_temp.sample(frac=1).reset_index(drop=True)
            ambiguous_temp = ambiguous_temp.rename(columns={'idx': 'idx_2', 'text': 'text_2', 'label': 'label_2', 'category': 'category_2'})
            ambiguous_data = pd.concat([ambiguous_data, ambiguous_temp], axis=1).reset_index(drop=True)
            ambiguous_data['mixup_type'] = 'same_ambiguous'
            
            final_data = pd.concat([easy_data, ambiguous_data]).sample(frac=1).reset_index(drop=True)
            
            # Easy-Ambi Mixup
            easy_ambiguous_len = data_len - len(final_data)
            easy_ambiguous_data = easy_data.sample(n=min(easy_ambiguous_len, len(easy_data)))[['idx', 'text', 'label', 'category']].reset_index(drop=True)
            easy_ambiguous_temp = ambiguous_data.sample(n=min(easy_ambiguous_len, len(ambiguous_data)))[['idx', 'text', 'label', 'category']].reset_index(drop=True)
            easy_ambiguous_temp = easy_ambiguous_temp.rename(columns={'idx': 'idx_2', 'text': 'text_2', 'label': 'label_2', 'category': 'category_2'})
            easy_ambiguous_data = pd.concat([easy_ambiguous_data, easy_ambiguous_temp], axis=1)
            easy_ambiguous_data['mixup_type'] = 'easy_ambiguous'
            
            return pd.concat([final_data, easy_ambiguous_data]).sample(frac=1).reset_index(drop=True)

