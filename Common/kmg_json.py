#!/usr/bin/python3
#-----------------------------------------------------------------------------
#   KMG JSON             　　                             Create 2021.09
#    
#   共通関数を定義したファイルです。他のプログラムから呼び出して使用します。   
#
#   Author  : GENROKU@Karakuri-musha
#   License : See the license file for the license.
#   
#   [変数記名規則]
#   i_ : 関数の引数
#   p_ : 関数内でのみ使用
#   o_ : 関数の戻り値
#
#   --------------------------------------------------------------------------
#   収録関数
#   --------------------------------------------------------------------------
#   [jsonファイル利用関数]
#   read_json_entry(dir_path, p_input_file_name)                        : jsonファイルの読み込み（To Dict)
#   read_json_dict_entry(p_json_data_dict:dict, p_dict_entry_name:str)  : jsonデータエントリの読み出し（From Dict）
#   
#
#   Author  : GENROKU@Karakuri-musha
#   License : See the license file for the license.
#       
#-----------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------
# ライブラリインポート部 
# -------------------------------------------------------------------------------------------
import os
import json

#---------------------------------------------
# json function
#---------------------------------------------
# json read to dict
def read_json_entry(dir_path, p_input_file_name):

    # jsonファイルを開く
    json_file_path = os.path.join(dir_path, p_input_file_name)
    json_open = open(json_file_path, 'r', encoding="utf-8")
    p_json_data_dict = json.load(json_open)

    return p_json_data_dict
# End Function

# Read dict(from json) 
def read_json_dict_entry(p_json_data_dict:dict, p_dict_entry_name:str):
    p_entry_data = p_json_data_dict.get(p_dict_entry_name, "")
    
    return p_entry_data
# End Function
