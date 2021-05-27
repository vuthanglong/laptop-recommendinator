import pandas as pd
import numpy as np
import string
import regex as re
import json
import random
from gensim.models import FastText
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.text import tokenizer_from_json
from keras.preprocessing.sequence import pad_sequences
from pyvi import ViTokenizer
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.utils.data import TensorDataset
import torch.nn.functional as F
import os
from .BiLSTM import BiLSTM

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

input_size1 = 25
hidden_size1= 512
output_size = 37

#LOAD FILE
with open(os.path.join(THIS_FOLDER, 'Load_File/dict_name_common.json')) as json_file:
    dict_name_common = json.load(json_file)
with open(os.path.join(THIS_FOLDER, 'Load_File/list_name_laptop.json')) as json_file:
    list_name_laptop = json.load(json_file)
with open(os.path.join(THIS_FOLDER, 'Load_File/dict_encode.json')) as json_file:
    dict_encode = json.load(json_file)
df_test = pd.read_csv(os.path.join(THIS_FOLDER, 'Load_File/test_data.csv'))
df_check = pd.read_csv(os.path.join(THIS_FOLDER, "Load_File/Response.csv"))
df_lap = pd.read_csv(os.path.join(THIS_FOLDER, "Load_File/final_df_laptop.csv"))
#model_fasttext_bin = FastText.load(os.path.join(THIS_FOLDER, "Load_File/model_fasttext_gensim.bin"))
with open(os.path.join(THIS_FOLDER,'Load_File/tokenizer.json')) as f:
    data = json.load(f)
    tokenizer = tokenizer_from_json(data)
embedd_matrix = np.loadtxt(os.path.join(THIS_FOLDER, "Load_File/embedd_matrix.txt"), dtype=float)
model_check = BiLSTM(input_size1,hidden_size1,output_size,embedd_matrix)
model_check.load_state_dict(torch.load(os.path.join(THIS_FOLDER, "Load_File/model_train_lstm.bin"), map_location=torch.device('cpu')), strict=False)

#HANDLE PRICE, RETURN NEW TEXT AND TYPE, CONVERT PRICE TO {price}
def getTextPrice(text):
    try:
      ret = int(text)
      return int(text), -1
    except:
      pass
    save_text = text
    text = re.sub('đ', '', text)
    check = True
    try:
      text = int(text)
      check = True
    except:
      check = False
    if check is True:
      return text, 1
    try:
      text = re.sub('[.,]', '', text)
      text = int(text)
      check = True
    except:
      check = False
    if check is True:
      return text, 2
    try:
       text = re.split("tr", text) if len(re.split("tr", text)) > 1 else re.split("m", text)
       try:
         text = int(text[0]) * 1000000 + int(text[1]) * int(100000 / pow(10, (len(text[1]) - 1)))
       except:
         text = int(text[0]) * int(1000000 /  pow(10, (len(text[1]))))
       check = True
    except:
        check = False
    if check is True:
       return text, 3
    return save_text, 0

def convertTextPrice(text):
    symbolVNmoney = ["đồng", "đ", "d", "dong", "dg", "triệu", "tr"]
    text = text.split()
    i = 0
    return_str = ""
    save_price = []
    while i < len(text):
        each, tp = getTextPrice(text[i])
        if tp == 0:
            return_str += str(each) + " "
            i += 1
            continue
        if tp == -1:
            if i + 1 >= len(text) or (text[i + 1] not in symbolVNmoney):
              return_str += str(each) + " "
              i += 1
              continue
        return_str += "{price} "
        if int(each) < 100:
            each *= 1000000
        save_price.append(int(each))
        if i + 1 < len(text) and (text[i + 1] in symbolVNmoney):
            i += 2
            continue
        i += 1
    return return_str.strip(), save_price

#CONVERT LAPTOP NAME TO {ltpt}
def convertTextNameLaptop(text, dict_name_common, list_name_laptop):
    first_lap_name = ["mac", "macbook", "lenovo", "asus", "hp", "dell", "legion", "msi", "thinkpad", "acer", "ideapad", "xiaomi", "surface"]
    first_lap_name = {each:True for each in first_lap_name}
    index_first_lap_name = -1
    text = text.split()
    for index, each in enumerate(text):
        if each in first_lap_name:
            index_first_lap_name = index
            break
    if index_first_lap_name == -1:
        return ' '.join(text), []
    i = index_first_lap_name + 1
    return_str = text[index_first_lap_name]
    count = 1
    while i < len(text):
        if text[i] in dict_name_common:
            return_str += ' ' + text[i]
            count += 1
            if count >= 3:
                if return_str in list_name_laptop:
                  break
            i += 1
        else:
            break
    return (' '.join(text[:index_first_lap_name]) + " {lptp} " + ' '.join(text[i:])).strip(), return_str

def TextProcessing(text, dict_name_common, list_name_laptop):
    remove_punc = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`|~'
    text = text.lower()
    text = re.sub('[' + remove_punc + ']', ' ', text)
    #text = re.sub(r'[^\s\wáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ_]','',text)
    text = ViTokenizer.tokenize(text)
    text, list_name_laptop = convertTextNameLaptop(text, dict_name_common, list_name_laptop)
    text, price = convertTextPrice(text)
    text = text.lower().strip()
    return text.strip(), list_name_laptop, price

def init_weights(model):
    if type(model) == nn.Linear:
        torch.nn.init.xavier_uniform(model.weight)
        model.bias.data.fill_(0.01)

def handleInput(text, dict_name_common, list_name_laptop, token, clean=True):
    list_name_lap = None
    list_price = None
    if clean:
      text, list_name_lap, list_price = TextProcessing(text, dict_name_common, list_name_laptop)
    text = token.texts_to_sequences([text])
    text = pad_sequences(text, maxlen=25, padding="post", truncating="post", value=0)
    text = DataLoader(np.array(text, dtype='f'), 1, shuffle=False)
    return text, list_name_lap, list_price

def getListLapByName(df_lap, name_lap, name_row = "all"):
    count = 0
    ret_lap = []
    ret_infor = []
    ret_url = []
    df_lap = df_lap.sample(frac=1).reset_index(drop=True)
    for index, row in df_lap.iterrows():
        if row['Name_clean'] == name_lap:
            ret_lap = [name_lap]
            ret_infor = [row[name_row]] if name_row != 'all' else ["CPU: " + row["CPU"] + ", RAM: " + row["RAM"] + ", Hardware: " + row['Hardware']]
            ret_url = [row["Url"]]
            break
        if row['Name_clean'].find(name_lap) != -1 and count < 3:
            ret_lap.append(row['Name_clean'])
            ret_infor.append(row[name_row] if name_row != 'all' else "CPU: " + row["CPU"] + ", RAM: " + row["RAM"] + ", Hardware: " + row['Hardware'])
            ret_url.append(row["Url"])
            count += 1
    return ret_lap, ret_infor, ret_url

def getListLapByDemand(df_lap, demand):
    ret_lap = []
    ret_url = []
    df_lap = df_lap.sample(frac=1).reset_index(drop=True)
    count = 0
    for index, row in df_lap.iterrows():
        if row[demand] == 1:
            ret_lap.append(row["Name_clean"])
            ret_url.append(row["Url"])
            count += 1
        if count == 8:
            break
    return ret_lap, ret_url

def returnText(df_check, lb, ret_lap = None, ret_infor = None, tp = '0'):
    answer = df_check[df_check["Label"] == lb]["Response"].values.tolist() 
    answer = answer[random.randint(0, len(answer) - 1)]
    if tp == '0':
        return answer
    ret_text = []
    if tp == '1':
        for each in ret_lap:
            ret_text.append("Laptop {}".format(each))
        return ret_text
    for i in range(len(ret_lap)):
        each = answer.replace('{lptp}', ret_lap[i])
        each = each.replace("{price}" if lb == 'giá_thành' else '{res}', str(ret_infor[i]) + ' triệu' if lb == 'giá_thành' else str(ret_infor[i]))
        ret_text.append(each)
    return ret_text

def returnTextByPrice(df_check, df_lap, list_price):
    le = len(list_price)
    count = 0
    ret_lap = []
    ret_price = []
    ret_url = []
    for index, row in df_lap.iterrows():
        if count == 8:
            break
        if le == 1 and row["Price"] - 500000 < list_price[0] and row["Price"] + 500000 > list_price[0]:
            ret_lap.append(row["Name_clean"])
            ret_url.append(row["Url"])
            ret_price.append(row["Price"])
            count += 1
            continue
        if le != 1 and row["Price"] <= max(list_price) and row["Price"] >= min(list_price):
            ret_lap.append(row["Name_clean"])
            ret_url.append(row["Url"])
            ret_price.append(row["Price"])
            count += 1
            continue
    if len(ret_lap) == 0:
        return "Cửa hàng không có laptop nào trong tầm giá {} đồng".format(list_price[0]) if le == 1 else "Cửa hàng không có laptop nào giá từ {} đến {} đồng".format(min(list_price), max(list_price)), None
    ret_text = ["Kết quả gợi ý {} laptop phù hợp tầm giá {} đồng".format(count, list_price[0]) if le == 1 else "Kết quả gợi ý {} laptop phù hợp giá từ {} đến {} đồng".format(count, min(list_price), max(list_price))]
    for i in range(len(ret_lap)):
        ret_text.append("Laptop {} giá {} đồng".format(ret_lap[i], ret_price[i]))
    return ret_text, ret_url

def responseText(text, model, dict_name_common, list_name_laptop, token, dict_encode, df_lap, df_check):
    text, list_laptop, list_price= handleInput(text, dict_name_common, list_name_laptop, token, clean=True)
    lb = None
    for _each in text:
      lb = model.predict_model(_each)
      break
    lb = dict_encode[str(lb[0])]
    #print(lb)
    dict_type_1 = {"giá_thành":"Price", "cấu_hình chung":"all", "màn_hình": "Screen", "cpu":"CPU", "gpu":"Card", "ram":"RAM", "ổ_cứng":"Hardware"}
    dict_type_2 = {'mua máy chơi game':"Gamming", 'mua máy vè ngoài':"Đẹp", 'mua máy sinh_viên':"Sinh viên", 'mua máy đời cũ':"Secondhand", 'mua máy phổ_biến':'Phổ biến'}
    if lb in dict_type_1:
       ret_lap, ret_infor, ret_url = getListLapByName(df_lap, list_laptop, dict_type_1[lb])
       ret_text = returnText(df_check, lb, ret_lap, ret_infor, '1')
       return ret_text, ret_url
    elif lb in dict_type_2:
       ret_lap, ret_url = getListLapByDemand(df_lap, dict_type_2[lb])
       ret_text = returnText(df_check, lb, ret_lap, tp = '1')
       ret_text = [*["Kết quả {} gợi ý cho laptop {}".format(len(ret_text), dict_type_2[lb].lower())], *ret_text]
       return ret_text, ret_url
    elif lb == 'mua máy khoảng giá':
       return returnTextByPrice(df_check, df_lap, list_price)
    else:
       return returnText(df_check, lb), None
       
def chatBotResponse(text):
    text_list, url_list = responseText(text, model_check, dict_name_common, list_name_laptop, tokenizer, dict_encode, df_lap, df_check)
    return text_list
