# =================================================
#  Flexible 4D simulation system for Archicad（仮）
#  ver.Beta1 2023/06/04
# =================================================

import os
import sys
import subprocess
import xml.etree.ElementTree as ET
import configparser
import shutil
import glob

def get_dir_path(filename):
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)
    print(datadir)
    return datadir

# ファイルパスを見つける。HsfとConvertedフォルダを空にして再生成
def find_folder_path(ini,currentpath):
    converterPath = ini['converterPath']['Path']
    srcDir = currentpath + "/Binary"
    outDir = currentpath + "/Hsf"
    cnvDir = currentpath + "/Converted"
    
    shutil.rmtree(outDir)
    os.mkdir(outDir)

    shutil.rmtree(cnvDir)
    os.mkdir(cnvDir)


    tmps = glob.glob(srcDir + "/*.gsm")
    gsmfiles =[]
    cnt = 0
    for gsmfile in tmps:
        gs = os.path.basename(gsmfile)
        gsmfiles.append(gs)
        cnt = cnt + 1
    return converterPath , srcDir , outDir , cnvDir , gsmfiles ,cnt

def find_file_path(cnt,outDir,gsmfiles):
    gsmfile = os.path.splitext(gsmfiles[cnt])[0]

    ParamFile = outDir + "/" + gsmfile + "/paramlist.xml"
    ThreeDFile = outDir + "/" + gsmfile + "/scripts/3d.gdl"
    LibpartdataFile = outDir + "/" + gsmfile + "/libpartdata.xml"
    ScriptDir = outDir + "/" + gsmfile + "/scripts"
    return gsmfile , ParamFile , ThreeDFile , LibpartdataFile , ScriptDir


# [ini] ファイル名からマスタスクリプトに書き込むためのインデックスを取得
def filename_to_index(ini,gsmfile):
    FileNameToRange = {}
    for i in range(10):
        tmp = ini["ファイル名連動"][str(i+1)]
        FileNameToRange[tmp] = i+1

    FileRange = 0
    for key in FileNameToRange:
        if key in gsmfile:
            FileRange = FileNameToRange[key]
    return FileRange

# libpartdataを書き換える
def rewrite_libpartdata(LibpartdataFile):
    tree = ET.parse(LibpartdataFile)
    root = tree.getroot()

    Script_1D = ET.SubElement(root, 'Script_1D')
    Script_1D.attrib["SectVersion"] = "20"
    Script_1D.attrib["SectionFlags"] = "0"
    Script_1D.attrib["SubIdent"] = "0"

    tree.write(LibpartdataFile,encoding="UTF-8")

# パラメータ（上の）書き換え。MaterialComb[変数名] = マテリアルインデックス
def rewrite_paramlist(ParamFile):
    tree = ET.parse(ParamFile)
    root = tree.getroot()

    ## materialの変数名：マテリアルインデックスの辞書
    MaterialComb = dict()
    tmp1 = ""
    tmp2 = 0
    for parameters in root:
        for parameter in parameters:
            if parameter.tag == "Material":
                tmp1 = parameter.attrib["Name"]
                for i in parameter:
                    if i.tag == "Value":
                        tmp2 = int(i.text)
                MaterialComb[tmp1] = tmp2


    ## WireSolid変数を追記
    DescTmpText = "\"\""

    for parameters in root.findall('Parameters'):
        Boolean = ET.SubElement(parameters, 'Boolean')
        Boolean.attrib["Name"] = "WireSolid"
        Description = ET.SubElement(Boolean, 'Description')
        #Cdata = ET.SubElement(Description,'![CDATA[\"\"]]')
        Description.text = DescTmpText
        ArrayValues = ET.SubElement(Boolean, 'ArrayValues')
        cnt = 0
        for i in MaterialComb:
            AVal = ET.SubElement(ArrayValues, 'AVal')
            AVal.attrib["Row"] = str(cnt+1)
            AVal.text = "1"
            cnt = cnt + 1
        ArrayValues.attrib["FirstDimension"] = str(cnt)
        ArrayValues.attrib["SecondDimension"] = "0"

        Boolean = ET.SubElement(parameters, 'Boolean')
        Boolean.attrib["Name"] = "isMVO"
        Description = ET.SubElement(Boolean, 'Description')
        Description.text = DescTmpText
        Value = ET.SubElement(Boolean, 'Value')
        Value.text = "1"

    tree.write(ParamFile,encoding="UTF-8")

    ### CDATAの記述がXMLでは出来ない？のでテキストとして処理
    ### CDATAが無いとHSFtoGSM変換がエラー
    with open(ParamFile, encoding="utf_8_sig", newline='') as f:
        data_lines = f.read()

    #### 文字列置換
    data_lines = data_lines.replace("<Description>", "<Description><![CDATA[")
    data_lines = data_lines.replace("</Description>", "]]></Description>")

    #### 同じファイル名で保存
    with open(ParamFile, mode="w", encoding="utf_8_sig", newline='') as f:
        f.write(data_lines)

    return MaterialComb

# 3Dスクリプトの書き換え
def rewrite_3d(ini,ThreeDFile,MaterialComb):
    WStextF = " : if WireSolid["
    WStextR = "] then MODEL SOLID else MODEL WIRE"

    ## 設定ini読み込み
    CombMaterial = {}

    for i in range(99):
        if ini['範囲No. = 材質インデックス'][str(i+1)] != "":
            CombMaterial[int(ini['範囲No. = 材質インデックス'][str(i+1)])] = i+1

    ## material表記のある行にWireSolidを追記
    with open(ThreeDFile, encoding="utf_8_sig", newline='') as f:
        data_lines = f.read()

    WSkey = 1
    for key in MaterialComb:
        WSkey = CombMaterial[MaterialComb[key]]
        before = "material " + key
        after = before + WStextF + str(WSkey) + WStextR
        data_lines = data_lines.replace(before, after)

    with open(ThreeDFile, mode="w", encoding="utf_8_sig", newline='') as f:
        f.write(data_lines)

# 1d(Master)を生成
def criate_1d(ScriptDir,FileRange):
    shutil.copyfile("1d.gdl", ScriptDir + "/1d.gdl")
    with open(ScriptDir + "/1d.gdl", encoding="utf_8_sig", newline='') as f:
        data_lines = f.read()

    before = "showStepIDtmp"
    after = "showStepID" + str(FileRange)
    data_lines = data_lines.replace(before, after)

    with open(ScriptDir + "/1d.gdl", mode="w", encoding="utf_8_sig", newline='') as f:
        f.write(data_lines)




# ini読み込み
ini = configparser.ConfigParser()
ini.read('config.ini', 'UTF-8')

cnt = 0

currentpath = get_dir_path(sys.argv[0])
# ファイル検索
converterPath , srcDir , outDir , cnvDir , gsmfiles, BinaryDirNum = find_folder_path(ini,currentpath)

# GSM to HSF
command = "l2hsf"
result = subprocess.run([converterPath, command, srcDir, outDir])


# BinaryDirNum = sum(os.path.isfile(os.path.join(srcDir,name)) for name in os.listdir(srcDir))

for cnt in range(BinaryDirNum):
    gsmfile , ParamFile , ThreeDFile , LibpartdataFile , ScriptDir = find_file_path(cnt,outDir,gsmfiles)
    # iniファイル連動
    FileRange = filename_to_index(ini,gsmfile)

    # libpartdata処理
    success = rewrite_libpartdata(LibpartdataFile)

    # パラメータスクリプト処理
    MaterialComb = rewrite_paramlist(ParamFile)

    # 3DにWIRE / SOLID変換を追記
    success = rewrite_3d(ini,ThreeDFile,MaterialComb)

    # 1d(Master)ファイルの生成
    success = criate_1d(ScriptDir,FileRange)

# HSF to GSM
command = "hsf2l"
result = subprocess.run([converterPath, command, outDir, cnvDir])

os.system('PAUSE')