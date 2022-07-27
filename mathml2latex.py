#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
from lxml import etree
from unicode_map import unicode_map

# MathML to LaTeX conversion with XSLT from Vasil Yaroshevich
base_path = os.path.dirname(os.path.realpath(__file__))
xslt_file = os.path.join(base_path, 'mmltex', 'mmltex.xsl')
xslt = etree.parse(xslt_file)
transform = etree.XSLT(xslt)

def mathml2latex(mathml_block):
    # Preprocess to remove aliases
    mathml_block = mathml_block.replace('<<', '&lt;<').replace('>>', '>&gt;')
    dom = etree.fromstring(mathml_block)
    return transform(dom)

def unicode2latex(latex_block):
    latex_text = str(latex_block, 'utf-8').encode('ascii', 'backslashreplace')
    for utf_code, latex_code in unicode_map.items():
        latex_text = str(latex_text).replace(utf_code, latex_code)
    latex_text = latex_text.replace('\\\\', '\\')                          # "\\" --> "\"
    latex_text = re.sub(r'\\textcolor\[rgb\]\{[0-9.,]+\}', '', latex_text) # "\textcolor[rgb]{...}" --> ""
    latex_text = latex_text.replace('\\ ~\\ ', '{\\sim}')                  # " ~ " --> "{\sim}"
    latex_text = latex_text[len('b\''):][:-len('\'')]                      # b'...' --> ...
    latex_text = re.sub(r'^\$ ', '$', latex_text)                          # "$ " --> "$"
    latex_text = latex_text.replace('{\\ }', '\\ ')                        # "{ }" --> " "
    latex_text = re.sub(r' \}', '}', latex_text)                           # " }" --> "}"
    latex_text = latex_text.replace('\\n\\[\\n\\t', '$$').replace('\\n\\]', '$$')
    return latex_text

def convert(text):
    mathml_blocks = re.findall(r"<!--\[if mathML\]>(.*?)<!\[endif\]-->", text)
    for mathml_block in mathml_blocks:
        latex_block = mathml2latex(mathml_block)
        latex_text = unicode2latex(latex_block)
        text = text.replace('<!--[if mathML]>' + mathml_block + '<![endif]-->', latex_text)
    # Remove multiple consecutive blank lines
    for _ in range(2):
        text = re.sub(r'\n\n', '\n', text)
    return text

def main():
    input_file = open(sys.argv[1], "r", encoding="utf-8")
    input = input_file.read()
    input_file.close()
    output = convert(input)
    output_file = open(sys.argv[2], "w", encoding="utf-8")
    output_file.write(output)
    output_file.close()

if __name__ == "__main__":
    main()
