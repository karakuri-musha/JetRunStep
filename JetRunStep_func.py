#!/usr/bin/python3
#-----------------------------------------------------------------------------
#   JetRunStep Function      　　                             Create 2021.09
#    
#   JetRunStepツールで使用する独自関数を定義したファイルです。
#   ツールのメインプログラムから呼び出して使用します。   
#
#   Author  : GENROKU@Karakuri-musha
#   License : See the license file for the license.
#   
#   [記名規則]
#   i_ : 関数の引数
#   p_ : 関数内でのみ使用
#   o_ : 関数の戻り値
#
#   --------------------------------------------------------------------------
#   収録関数
#   --------------------------------------------------------------------------
#   get_option():                                                                                       :ツール実行時オプションの設定
#   read_parameters(i_input_file_name):                                                                 :動作パラメータの取得（jsonファイルからの読み出し）
#   prettify(i_elem):                                                                                   :XML判読化
#   create_xml(i_pkg_list, i_xml_file_d, logger):                                                       :管理用XML生成（初期化）
#   update_xml(i_xml_file_d, i_new_pkg_list, cmd_str, logger):                                          :管理用XML更新
#   create_xml_view(i_xml_view_file_name, i_xml_trace_file, i_xml_bk_dir, logger):                      :判読化済みXMLファイル生成
#   create_html(i_xml_file_path, i_html_file_path, logger):                                             :HTMLファイル生成
#   run_one_cmd(i_cmd_string, i_env_t_int, i_xml_path, logger):                                         :コマンド単体実行処理
#   run_auto_setup(i_env_t_int, i_dir_path, i_json_name, i_xml_path, logger):                           :Auto Setup実行処理（パラメータ設定）
#   iterate_env_setting(i_res_status, i_type_d, i_comment_d, i_cmd_d, logger, i_original_d = '', i_after_d = ''):   :Auto Setuo実行処理（実行）
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
from datetime import datetime
from logging import INFO, DEBUG, NOTSET
from argparse import ArgumentParser
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom

# 共通関数の呼び出し
from Common.kmg_common import *
from Common.kmg_json import *
from Common.kmg_file import *
from Common.kmg_subprocess import *


# -------------------------------------------------------------------------------------------
# 変数/定数　定義部 
# -------------------------------------------------------------------------------------------
MSG_OPTIONS_HELP_INSTALL    = "Specify when executing by specifying a command. Specifies the command to execute."
MSG_OPTIONS_HELP_AUTOINS    = "Specify when performing automatic installation. Specify the installation command definition file."
MSG_OPTIONS_HELP_SETUP      = "Specify the operation setting file (json)."
SETTING_FILE_NAME           = "JetRunStepSetting.json"

XML_ROOTENTITY_NAME = "Pkglist"
XML_MGMENTITY_NAME  = "Package"
XML_MGMENTITY_ATTR1 = "name"
XML_MGMENTITY_ATTR2 = "flg"
XML_ITEM_NAME       = "Trace"
XML_ITEM_ATTR       = "order"
XML_ITEM_VERSION    = "Versions"
XML_ITEM_DATE       = "Updatedate"
XML_ITEM_REASON     = "Reasonforup"

# ----------------------------------------------------------
# 関数定義部
# ----------------------------------------------------------
# 実行時オプションの構成
def get_option():
    o_argparser = ArgumentParser()
    o_argparser.add_argument("-i", "--Install", default="1", help=MSG_OPTIONS_HELP_INSTALL)
    o_argparser.add_argument("-a", "--AutoInstall", default="1", help=MSG_OPTIONS_HELP_AUTOINS)
    o_argparser.add_argument("-s", "--json", default=SETTING_FILE_NAME, help=MSG_OPTIONS_HELP_SETUP)
    o_argparser.add_argument("-v", "--XMLViewFile", default="1", help=MSG_OPTIONS_HELP_SETUP)
    return o_argparser.parse_args()
# End Function

# 実行環境のカレントパス取得処理
def get_current_path():
    if getattr(sys, 'frozen', False):
        os_current_path = os.path.dirname(os.path.abspath(sys.executable))
    else:
        os_current_path = os.path.dirname(os.path.abspath(__file__))
    dir_path = os_current_path

    return dir_path
# End Function


# 動作パラメータの取得（jsonファイルからの読み出し）
def read_parameters(i_dir_path, i_input_file_name):

    # jsonファイルを開く
    p_json_data_dict = read_json_entry(i_dir_path, i_input_file_name)

    o_run_env       = read_json_dict_entry(p_json_data_dict,'run_env')
    o_env_t_int     = read_json_dict_entry(p_json_data_dict,'env_trace_interval')
    o_env_t_out_d   = read_json_dict_entry(p_json_data_dict,'env_trace_output_dir')
    o_env_t_xml_f   = read_json_dict_entry(p_json_data_dict,'env_trace_xml_file')
    o_env_b_f       = read_json_dict_entry(p_json_data_dict,'env_browse_file')
    o_env_l_pkg_f   = read_json_dict_entry(p_json_data_dict,'env_latest_pkg_file') 
    o_max_log_cnt   = read_json_dict_entry(p_json_data_dict,'max_log_cnt')
  
    return o_run_env, o_env_t_int, o_env_t_out_d, o_env_t_xml_f, o_env_b_f, o_env_l_pkg_f, o_max_log_cnt
# End Function

#---------------------------------------------
# XML function
#---------------------------------------------
# XML成型用関数
def prettify(i_elem):
    p_rough_string = ElementTree.tostring(i_elem, 'utf-8')
    o_reparsed = minidom.parseString(p_rough_string)
    return o_reparsed.toprettyxml(indent="  ")
# End Function

# XML構造生成処理（初回実行時）
# XMLファイルが存在しない場合に実行する処理（XML構造を持ったリストを返す）
def create_xml(i_pkg_list, i_xml_file_d, logger):
    
    logger.info("The environment configuration check (init) will start.")

    # XMLファイルのヘッダ作成
    xml_root = Element(XML_ROOTENTITY_NAME)
    comment = Comment('Generated for JetRunSetup by GENROKU@Karakuri-Musha')
    xml_root.append(comment)

    # 各パッケージの情報をXML構造化する
    for i in range(len(i_pkg_list)):
        xml_pkg = SubElement(xml_root, XML_MGMENTITY_NAME)
        xml_pkg.set(XML_MGMENTITY_ATTR1, i_pkg_list[i][0])
        xml_pkg.set(XML_MGMENTITY_ATTR2, "1")
        xml_item = SubElement(xml_pkg, XML_ITEM_NAME)
        xml_item.set(XML_ITEM_ATTR, "0")
        xml_ver = SubElement(xml_item, XML_ITEM_VERSION)
        xml_ver.text = i_pkg_list[i][1]
        xml_date = SubElement(xml_item, XML_ITEM_DATE)
        xml_date.text = f"{datetime.now():%Y.%m.%d}"
        xml_reason = SubElement(xml_item, XML_ITEM_REASON)
        xml_reason.text = "Initial creation"

    p_elemtree = ElementTree.ElementTree()
    p_elemtree._setroot(xml_root)
    p_elemtree.write(i_xml_file_d, encoding="utf-8", xml_declaration=None, method="xml")

    logger.info("The environment configuration check (init) is complete.")
# End Function

# XMLファイル更新処理
# 指定のXMLファイルに対して新しいバージョンを追加する処理
def update_xml(i_xml_file_d, i_new_pkg_list, cmd_str, logger):
    
    logger.info("The environment configuration check will start.")

    # XMLファイルの読み込み
    xml_tree = ElementTree.parse(i_xml_file_d)

    # 更新内容格納用リストの生成
    o_update_list = []

    # ルート要素の取得
    xml_root = xml_tree.getroot()

    # XML構造体の更新フラグを"0"にする
    for child in xml_root.iter(XML_MGMENTITY_NAME):
        child.set(XML_MGMENTITY_ATTR2, '0')

    for i in range(len(i_new_pkg_list)):
        
        pkg_n = i_new_pkg_list[i][0]    # 最新環境パッケージ名の格納
        pkg_v = i_new_pkg_list[i][1]    # 最新環境バージョンの格納

        # XMLデータから対象のパッケージの最終更新情報を取得
        q_str = "./" + XML_MGMENTITY_NAME + "[@" + XML_MGMENTITY_ATTR1 + "=" + "\'" + pkg_n + "\'" + "]/" + XML_ITEM_NAME + "[@" + XML_ITEM_ATTR + "]"
        res_find = xml_tree.findall(q_str)

        # 環境にパッケージが新しく追加された場合
        if len(res_find) == 0:
            Add_pack_ent = SubElement(xml_root, XML_MGMENTITY_NAME)
            Add_pack_ent.set(XML_MGMENTITY_ATTR1, pkg_n)
            Add_pack_ent.set(XML_MGMENTITY_ATTR2, "1")
            Add_mgm_ent = SubElement(Add_pack_ent, XML_ITEM_NAME)
            Add_mgm_ent.set(XML_ITEM_ATTR, str(0))
            Add_xml_ver = SubElement(Add_mgm_ent, XML_ITEM_VERSION)
            Add_xml_ver.text = pkg_v
            Add_xml_date = SubElement(Add_mgm_ent, XML_ITEM_DATE)
            Add_xml_date.text = f"{datetime.now():%Y.%m.%d}"
            Add_xml_reason = SubElement(Add_mgm_ent, XML_ITEM_REASON)
            Add_xml_reason.text = cmd_str
       
        # 環境にパッケージが既に存在する場合
        else:
            cnt = "0"
            for elem in res_find:
                cnt = elem.attrib[XML_ITEM_ATTR]
        
            # 対象パッケージの最終バージョンの取得
            q_str = "./" + XML_MGMENTITY_NAME + "[@" + XML_MGMENTITY_ATTR1 + "=" + "\'" + pkg_n + "\'" + "]/" + XML_ITEM_NAME + "[@" + XML_ITEM_ATTR + "=\'" + cnt + "\']/" + XML_ITEM_VERSION
            least_v = xml_tree.find(q_str).text

            # バージョンに変更がない場合は何もしない
            if pkg_v == least_v:
                q_str = "./" + XML_MGMENTITY_NAME + "[@" + XML_MGMENTITY_ATTR1 + "=" + "\'" + pkg_n + "\']" 
                res_pkg = xml_tree.findall(q_str)
                for elem in res_pkg:
                    elem.set(XML_MGMENTITY_ATTR2, '1')

            # バージョンに変更がある場合、タグを追加
            else:
                o_update_list.append(pkg_n + " : " + least_v + " -> " + pkg_v + "\n")
                q_str = "./" + XML_MGMENTITY_NAME + "[@" + XML_MGMENTITY_ATTR1 + "=" + "\'" + pkg_n + "\']"
                for a_elem in xml_tree.findall(q_str):
                    elem.set(XML_MGMENTITY_ATTR2, '1')
                    Add_mgm_ent = SubElement(a_elem, XML_ITEM_NAME)
                    Add_mgm_ent.set(XML_ITEM_ATTR, str(int(cnt) + 1))
                    Add_xml_ver = SubElement(Add_mgm_ent, XML_ITEM_VERSION)
                    Add_xml_ver.text = pkg_v
                    Add_xml_date = SubElement(Add_mgm_ent, XML_ITEM_DATE)
                    Add_xml_date.text = f"{datetime.now():%Y.%m.%d}"
                    Add_xml_reason = SubElement(Add_mgm_ent, XML_ITEM_REASON)
                    Add_xml_reason.text = cmd_str

    q_str = "./" + XML_MGMENTITY_NAME + "[@" + XML_MGMENTITY_ATTR2 + "=" + "\'0\'" + "]" 
    res = xml_tree.findall(q_str)
    if len(res) is not 0:
        for elem in res:
            xml_root.remove(elem)

    xml_tree.write(i_xml_file_d, encoding="utf-8", xml_declaration=None, method="xml")

    logger.info("The environment configuration check is complete.")

    return o_update_list
# End Function

def create_xml_view(i_xml_view_file_name, i_xml_trace_file, i_xml_bk_dir, logger):

    logger.info("Start generating XML file for reference.")

    # XMLファイルの読み込み
    xml_tree = ElementTree.parse(i_xml_trace_file)

    # ルート要素の取得
    xml_root = xml_tree.getroot()

    # インデントの付与
    p_output = prettify(xml_root)

    # ファイル保存
    update_file_full(i_xml_view_file_name, p_output, i_xml_bk_dir, logger)
    logger.info("Complete generating XML file for reference.")
# End Function

# HTML（親属性）生成
def create_html(i_xml_file_path, i_html_file_path, i_xml_bk_dir, logger):
    logger.info("Start HTML file generation.")

    p_html_str_list = []

    # 固定表記部分の生成
    p_html_str_list.append('<!DOCTYPE HTML>')
    p_html_str_list.append('<html lang=\"ja\" class=\"pc\">')
    p_html_str_list.append('<head>')
    p_html_str_list.append('<meta charset="UTF-8">')
    p_html_str_list.append('<title>Package environment update history for Ubuntu</title>')
    p_html_str_list.append('<link rel=\"stylesheet\" type=\"text/css\" href=\"js/JetRunStep.css\">')
    p_html_str_list.append('<script src=\"js/jquery-3.6.0.min.js\"></script>')
    p_html_str_list.append('</head>')
    p_html_str_list.append('<body>')
    p_html_str_list.append('<b style=\"font-size: 20pt;\">Package environment update history for Ubuntu</b><br />')
    p_html_str_list.append('<a style=\"float: right;\">Generated in '+ f"{datetime.now():%Y.%m.%d}" + '</a><br />')
    p_html_str_list.append('<a style=\"float: right;\">JetRunStep Tool: genroku @ Karakuri-Musha</a>')
    p_html_str_list.append('<div id=\'Title\'></div>')
    p_html_str_list.append('<table class=\'package-list\'>')
    p_html_str_list.append('<thead>')
    p_html_str_list.append('<tr>')
    p_html_str_list.append('<th class=\"pkg-n\">Package Name</th>')
    p_html_str_list.append('<th class=\"pkg-v\">Version</th>')
    p_html_str_list.append('<th class=\"plg-ud\">least Update Date</th>')
    p_html_str_list.append('<th class=\"show-hide\">Show/<br />Hide</th>')
    p_html_str_list.append('<th class=\"up-his\">Update History</th>')
    p_html_str_list.append('</tr>')
    p_html_str_list.append('</thead>')
    p_html_str_list.append('<tbody>')

    # XMLファイルからの要素の取得とHTMLの生成
    xml_tree = ElementTree.parse(i_xml_file_path)
    xml_root = xml_tree.getroot()
    for child in xml_root:
        p_pkg_name = child.attrib['name']

        p_html_str_list.append('<tr>')
        p_html_str_list.append('<td>' + p_pkg_name + '</td>')

        cnt = 0
        least_cnt = str(len(child))
        for e in reversed(child):
            p_pkg_v = e[0].text
            p_pkg_update = e[1].text
            p_pkg_note = e[2].text

            if cnt == 0:
                p_html_str_list.append('<td>' + p_pkg_v + '</td>')
                p_html_str_list.append('<td>' + p_pkg_update + '</td>')
                p_html_str_list.append('<td><a href=\"#\" class=\"open\">+</a><a href=\"#\" class=\"close\">-</a></td>')
                p_html_str_list.append('<td>' + least_cnt + '<br />')
                p_html_str_list.append('<dl class=\"versions\">')
            
            p_html_str_list.append('<dt>' + p_pkg_v + ' </dt><dd>&lt;--' + p_pkg_update + ' [' + p_pkg_note + ']</dd>')
            cnt = cnt + 1

        p_html_str_list.append('</dl>')
        p_html_str_list.append('</td>')
        p_html_str_list.append('</tr>')
    
    p_html_str_list.append('</tbody>')
    p_html_str_list.append('</table>')
    p_html_str_list.append('<script src=\"js/JetRunStep.js\"></script>')
    p_html_str_list.append('</body>')
    p_html_str_list.append('</html>')

    logger.info("End HTML file generation.")

    p_join_str = "".join(p_html_str_list)
    update_file_full(i_html_file_path, p_join_str, i_xml_bk_dir, logger)
# End Function

#---------------------------------------------
# One Command Execute function
#---------------------------------------------
# 単体コマンドの実行と環境変更情報の生成
def run_one_cmd(i_cmd_string, i_env_t_int, i_xml_path, logger):
    
    if i_env_t_int in {"All", "Once"}:
        res = call_subprocess_run(i_cmd_string, logger)
        for line in res:
            logger.info(line)

        o_pkg_list = get_pkglist(logger)

        if os.path.exists(i_xml_path):
            o_update_list = update_xml(i_xml_path, o_pkg_list, i_cmd_string, logger)

            if len(o_update_list) is not 0:
                for line in o_update_list:
                    logger.info(line)
        else:
            create_xml(o_pkg_list, i_xml_path, logger)
            logger.info("Since this tool was executed for the first time, an administrative file (Env_trace.xml) was created.")
            o_update_list = []

    return o_update_list, o_pkg_list
# End Function

#---------------------------------------------
# Auto Setup Execute function
#---------------------------------------------
# インストールコマンド定義ファイルをもとにした自動インストール処理
def run_auto_setup(i_env_t_int, i_dir_path, i_json_name, i_xml_path, i_bk_dirname, logger):
    res_status = 0

    p_json_read = read_json_entry(i_dir_path,i_json_name)
    logger.info('Setup will start. The environment is Jetson and the file name is [' + i_json_name + ']')


    # Auto Setup 定義ファイル内のコマンドリストの順次実行
    for json_s in p_json_read:
        p_type_d = json_s.get('type', '')
        p_comment_d = json_s.get('comment', '')
        p_cmd_d = json_s.get('cmd', '')
        p_original_d = json_s.get('original', '')
        p_after_d = json_s.get('after', '')

        logger.info('The following command is being executed. [' + p_cmd_d + ']')
        res_status = iterate_env_setting(res_status, p_type_d, p_comment_d, p_cmd_d, i_bk_dirname, logger, p_original_d, p_after_d)

        # Auto Setup 内のコマンド実行毎にパッケージ更新情報を生成
        if i_env_t_int == "All":

            o_pkg_list = get_pkglist(logger)

            if os.path.exists(i_xml_path):
                o_update_list = update_xml(i_xml_path, o_pkg_list, p_cmd_d, logger)

                if len(o_update_list) is not 0:
                    for line in o_update_list:
                        logger.info(line)
            else:
                create_xml(o_pkg_list, i_xml_path, logger)
                logger.info("Since this tool was executed for the first time, an administrative file (Env_trace.xml) was created.")

    if i_env_t_int == "Once":
        o_pkg_list = get_pkglist(logger)

        if os.path.exists(i_xml_path):
            o_update_list = update_xml(i_xml_path, o_pkg_list, p_cmd_d, logger)

            if len(o_update_list) is not 0:
                for line in o_update_list:
                    logger.info(line)
            else:
                create_xml(o_pkg_list, i_xml_path)
                logger.info("Since this tool was executed for the first time, an administrative file (Env_trace.xml) was created.")

    return o_update_list, o_pkg_list
# End Function

#---------------------------------------------
# Auto Install function
#---------------------------------------------
# 実行処理と結果対処　Execution processing and result handling functions.
def iterate_env_setting(i_res_status, i_type_d, i_comment_d, i_cmd_d, i_bk_dirname, logger, i_original_d = '', i_after_d = ''):
    logger.info(i_comment_d)

    if i_type_d == 'cmd':
        res = call_subprocess_run(i_cmd_d, logger)
        for cnt in res:
            if 'Failed to execute' in cnt:
                logger.error(cnt)
                i_res_status = 1 
                break
            else:
                logger.info(cnt)
    
    elif i_type_d == 'frc':
        i_res_status = update_file(i_cmd_d, i_original_d, i_after_d, i_bk_dirname, logger)

    elif i_type_d == 'ffc':
        i_res_status = update_file_firstline(i_cmd_d, i_after_d, i_bk_dirname, logger)

    elif i_type_d == 'fec':
        i_res_status = update_file_endline(i_cmd_d, i_after_d, i_bk_dirname, logger)

    return i_res_status
# End Function

