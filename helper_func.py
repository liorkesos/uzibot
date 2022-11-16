import pymongo
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import os
from os import listdir
import shutil
import pandas as pd
import xlrd
import xlsxwriter

import lib

path1 = "/home/hadio/PycharmProjects/uzi_accountent/pdfs"
name_list = ["ksp", "work plus", "hadio", "liram"]

def get_all_pdfs(path):
    file_list = os.listdir(path)
    return file_list


def pdf_to_img(pdf_path, name):
    images = convert_from_path(pdf_path)

    dir_name = lib.temp_path + name
    os.mkdir(dir_name)
    save_path = dir_name + "/page"

    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save(save_path + str(i) + '.jpg', 'JPEG')
        break
    return dir_name



def erase_dir(path):
    print("erasing - " + path)
    shutil.rmtree(path)

def img_to_str(dir_name,lang):
    dir = listdir(dir_name)
    data_list = []
    for i in dir:
        path = dir_name + "/" + i
        data = pytesseract.image_to_string(Image.open(path), lang=lang)
        data_list.append(data)

    return data_list


def scan_pdf(data, delimiter,lang):
    dict_name = delimiter + "_" + lang

    check_list = []
    name = []
    bn = []
    description = []
    price = []
    receipt = []
    date = []

    if delimiter == "":
        data_one = data.split()
    else:
        data_one = data.split(delimiter)

    for i in data_one:
        if i in check_list:
            continue
        check_list.append(i)
        i = i.replace("\n", " ")
        i = i.replace("|", "")
        if len(i) > 2:
            if i.isnumeric() and i[0] == "5":
                if i[1] != "0":
                    bn.append(i)
        no_space = i.replace(" ", "")
        if no_space.isalpha() and len(no_space) > 10:
            description.append(i)
        elif no_space.isalpha() and 6<len(no_space)<12:
            name.append(i)

        if "." in i and i[0] != "0":
            temp = i.replace(".", "")
            temp = temp.replace(",", "")
            try:
                temp = int(temp)
                price.append(i)
            except:
                pass

        if i.isnumeric() and 4 < len(i) < 8:
            receipt.append(i)
        if "/" in i:
            temp = i.replace("/", "")
            if temp.isnumeric():
                date.append(i)

    data_dict = {"name":name,"bn": bn, "description": description, "price": price, "receipt": receipt, "date": date}
    data_dict = {dict_name: data_dict}
    return data_dict


def start_db(name):
    dbpath = "mongodb://localhost:27017/"
    myclient = pymongo.MongoClient(dbpath)
    mydb = myclient["heshbotnit_database"]
    mycol = mydb[name]
    return mycol


def db_query(cmd, data):
    mycol = start_db("heshbotnit")
    if cmd == "clients":
        return_list = []
        for i in mycol.find():
            if "client" in i.keys():
                return_list.append(i[data])
        return return_list
    elif cmd == "insert":
        mycol.insert_one(data)


def fix_info(info_list,cmd):
    check_list = []
    return_list = []
    for dict in info_list:
        if len(dict["info"]) != 0:
            if type(dict["info"]) == str:
                delimiter = dict["delimiter"]+"_"+str(dict["index"])
                temp_dict = {"delimiter":delimiter,"info":dict["info"],"type":cmd}
                return_list.append(temp_dict)
                continue
            for i in dict["info"]:
                if i not in check_list:
                    index = dict["info"].index(i)
                    delimiter = dict["delimiter"]+"_"+str(index)
                    temp_dict = {"delimiter": delimiter, "info": i,"type":cmd}
                    return_list.append(temp_dict)
                    check_list.append(i)

    return return_list


def get_info(info_list, cmd):
    temp_list = []
    print(info_list)
    print(cmd)
    if cmd == "name" or cmd == "description":
        file_name = info_list.pop(-1)
        name_index = file_name.index(".")
        name_by_file = file_name[:name_index]
        temp_dict = {"delimiter": "name by file", "info": name_by_file, "index": name_index}
        temp_list.append(temp_dict)
    return_list = []
    for dict in info_list:
        info_dict = list(dict.values())[0]
        delimiter = list(dict.keys())[0]
        temp_dict = {"delimiter": delimiter}
        info = info_dict[cmd]
        temp_dict["info"] = info
        temp_list.append(temp_dict)
    new_info_list = fix_info(temp_list,cmd)

    return new_info_list


def handler(date_dict):
    return_list = []
    dir_name = pdf_to_img(date_dict["path"], date_dict["name"])
    for lang in lib.lang_list:
        data_list = img_to_str(dir_name,lang)
        for data in data_list:
            for delimiter in lib.delimiter_list:
                info_dict = scan_pdf(data, delimiter, lang)
                return_list.append(info_dict)
    erase_dir(dir_name)
    return return_list


def test_db():
    temp_list = [{"client": "db", "name": "first", "5": "6"}, {"client": "db", "name": "second", "1": "2"}]
    for i in temp_list:
        db_query("insert", i)

    db_query("clients", 123)

def xlsx_to_list(path):
    workbook = xlrd.open_workbook_xls(path, ignore_workbook_corruption=True)
    data = pd.read_excel(workbook,sheet_name="קודים הוצאות")
    temp_list = data.values.tolist()
    return_dict = {}
    for i in temp_list:
        return_dict[i[1]] = i[0]
    print(return_dict)


def get_answer(item_list,delimiter):
    for item in item_list:
        if item["delimiter"] == delimiter:
            return item["info"]


def fix_for_buttons(type,item_list):
    codes_dict = lib.codes_dict
    temp_list = []
    return_list = []
    counter = 0
    for key,value in codes_dict.items():

        temp_list.append(key)
        temp_list.append(value)
        if len(temp_list) == 6:
            return_list.append(temp_list)
            temp_list=[]
    if len(temp_list) != 0:
        return_list.append(temp_list)
    return return_list

