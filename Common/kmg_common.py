#!/usr/bin/python3
#-----------------------------------------------------------------------------
#   KMG Common             　　                             Create 2021.09
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
#   [logger function]
#   logger_init(i_logdir_path)                                          : logger設定処理
#   
#   [Ubuntu環境確認用関数]
#   get_pkglist()
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
import sys
import subprocess
import json
import shutil
import platform
from datetime import datetime
import logging
from logging import StreamHandler, FileHandler, Formatter
from logging import INFO, DEBUG, NOTSET
from argparse import ArgumentParser
from typing import Match
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom

from Common.kmg_subprocess import *

# -------------------------------------------------------------------------------------------
# 変数/定数　定義部 
# -------------------------------------------------------------------------------------------
# 実行環境ラベル
SYSTEM_LABEL_RASPI          = 1
SYSTEM_LABEL_JETSON         = 2
SYSTEM_LABEL_LINUX          = 3
SYSTEM_LABEL_LINUX_OTHER    = 4
SYSTEM_LABEL_WIN10          = 5
SYSTEM_LABEL_WIN_OTHER      = 6


# -------------------------------------------------------------------------------------------
# 関数定義部 
# -------------------------------------------------------------------------------------------

#---------------------------------------------
# logger function
#---------------------------------------------
def logger_init(i_logdir_path):
    # ロギングの設定（コンソールとログファイルの両方に出力する
    # --コンソール出力用ハンドラ
    p_stream_hundler = StreamHandler()
    p_stream_hundler.setLevel(INFO)
    p_stream_hundler.setFormatter(Formatter("%(message)s"))

    # --ログ出力用ライブラリの所在確認と作成
    if not os.path.isdir(i_logdir_path):
        os.makedirs(i_logdir_path, exist_ok = True)

    # --ファイル出力用ハンドラ
    p_file_handler = FileHandler(
        f"./Log/log{datetime.now():%Y%m%d%H%M%S}.log"
    )
    p_file_handler.setLevel(DEBUG)
    p_file_handler.setFormatter(
        Formatter("%(asctime)s@ %(name)s [%(levelname)s] %(funcName)s: %(message)s")
    )

    # --ルートロガーの設定
    logging.basicConfig(level=NOTSET, handlers=[p_stream_hundler, p_file_handler])

    o_logger = logging.getLogger(__name__)

    return o_logger
# End Function

#---------------------------------------------
# Ubuntu environment check function
#---------------------------------------------

# 実行環境のシステム判定処理
def check_system_env(logger):

    # システム環境の判別 Determining the system environment.
    logger.info('System Enviroment Check Process Begin')

    system_label = ''
    os_name = platform.system()
    logger.info('The operating system is [' + os_name + ']')
    if os_name == 'Linux':
        # Raspberry Pi / Jetson / other ( have device-tree/model )
        if os.path.exists('/proc/device-tree/model'):
            res = call_subprocess_run('cat /proc/device-tree/model', logger)
            os_info = res.__next__()
            if 'Raspberry Pi' in os_info:
                system_label = SYSTEM_LABEL_RASPI
                logger.info('The model name is [' + os_info + ']')
            elif 'NVIDIA Jetson' in os_info:
                system_label = SYSTEM_LABEL_JETSON
                logger.info('The model name is [' + os_info + ']')
            else:
                system_label = SYSTEM_LABEL_LINUX_OTHER
                logger.info('The model name is [' + os_info + ']')
        # Linux ( Not have device-tree/model )
        else:
            for product in read_data(get_system_data()):
                os_info = SYSTEM_LABEL_LINUX
            logger.error('The model name is [' + os_info + ']')

    elif os_name == 'Windows':
        systeminfo_l = win_call_subprocess_run('systeminfo', logger)
 
        systeminfo_dict = []
        for line in systeminfo_l:
            info_l = line.split(': ')
            for i in range(len(info_l)):
                info_l[i] = info_l[i].strip()
            systeminfo_dict.append(info_l)
        
        if 'Microsoft Windows 10' in systeminfo_dict[5][1]:
            system_label = SYSTEM_LABEL_WIN10
            logger.info('The model name is [' + systeminfo_dict[5][1] + ']')
        else:
            system_label = SYSTEM_LABEL_WIN_OTHER
            logger.info('The model name is [' + systeminfo_dict[5][1] + ']')

    return system_label
# End Function

# Ubuntuパッケージリスト取得処理（[0]パッケージ名、[1]バージョン、[2]アーキテクチャ)
def get_pkglist(logger):
    res = call_subprocess_run("dpkg-query -l | awk -F, '6<=NR' | awk '{print $2\",\"$3\",\"$4}'", logger)
    
    r_pkg_list = []

    for line in res:
        r_pkg_list.append(line.split(","))

    return r_pkg_list
# End Function

