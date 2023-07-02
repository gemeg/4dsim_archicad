# Flexible 4D simulation system for Archicad（仮） 

Archicad上で4Dシミュレーションを行うにあたり、GSMファイルを書き換える。

# DEMO

https://youtu.be/JjVQ9UvnnPM

# Features

* MVO（モデル表示オプション）に連動し、工区の境もスパンの1/4程度のところで分割して表現できています。
* 工区の境にある要素は「分割」ツールなどで分割されているわけではないため、あとから工区割や躯体形状が変わっても対応できます。
* SCP(smartCON Planner)で作成した足場も分割可能です。
また、通常の手法だと表現しづらい掘削のようなマイナスに進んでいく要素にも対応しています。
* 概要説明記事→https://zenn.dev/cote2/articles/e4b16d1d22f20a

# Requirement

* configparser 5.3.0

# Installation

Requirementで列挙したライブラリなどのインストール方法を説明する

```bash
pip install configparser
```

# Usage

BinaryフォルダにGSMファイルを保存しFlex4dsim.pyを実行する。
正常動作すればConvertedフォルダに変換された同名のGSMファイルが生成される。

# Note

* Archicad25 6000 JPN で動作確認しています。
* たぶん26でも動作します。
* 本プログラムを使用したことにより利用者に生じた損害について、いかなる責任も負わないものとし、損害賠償義務も一切負わないものとします。

# Author

* Kotetsu
* gemegemeg333@gmail.com

# License
"Flexible 4D simulation system for Archicad（仮） " is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
  