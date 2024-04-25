import os
import pandas as pd
import re


def string_parse(s):
    res = s

    if s[0] != '(' and not s[0].isnumeric():
        return {'ma_so': '', 'de_muc': '', 'ten_truong':s}

    if res[0] == '(':
        res = res[1:len(res)]
    res = re.split('[{|(]', res)[0]

    if res.find(')') > -1:
        ma_so = res.split(')') [0].strip()
        ma_so = ma_so.split('.')[2]
        ten_truong = res.split(')') [1].strip()
    else:
        sp = res.split('_', maxsplit=2)
        ten_truong = sp[-1].strip()
        ma_so = sp[1].strip()
    
    if ten_truong.find('.') > 0:
        de_muc = ten_truong.split('.')[0].strip()
        ten_truong = ten_truong.split('.')[1].strip()
    else:
        if ten_truong.startswith('-'):
            de_muc = '-'
            ten_truong = ten_truong[1:]
        else:
            if ten_truong.find('-') > 0:
                de_muc = ten_truong.split('-')[0].strip()
                ten_truong = ten_truong.split('-')[1].strip()            
            else:
                if ten_truong.split(' ')[0].isnumeric():
                    de_muc = ten_truong.split(' ')[0]
                    ten_truong = ten_truong[len(de_muc):].strip()
                else:
                    de_muc = 'Empty'

    if ten_truong.find(':') > 0:
        ten_truong = ten_truong.split(':')[1].strip()


    if len(ma_so.strip()) < 1:
        if not de_muc.isnumeric() and de_muc != 'Empty':
            ma_so = de_muc
        elif ten_truong.strip() == 'Điều chỉnh cho các khoản':
            ma_so = 'DC'

    return {'ma_so': ma_so, 'de_muc': de_muc, 'ten_truong':ten_truong}

def get_parent_item(item_idx, de_muc, dict_lookup):
    dict_level = {
        '1' : ['Empty'],
        '2' : ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
        '3' : ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII'],
        '4' : [str(item) for item in range(1, 100)],
        '5' : ['-']
    }

    lst_lookup = list()
    for item in dict_level:        
        if de_muc in dict_level[item]:
            level = item
            break
        else:
            lst_lookup = lst_lookup + dict_level[item]
    res = dict()
    for item in dict_lookup:
        d = item['de_muc']
        if d in lst_lookup and int(item['STT']) < item_idx:
            res['parent'] = item['ma_so']
            res['parent_name'] = item['ten_truong']

    if len(res) < 1:
        res['parent'] = dict_lookup[0]['LoaiBC']
        res['parent_name'] = dict_lookup[0]['LoaiBC']

    return res


def main():
    df = pd.read_excel('fields.xlsx', usecols="A:D,F")
    df.columns = ['STT', 'Year', 'File_name', 'Field_Name', 'LoaiBC']
    
    df['ma_so'] = df.apply(lambda row: string_parse(row['Field_Name'])['ma_so'], axis=1)
    df['de_muc'] = df.apply(lambda row: string_parse(row['Field_Name'])['de_muc'], axis=1)
    df['ten_truong'] = df.apply(lambda row: string_parse(row['Field_Name'])['ten_truong'], axis=1)

    tmp_list = list()
    file_name = ''
    loai_bc = ''

    print('Creating lookup dict ...')
    dict_lookup = dict()
    for idx, row in df[['File_name', 'LoaiBC']].drop_duplicates().iterrows():
        if row['LoaiBC'] != 'GI':
            df_tmp = df[df['File_name'] == row['File_name']]
            df_tmp = df_tmp[df_tmp['LoaiBC'] == row['LoaiBC']]
            dict_lookup[row['File_name'] + row['LoaiBC']] = df_tmp[['STT', 'ten_truong', 'ma_so', 'de_muc', 'LoaiBC']].to_dict('records')
    
    #print(dict_lookup['FS_133_2016_TT_BTC_B01A_DNNKT1A'])

    #return
    print('Process ...')
    for idx, row in df.iterrows():
        key = row['File_name'] + row['LoaiBC']
        if key in dict_lookup:
            df_lookup_tmp = dict_lookup[row['File_name'] + row['LoaiBC']]

            res = get_parent_item(int(row['STT']), row['de_muc'], df_lookup_tmp)
            tmp_list.append(list(row) + [res['parent'], res['parent_name']])

    df = pd.DataFrame(tmp_list, columns=list(df.columns) + ['parent', 'parent_name'])


    df.to_excel('output.xlsx')


    # list_str = ['2_30_10 Lợi nhuận thuần từ hoạt động kinh doanh {30 = 20 + (21 - 22) - (24 + 25)}',
    #             '(2.11.30)10 Lợi nhuận thuần từ hoạt động kinh doanh {30 = 20 + (21 - 22) - (24 + 25)}',
    #             '2_23_  - Trong đó: Chi phí lãi vay',
    #             '(2.8.23)  - Trong đó: Chi phí lãi vay',
    #     'TEN_DN','1_200_TỔNG CỘNG TÀI SẢN (200=110+120+130+140+150+160+170+180)',
    #      '4_ _III. Lưu chuyển tiền từ hoạt động tài chính',
    #      '1_TS_TÀI SẢN',
    #      '1_141_  1. Hàng tồn kho',
    #      '(4.10. )II. Lưu chuyển tiền từ hoạt động đầu tư',
    #      '(5.4.03)- Khấu hao TSCĐ và BĐSĐT',
    #      '(2.19.70)18. Lãi cơ bản trên cổ phiếu (*)',
    #      '(1.109.421)11. Lợi nhuận sau thuế chưa phân phối (421 =421a + 421b)',
    #      '(1.95.400)D - VỐN CHỦ SỞ HỮU (400=410+430)',
    #      '(2.11.30)10. Lợi nhuận thuần từ hoạt động kinh doanh {30 = 20 + (21 - 22) - (25 + 26)}',
    #      '(1.20.200)B - TÀI SẢN DÀI HẠN (200=210+220+230+240+250+260)']

    # for s in list_str:
    #     s_dict = string_parse(s)
    #     print(f"{s} --------------------------------- Ma so: [{s_dict['ma_so']}]         De muc: [{s_dict['de_muc']}]   Ten Truong: [{s_dict['ten_truong']}]")



if __name__ == "__main__":
    
    main()
       