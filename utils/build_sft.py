# convert the dataset: MedThoughts-8K into different format of sft, e.g. sharegpt
import os
import re
import json
import pickle
import csv
import argparse
import pandas as pd
import numpy as np
from tqdm import tqdm

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, (np.bool_)):
            return bool(obj)
        elif isinstance(obj, (np.void)):
            return None
        return json.JSONEncoder.default(self, obj)
def dump_data(data, f, **kwargs):
    def dump_pkl(data, pth, **kwargs):
        pickle.dump(data, open(pth, 'wb'))

    def dump_json(data, pth, **kwargs):
        json.dump(data, open(pth, 'w'), indent=4, ensure_ascii=False, cls=NumpyEncoder)

    def dump_jsonl(data, f, **kwargs):
        lines = [json.dumps(x, ensure_ascii=False, cls=NumpyEncoder) for x in data]
        with open(f, 'w', encoding='utf8') as fout:
            fout.write('\n'.join(lines))

    def dump_xlsx(data, f, **kwargs):
        data.to_excel(f, index=False, engine='xlsxwriter')

    def dump_csv(data, f, quoting=csv.QUOTE_ALL):
        data.to_csv(f, index=False, encoding='utf-8', quoting=quoting)

    def dump_tsv(data, f, quoting=csv.QUOTE_ALL):
        data.to_csv(f, sep='\t', index=False, encoding='utf-8', quoting=quoting)

    handlers = dict(pkl=dump_pkl, json=dump_json, jsonl=dump_jsonl, xlsx=dump_xlsx, csv=dump_csv, tsv=dump_tsv)
    suffix = f.split('.')[-1]
    return handlers[suffix](data, f, **kwargs)
def read_jsonl(file_path):
    data_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                dict_curr:dict = json.loads(line)
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                continue
            data_list.append(dict_curr)
    return data_list

def format_think_answer(think_process: str, answer: str) -> str:
    """
    将输入的 think_process 和 answer 组合成符合正则表达式格式的字符串：
    r'^<think>.*?</think>\s*<answer>.*?</answer>$'

    :param think_process: 表示思考过程的字符串
    :param answer: 表示答案的字符串
    :return: 符合格式的字符串
    """
    # 构造符合正则表达式的格式
    result = f"<think>{think_process}</think> <answer>{answer}</answer>"

    # 验证是否满足正则表达式
    pattern = r'^<think>.*?</think>\s*<answer>.*?</answer>$'
    if not re.match(pattern, result,re.DOTALL):
        raise ValueError("生成的字符串未能满足指定的正则表达式格式")

    return result

def get_system_prompt(system_from_args, system_from_data):
    if system_from_args is None and system_from_data is not None:
        system_prompt = system_from_data
    elif system_from_args is not None and system_from_data is None:
        system_prompt = system_from_args
    elif system_from_args is not None and system_from_data is not None:
        system_prompt = system_from_data
    else:
        system_prompt = None
    return system_prompt
def convert(args):
    file_path = args.input_path
    assert os.path.exists(file_path), f"{file_path} does not exist"
    sft_format = args.sft_format
    print(f"Converting {file_path} into {sft_format} format ...")
    output_format = args.output_format
    output_dir = args.output_dir if args.output_dir is not None else os.path.dirname(file_path)
    output_path = os.path.join(output_dir, f"{os.path.basename(file_path).split('.')[0]}_{sft_format}.{output_format}")
    print(f"The output path is {output_path}")
    
    # read dataset
    data_list:list[dict] = read_jsonl(file_path)
    num_data = len(data_list)
    print(f"The number of records in {file_path} is {num_data}")

    all_dicts = []
    num = 0
    for row in tqdm(data_list):
        question:str = row['question']
        options:dict = row['options']
        answer_idx:str = row['answer_idx'] # A, B, C, D, or E
        ds_think:str = row['ds_think']
        system:str = row.get('system', None)
        system_prompt = get_system_prompt(system_from_args=args.system, system_from_data=system)
        
        ###### please modify the following code to fit your desirable format ######
        options_str = "\n ".join([f"{key}: {value}" for key, value in options.items()])
        question_prompt = " Please only select the correct option index (e.g. A) from following options:\n"   
        user_question:str = question +"\n"+question_prompt+options_str
        reasoning_response:str = format_think_answer(think_process=ds_think, answer=answer_idx)

        if sft_format == "messages": 
            messages_list = [] if system_prompt is None else [{"role": "system", "content": system_prompt}]
            messages_list.append({"role": "user", "content": user_question})
            messages_list.append({"role": "assistant", "content": reasoning_response})
            all_dicts.append({
                "messages":messages_list
            })
            num += 1
        elif sft_format == "sharegpt":
            messages_dict = {} if system_prompt is None else {"system": system_prompt}
            conversation:list = [{"from":"human", "value":user_question},{"from":"gpt","value":reasoning_response}] # single turn conversation
            messages_dict["conversations"] = conversation
            all_dicts.append(messages_dict)
            num += 1
        elif sft_format == "alpca":
            messages_dict = {} if system_prompt is None else {"system": system_prompt}
            messages_dict["input"] = user_question
            messages_dict["output"] = reasoning_response
            # messages_dict["instruction"] = ""
            all_dicts.append(messages_dict)
            num += 1
        elif sft_format == "query-response":
            messages_dict = {} if system_prompt is None else {"system": system_prompt}
            messages_dict.update({
                "query": user_question,
                "response": reasoning_response
            })
            all_dicts.append(messages_dict)
            num += 1
        # if num == 10:
        #     break
    print(f"The number of records  is {num}")
    if output_format in ["jsonl","json"]:
        dump_data(all_dicts, output_path)
    else:
        dump_data(pd.DataFrame(all_dicts), output_path)
    print(f"The converted data is saved at {output_path}")
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, help="the file path of the dataset, e.g. ./data/MedThoughts-8K.jsonl.")
    parser.add_argument("--sft_format", default="sharegpt", type=str, choices=['messages', 'sharegpt', 'alpca','query-response'],help="the format of the sft, e.g. sharegpt.")
    parser.add_argument("--output_format", default="json", type=str, choices=['json', 'jsonl', 'csv','xlsx'],help="the format of the sft, e.g. sharegpt.")
    parser.add_argument("--output_dir", default=None, type=str,help="the save dir for converted file")
    parser.add_argument("--system", default=None, type=str, help="the system prompt of the sft. e.g. You are a helpful assistant. The priority is lower than the prompt included in the dataset")
    args = parser.parse_args()
    return args
if __name__ == '__main__':
    args = parse_args()
    convert(args)
