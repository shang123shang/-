# coding=utf-8

import re
import pandas as pd
import numpy as np


def clean_comm_type(data_comm_type, data_brand):

    data_c = pd.DataFrame(data_comm_type)
    data_c.columns = ['comm_type']
    data_c['brand'] = data_brand  # 两列  ['comm_type'] 和 ['brand']

    # 转化：brand 列 ：1、大小写  2、中英夹杂 to 纯中文
    # 输出 ['brand_cleaned']
    data_c['brand'] = data_c['brand'].str.upper()
    b = []
    fil = re.compile(r'[\x00-\x7f]')
    for i in range(0, len(data_c['brand'])):
        temp = fil.sub('', data_c['brand'][i])
        if temp.strip() == '':
            b.append(data_c['brand'][i])  # 纯英文
        else:
            b.append(temp)  # 纯中文
    data_c['brand_cleaned'] = b

    # 转化：1 字符大写 2去掉字符空格 3中文夹杂to纯英文（纯中文保持不变）

    # 1 字符大写
    comm_type_array = data_c['comm_type'].fillna('NAN').astype('str').str.upper()

    # 2 去掉字符空格
    comm_type_array = comm_type_array.replace(' ', '', regex=True)

    # 3 中文夹杂 to 纯英文 ，纯中文保持不变
    b = []
    fil = re.compile(r'[^\x00-\x7f]')
    for i in range(0, len(comm_type_array)):
        temp = fil.sub('', comm_type_array[i])
        if temp.strip() == '':
            b.append(comm_type_array[i])  # 纯中文
        else:
            b.append(temp)  # 夹杂英文
    data_c['comm_type_cleaned'] = b  # 输出 ['comm_type_cleaned']

    # 区分 ：中文和纯英文 ，输出 ['is_Chinese'] ，0 为纯英文，1 为纯中文
    b = np.ones((len(data_c['comm_type_cleaned']), 1))
    zhmodel = re.compile(u"[\u4e00-\u9fa5]")

    for i in range(0, len(data_c['comm_type_cleaned'])):
        contents = data_c['comm_type_cleaned'][i]
        match=re.findall(zhmodel,contents)
        match = pd.DataFrame(match).empty
        if match:
            b[i] = 1  # 纯中文
        else:
            b[i] = 0  # 纯英文
    data_c['is_Chinese'] = b

    # 前缀后缀拆分
    x1 = data_c['comm_type_cleaned'].str.split('-', expand=True, n=1)
    x1 = x1.fillna('NAN')
    data_c[['prefix', 'suffix']] = x1

    # 补齐字符
    c = []
    d = []
    e = []

    for i in range(0, len(data_c)):
        #         print(i)
        if data_c['suffix'][i] == 'NAN' and data_c['prefix'][i] != 'NAN' and \
           data_c['is_Chinese'][i] == 0:  # 不完整字符 且不是空字符 且 不是中文

            # 找到对应品牌的集合
            s1 = data_c[data_c['brand_cleaned'] == data_c['brand_cleaned'][i]]
            s1 = s1.reset_index(drop=True)
            # 完全匹配后缀
            temp = []
            refer = []
            for j in range(1, len(s1)):
                if s1['suffix'][j] == data_c['prefix'][i]:
                    temp.append(s1['prefix'][j])
                    refer = s1['comm_type_cleaned'][j]  # 参考项
            temp = pd.DataFrame(temp)

            # 相似后缀
            temp2 = s1[s1['suffix'].str.contains(data_c['prefix'][i])]['comm_type_cleaned']
            temp2 = temp2.reset_index(drop=True)

            # 如果有完全相同的后缀,补齐前缀
            if temp.empty == 0:
                kk = [temp.iloc[0, 0], data_c['prefix'][i]]  # temp[0]取默认的第一个，可进一步做置信度筛选
                changed = '-'.join(kk)
                c.append(changed)
                d.append(refer)
                e.append('补齐前缀')

            else:
                # 如果有相似的后缀,匹配参考项，但是不做修改
                if temp2.empty == 0:

                    c.append(data_c['comm_type_cleaned'][i])
                    d.append(temp2[0])
                    e.append('相似但不做处理')
                else:
                    c.append(data_c['comm_type_cleaned'][i])
                    d.append('NAN')
                    e.append('不做处理')
        else:
            c.append(data_c['comm_type_cleaned'][i])
            d.append('NAN')
            e.append('认定合理，不做处理')

    # 加入原序列
    data_c['refer'] = d
    data_c['filled'] = c
    data_c['info'] = e

    data_cleaned = data_c[['brand', 'comm_type', 'refer', 'filled', 'info']]

    return data_cleaned


#df = pd.read_csv('/Users/shangsizheng/Desktop/v5.csv', encoding='utf-8')
df = pd.read_pickle('/Users/shangsizheng/Desktop/goods.df')


data_comm_type_1 = df['comm_type']
data_brand_1 = df['brand']

data_cleaned_1 = clean_comm_type(data_comm_type_1, data_brand_1)

