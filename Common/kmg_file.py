#!/usr/bin/python3
#-----------------------------------------------------------------------------
#   KMG file             　　                             Create 2021.09
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
#   [外部ファイル編集用関数]
#   update_file(file_d, original_d, after_d, logger)                    : 編集元文字列指定
#   update_file_firstline(file_d, original_d, after_d, logger)          : 先頭行追加
#   update_file_endline(file_d, original_d, after_d, logger)            : 最終行追加
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
import shutil
import csv

#---------------------------------------------
# file custom function
#---------------------------------------------
# 外部ファイルの新規作成処理
def create_file(i_file_d, i_after_d, logger):
    try:
        if not os.path.exists(i_file_d):
            logger.info('---- Create file ----')
            with open(i_file_d, "w") as fs:
                fs.write(i_after_d)
            logger.info('---- Success Create file ----')
            return 0
        else:
            logger.error("The specified file name already exists.")
            return 1
    except OSError as e:
        logger.error(e)
        return 1
# End Function

# 外部ファイルの更新処理[1]（指定行の更新）　Function for updating external files.
def update_file(i_file_d, i_original_d, i_after_d, i_bk_dirname, logger):
    try:
        #指定されたファイルパスを元に更新元ファイルをバックアップ
        p_dir_name = os.path.dirname(i_file_d)
        p_file_name = os.path.basename(i_file_d)
        p_mk_dir_name = os.path.join(p_dir_name + i_bk_dirname)
        p_bk_file_namepath = os.path.join(p_mk_dir_name, p_file_name)
        if not os.path.isdir(p_mk_dir_name):
          os.makedirs(p_mk_dir_name, exist_ok = True)
        shutil.copy2(i_file_d, p_bk_file_namepath)

        # 更新処理
        file_line = []
        logger.info('---- Scan file ----')
        with open(i_file_d, "r") as fs:
            for fsline in fs:
                if fsline.find(i_original_d) == 0:
                    file_line.append(i_after_d + '\n')
                else:
                    file_line.append(fsline)
        logger.info('---- Update file ----')
        with open(i_file_d, "w") as fs:
            for line in file_line:
                fs.write(line)
        logger.info('---- Success update file ----')
        return 0
    except OSError as e:
        logger.error(e)
        return 1

# 外部ファイルの更新処理[2]（先頭行追加）
def update_file_firstline(i_file_d, i_after_d, i_bk_dirname, logger):
    try:
        #指定されたファイルパスを元に更新元ファイルをバックアップ
        p_dir_name = os.path.dirname(i_file_d)
        p_file_name = os.path.basename(i_file_d)
        p_mk_dir_name = os.path.join(p_dir_name + i_bk_dirname)
        p_bk_file_namepath = os.path.join(p_mk_dir_name, p_file_name)
        if not os.path.isdir(p_mk_dir_name):
          os.makedirs(p_mk_dir_name, exist_ok = True)
        shutil.copy2(i_file_d, p_bk_file_namepath)

        # 更新処理
        file_line = []
        file_line.append(i_after_d + '\n')
        logger.info('---- Scan file ----')
        with open(i_file_d, "r") as fs:
            for fsline in fs:
                file_line.append(fsline)
        logger.info('---- Update file ----')
        with open(i_file_d, "w") as fs:
            for line in file_line:
                fs.write(line)
        logger.info('---- Success update file ----')
        return 0
    except OSError as e:
        logger.error(e)
        return 1


# 外部ファイルの更新処理[3]（末尾追記）　Function for updating external files.
def update_file_endline(i_file_d, i_after_d, i_bk_dirname, logger):
    try:
        #指定されたファイルパスを元に更新元ファイルをバックアップ
        p_dir_name = os.path.dirname(i_file_d)
        p_file_name = os.path.basename(i_file_d)
        p_mk_dir_name = os.path.join(p_dir_name + i_bk_dirname)
        p_bk_file_namepath = os.path.join(p_mk_dir_name, p_file_name)
        if not os.path.isdir(p_mk_dir_name):
          os.makedirs(p_mk_dir_name, exist_ok = True)
        shutil.copy2(i_file_d, p_bk_file_namepath)

        logger.info('---- Update file ----')
        with open(i_file_d, "a") as fs:
            fs.write('\n' + i_after_d + '\n')
        logger.info('---- Success update file ----')
        return 0
    except OSError as e:
        logger.error(e)
        return 1

# 外部ファイルの更新処理[4]（ファイル　有：全上書き、無：新規作成）
# 指定名のファイルが存在する場合は、バックアップを取得して更新
def update_file_full(i_file_d, i_after_d, i_bk_dirname, logger):
    try:
        # 指定名のファイルがない場合
        if not os.path.exists(i_file_d):
            logger.info('---- Create file ----')
            with open(i_file_d, "w") as fs:
                fs.write(i_after_d + '\n')
            logger.info('---- Success Create file ----')
            return 0
        # 指定名のファイルがある場合
        else:
            #指定されたファイルパスを元に更新元ファイルをバックアップ
            p_dir_name = os.path.dirname(i_file_d)
            p_file_name = os.path.basename(i_file_d)
            p_mk_dir_name = os.path.join(p_dir_name, i_bk_dirname)
            p_bk_file_namepath = os.path.join(p_mk_dir_name, p_file_name)
            if not os.path.isdir(p_mk_dir_name):
                os.makedirs(p_mk_dir_name, exist_ok = True)
            shutil.copy2(i_file_d, p_bk_file_namepath)

            # 指定名のファイルに上書き
            logger.info('---- Update file ----')
            with open(i_file_d, "w") as fs:
                fs.write(i_after_d)
            logger.info('---- Success Update file ----')

    except OSError as e:
        logger.error(e)
        return 1
# End Function