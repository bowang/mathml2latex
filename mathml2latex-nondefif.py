
import re
import os
import sys
from lxml import etree
from unicode_map import unicode_map

# MathML to LaTeX conversion with XSLT from Vasil Yaroshevich
base_path = os.path.dirname(os.path.realpath(__file__))
xslt_file = os.path.join(base_path, "mmltex", "mmltex.xsl")
xslt = etree.parse(xslt_file)
transform = etree.XSLT(xslt)


def mathml2latex(mathml_block):
    # Preprocess to remove aliases
    mathml_block = mathml_block.replace("<<", "&lt;<").replace(">>", ">&gt;")
    dom = etree.fromstring(mathml_block)
    return transform(dom)


def unicode2latex(latex_block):
    latex_text = str(latex_block, "utf-8").encode("ascii", "backslashreplace")
    for utf_code, latex_code in unicode_map.items():
        latex_text = str(latex_text).replace(utf_code, latex_code)
    latex_text = latex_text.replace("\\\\", "\\")  # "\\" --> "\"
    latex_text = re.sub(
        r"\\textcolor\[rgb\]\{[0-9.,]+\}", "", latex_text
    )  # "\textcolor[rgb]{...}" --> ""
    latex_text = latex_text.replace("\\ ~\\ ", "{\\sim}")  # " ~ " --> "{\sim}"
    latex_text = latex_text[len("b'") :][: -len("'")]  # b'...' --> ...
    latex_text = re.sub(r"^\$ ", "$", latex_text)  # "$ " --> "$"
    latex_text = latex_text.replace("{\\ }", "\\ ")  # "{ }" --> " "
    latex_text = re.sub(r" \}", "}", latex_text)  # " }" --> "}"
    latex_text = latex_text.replace("\\n\\[\\n\\t", "$$").replace("\\n\\]", "$$")
    return latex_text


def convert(text):
    # 修改正则表达式以匹配 <mml:math> 开头的 MathML 代码段
    mathml_blocks = re.findall(r"<mml:math.*?</mml:math>", text, re.DOTALL)
    for mathml_block in mathml_blocks:
        latex_block = mathml2latex(mathml_block)
        latex_text = unicode2latex(latex_block)
        text = text.replace(mathml_block, latex_text)
    # Remove multiple consecutive blank lines
    for _ in range(2):
        text = re.sub(r"\n\n", "\n", text)
    return text


def main():
    input_file_path = "./Design_EN.md"
    output_file_path = "./test.md"

    # Open the input file and read its contents
    with open(input_file_path, "r", encoding="utf-8") as input_file:
        input_content = input_file.read()

    # Convert the content
    output_content = convert(input_content)

    # Write the converted content to the output file
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(output_content)


if __name__ == "__main__":
    main()
