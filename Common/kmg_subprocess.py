#!/usr/bin/python3
#-----------------------------------------------------------------------------
#   KMG Subprocess             　　                             Create 2021.09
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
#   [Subprocess function]
#   win_call_subprocess_run(origin_cmd, logger)                         : Windows向け外部コマンド実行処理関数
#   call_subprocess_run(origin_cmd, logger)                             : Linux向け外部コマンド実行処理関数(1)
#   call_subprocess_run_sudo(origin_cmd, p_passphrase, logger)          : Linux向け外部コマンド実行処理関数(2)
#   get_system_data(p_passphrase)                                       : Linux実行環境確認関数（1）
#   read_data(proc_output)                                              : Linux実行環境確認関数（2）
#   
#
#   Author  : GENROKU@Karakuri-musha
#   License : See the license file for the license.
#       
#-----------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------
# ライブラリインポート部 
# -------------------------------------------------------------------------------------------
import sys
import subprocess
import json

#---------------------------------------------
# Subprocess function
#---------------------------------------------
# Windows向け　外部コマンドの実行処理用の関数　Function for executing external commands.
# Windowsはロケールによってコマンドプロンプトの言語設定が違うため、英語出力に変更して出力する
def win_call_subprocess_run(origin_cmd, logger):
    try:
        # コマンドプロンプトの言語コードを確認し、変数chcp_originに格納
        pre_p = subprocess.Popen("chcp",
                            shell=True,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            ) 
        chcp_res, _ = pre_p.communicate()
        chcp_origin = chcp_res.split(':')

        # コマンドプロンプト起動時に言語コードを英語に変更して起動し、systeminfoを実行
        res = subprocess.Popen("cmd.exe /k \"chcp 437\"",
                            shell=True,
                            stdin=subprocess.PIPE, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            ) 
        res.stdin.write(origin_cmd + "\n")
        stdout_t, _ = res.communicate()

        # コマンドプロンプトの言語コードをorigin_chcpに戻す
        cmd = "chcp " + str(chcp_origin[1])
        after_p = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            ) 
        after_res, _ = after_p.communicate()
  
        for line in stdout_t.splitlines():
            yield line

    except subprocess.CalledProcessError:
        logger.error('Failed to execute the external command.[' + origin_cmd + ']', file = sys.stderr)
        sys.exit(1)
# End Function

# Linux/Raspberry Pi OS用の外部コマンド実行関数(1)
# 通常外部コマンドの実行処理用の関数　Function for executing external commands.
def call_subprocess_run(origin_cmd, logger):
    try:
        res = subprocess.run(origin_cmd, 
                            shell=True, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            )
        for line in res.stdout.splitlines():
            yield line
    except subprocess.CalledProcessError:
        logger.error('Failed to execute the external command.[' + origin_cmd + ']', file = sys.stderr)
        sys.exit(1)
# End Function

# Linux/Raspberry Pi OS用の外部コマンド実行関数(2)
# Sudo系コマンドの実行処理用の関数　Function for executing external commands.
def call_subprocess_run_sudo(origin_cmd, p_passphrase, logger):
    try:
        res = subprocess.run(origin_cmd, 
                            shell=True, 
                            check=True,
                            input=p_passphrase + '\n',
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                            )
        for line in res.stdout.splitlines():
            yield line
    except subprocess.CalledProcessError:
        logger.error('Failed to execute the external command.[' + origin_cmd + ']', file = sys.stderr)
        sys.exit(1)
# End Function

# システム情報の取得
# Rassbery PiとJetson以外のLinuxで実行された場合に実行環境を取得するための処理
def get_system_data(p_passphrase):
    lshw_cmd = ['sudo', 'lshw', '-json']
    proc = subprocess.Popen(lshw_cmd, 
                            stdin=p_passphrase + '/n',
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return proc.communicate()[0]
# End Function

# Rassbery PiとJetson以外のLinuxで実行された場合に実行環境を読み込むための処理
def read_data(proc_output):
    proc_result = []
    proc_json = json.loads(proc_output)
    for entry in proc_json:
        proc_result.append(entry.get('product', ''))
    return proc_result
# End Function