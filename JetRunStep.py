#!/usr/bin/python3
#-----------------------------------------------------------------------------
#   Jetson Nano Run Step cmd Tool (JetRunStep)              　　Create 2021.09
#    
#   このツールは、Jetson Nanoの環境の更新履歴をトレースできる情報を管理するツールです。
# 　Ubuntuにおいてインストールコマンドなどを実行する際に、このコマンドを通して実行する
# 　ことで、下記の管理情報をもとに環境更新履歴を生成します。
# 　また、あらかじめ定義しておいた、インストールコマンド定義ファイル（.json形式）を使い
# 　複数パッケージのインストール処理などを自動で実行することができます。
#   ツールの動作条件は、JetRunStepSetting.jsonファイルで指定できます。
#
#   環境変更履歴は以下のコマンドで得られる情報をもとに生成します。
#   【管理情報】
#     インストールパッケージ情報　（dpkg-query -l)
#
#   オプション指定
#     -i [Install]          : コマンドを指定して実行する場合に指定します。実行するコマンドを指定します。
#     -a [auto Install]     : 自動インストールを行う場合に指定します。インストールコマンド定義ファイルを指定します。
#     -s [Setup file name]  : 動作設定用ファイル（json）を指定します。
#
#   処理結果出力　
#   　出力：環境変更履歴は、ツール実行フォルダの配下に「env_files」フォルダを生成し
# 　　　　　出力されます。出力されるファイルは以下の構成です。
#           (1) Env_trace.xml       : 変更履歴のXML形式出力
#           (2) Env_trace_view.xml  : 変更履歴のXML形式出力（参照用）
#           (3) Env_browse.html     : 変更履歴のHtml形式出力
#           (4) Env_latest_pack     : 最新のパッケージ構成情報
#          
# 　　ログ：ツール実行フォルダの配下に「Log」というフォルダを作成し出力されます。
# 　　　　　ログファイルは指定したファイル数に達すると古いものから削除されます。
#
#   Author  : GENROKU@Karakuri-musha
#   License : See the license file for the license.
#       
#-----------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------
# ライブラリインポート部 
# -------------------------------------------------------------------------------------------
import sys
import csv

# 共通関数の呼び出し
from Common.kmg_common import *
from Common.kmg_json import *
from Common.kmg_file import *
from Common.kmg_subprocess import *

# ツール独自関数の呼び出し
from JetRunStep_func import *

SETTING_LOG_DIR     = "./Log"
SETTING_BK_DIR      = "xml_bk"


MSG_TOOL_RUN                = "Start the Jetson Nano Run Setup Tool (JetRunStep) ."
MSG_TOOL_END                = "Exit the Jetson Nano Run Setup Tool (JetRunStep) "
MSG_TOOL_ENV_ERROR          = "This tool is not available in your environment."
MSG_TOOL_OPTION_ERROR       = "The specified parameter is incorrect. To display the help, execute it with the -h option."

# -----------------------------------------------------------------------------
# main処理（main.pyが起動された場合に処理される内容）
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    # loggerの初期化
    logger = logger_init(SETTING_LOG_DIR)

    # カレントディレクトリの取得
    dir_path = get_current_path()

    # システム環境の判別 Determining the system environment.
    system_label = check_system_env(logger)

    # 指定されたオプションの確認
    args = get_option()
    cmd_run_flg         = args.Install          # 実行コマンド
    auto_install_flg    = args.AutoInstall      # Auto Install 定義ファイル
    input_file_name     = args.json             # 動作設定用ファイル
    xml_view_file_name  = args.XMLViewFile      # 参照用XMLファイル

    # ツールの動作設定ファイルの読み込み
    p_run_env, p_env_t_int, p_env_t_out_d, p_env_t_xml_f, p_env_b_f, p_env_l_pkg_f, p_max_log_cnt = read_parameters(dir_path, input_file_name)

    # ---------------------------------------------------------------
    # Delete Old Log file  
    # ---------------------------------------------------------------
    files = os.listdir(SETTING_LOG_DIR)             # ディレクトリ内のファイルリストを取得
    if len(files) >= int(p_max_log_cnt) + 1:
        del_files = len(files)-int(p_max_log_cnt)
        files.sort()                                # ファイルリストを昇順に並び替え
        for i in range(del_files):
            del_file_name = os.path.join(SETTING_LOG_DIR, files[i])
            logger.info("delete log file : " + del_file_name)
            os.remove(del_file_name)                 # 一番古いファイル名から削除

    # ファイルパスの生成
    p_env_xml_f_p   = os.path.join(p_env_t_out_d, p_env_t_xml_f)
    p_html_f_p      = os.path.join(p_env_t_out_d, p_env_b_f)
    p_pl_f_p        = os.path.join(p_env_t_out_d, p_env_l_pkg_f)
    p_ai_f_p        = os.path.join(dir_path, auto_install_flg)

    # 実行されたシステムと動作設定ファイルで指定された環境の比較
    if system_label == int(p_run_env):

        logger.info(MSG_TOOL_RUN)

        # コマンド指定オプションが指定され、コマンドが入力された場合
        if cmd_run_flg is not "1":
            # コマンド実行と変更履歴生成
            p_update_list, p_pkg_list = run_one_cmd(cmd_run_flg, p_env_t_int, p_env_xml_f_p, logger)

            # 各出力ファイルの生成
            # 1-xml
            if xml_view_file_name is not "1":
                create_xml_view(xml_view_file_name, p_env_xml_f_p, SETTING_BK_DIR, logger)
            # 2-html
            create_html(p_env_xml_f_p, p_html_f_p, SETTING_BK_DIR, logger)

        # AutoInstall指定オプションが指定され、定義ファイルが指定された場合
        else:
            if auto_install_flg is not "1":
                # 実行コマンドリストの読み込み　Reading the execution command list (things_to_do.json).
                p_update_list, p_pkg_list = run_auto_setup(p_env_t_int, p_env_t_out_d, p_ai_f_p, p_env_xml_f_p, SETTING_BK_DIR, logger)
            
                # 各出力ファイルの生成
                # 1-xml
                if xml_view_file_name is not "1":
                    create_xml_view(xml_view_file_name, p_env_xml_f_p, SETTING_BK_DIR, logger)
                # 2-html
                create_html(p_env_xml_f_p, p_html_f_p, SETTING_BK_DIR, logger)

            else:
                logger.error(MSG_TOOL_OPTION_ERROR)

    else:
        logger.error(MSG_TOOL_ENV_ERROR)
        sys.exit()
# End Function