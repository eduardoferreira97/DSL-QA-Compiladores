from antlr4 import *
from TestScriptLexer import TestScriptLexer
from TestScriptParser import TestScriptParser
from PlaywrightGenerator import PlaywrightGenerator

import os

def test_script(dsl_path):
    dsl_path = os.path.abspath(dsl_path)

    input_stream = FileStream(dsl_path, encoding="utf-8")
    lexer = TestScriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = TestScriptParser(tokens)

    tree = parser.script()

    generator = PlaywrightGenerator()
    generator.visit(tree)
    code = generator.generate() 

    out_file = os.path.join(os.path.dirname(__file__), "saida_playwright.py")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"Código Playwright gerado em: {out_file}")

if __name__ == "__main__":
    test_script("../tests/tests.dsl")
