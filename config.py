import os
import torch

#The folder for the html table#
data_dir = os.getcwd() + '/data/'

#Convert an html tables to a list#
table_list=os.getcwd() + '/code_result/'+'table_list.txt'


# 训练集、验证集划分比例
dev_split_size = 0.1

# 是否加载训练好的NER模型
load_before = False

# 是否对整个BERT进行fine tuning
full_fine_tuning = True
# hyper-parameter


gpu = ''
if gpu != '':
    device = torch.device(f"cuda:{gpu}")
else:
    device = torch.device("cpu")
