#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree
import re
import os
import sys
from unicode_map import unicode_map

def mathml2latex(mathml_block):
    # Preprocess to remove aliases
    mathml_block = mathml_block.replace('<<', '&lt;<').replace('>>', '>&gt;')
    # MathML to LaTeX conversion with XSLT from Vasil Yaroshevich
    script_base_path = os.path.dirname(os.path.realpath(__file__))
    xslt_file = os.path.join(script_base_path, 'mmltex', 'mmltex.xsl')
    dom = etree.fromstring(mathml_block)
    xslt = etree.parse(xslt_file)
    transform = etree.XSLT(xslt)
    newdom = transform(dom)
    return newdom

def unicode2latex(latex_block):
    latex_text = str(latex_block, 'utf-8').encode('ascii', 'backslashreplace')
    for utf_code, latex_code in unicode_map.items():
        latex_text = str(latex_text).replace(utf_code, latex_code)
    latex_text = latex_text.replace('\\\\', '\\')
    latex_text = re.sub(r'\\textcolor\[rgb\]\{[0-9.,]+\}', '', latex_text)
    latex_text = latex_text.replace('\\ ~\\ ', '\\sim')
    latex_text = latex_text[len('b\''):][:-len('\'')]
    latex_text = re.sub(r'^\$ ', '$', latex_text)
    latex_text = re.sub(r' \}', '}', latex_text)
    latex_text = latex_text.replace('\\n\\[\\n\\t', '$$').replace('\\n\\]', '$$')
    latex_text = latex_text.replace('\\left', '').replace('\\right', '')
    return latex_text

def convert(text):
    mathml_blocks = re.findall(r"<!--\[if mathML\]>(.*?)<!\[endif\]-->", text)
    for mathml_block in mathml_blocks:
        latex_block = mathml2latex(mathml_block)
        latex_text = unicode2latex(latex_block)
        text = text.replace('<!--[if mathML]>' + mathml_block + '<![endif]-->', latex_text)
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
