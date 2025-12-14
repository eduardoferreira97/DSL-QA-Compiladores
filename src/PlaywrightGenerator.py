from TestScriptVisitor import TestScriptVisitor

class PlaywrightGenerator(TestScriptVisitor):
    def __init__(self):
        self.tests_code = []   # funções test_*
        self.test_names = []   # nomes dos testes

    # =========================
    # Geração do arquivo final
    # =========================
    def generate(self):
        header = [
            "import sys",
            "import os",
            "from playwright.sync_api import sync_playwright",
            "",
        ]

        runner_start = [
            "def run_tests(test_to_run=None):",
            "    TRACE_FILE = 'trace.zip'",
            "    if os.path.exists(TRACE_FILE):",
            "        os.remove(TRACE_FILE)",
            "",
            "    with sync_playwright() as p:",
            "        browser = p.chromium.launch(headless=True)",
            "        context = browser.new_context()",       
            "        page = context.new_page()",
            "        try:",
            "",
        ]

        runner_calls = []
        for name in self.test_names:
            runner_calls += [
                f"            if test_to_run in (None, '{name}'):",
                f"                context.tracing.start(screenshots=True, snapshots=True, sources=True)",
                f"                test_{name}(page)",
                f"                context.tracing.stop(path='trace.zip')",
                "",
            ]

        #runner_end = [
        #    "        finally:",
        #    "            context.tracing.stop(path='trace.zip')",
        #    "            browser.close()",
        #    "",
        #]

        runner_end = [
            "        finally:",
            "            browser.close()",
            "",
        ]

        main = [
            "if __name__ == '__main__':",
            "    if len(sys.argv) == 1:",
            "        print('Uso: python saida_playwright.py <nome_do_teste> | all')",
            "        sys.exit()",
            "",
            "    arg = sys.argv[1]",
            "    run_tests(arg if arg != 'all' else None)",
        ]

        return "\n".join(
            header +
            self.tests_code +
            runner_start +
            runner_calls +
            runner_end +
            main
        )
    
    # =========================
    # Blocos de teste
    # =========================
    def visitTestBlock(self, ctx):
        name = ctx.IDENT().getText()
        self.test_names.append(name)

        self.tests_code.append(f"def test_{name}(page):")

        #if name == "formulario":
            #self.tests_code.append("    page.fill('#userEmail', 'teste@teste.com')")
            #self.tests_code.append("    page.fill('#userNumber', '81999999999')")

        self.visit(ctx.commandBlock())
        self.tests_code.append("")
        return None

    # =========================
    # Comandos da DSL
    # =========================
    def visitOpenCmd(self, ctx):
        self.tests_code.append(
            f"    page.goto({ctx.STRING().getText()}, wait_until='domcontentloaded')"
        )

    #def visitTypeCmd(self, ctx):
        #sel = ctx.STRING(0).getText()
        #txt = ctx.STRING(1).getText()
        #self.tests_code.append(f"    page.fill({sel}, {txt})")

    def visitTypeCmd(self, ctx):
        sel = ctx.STRING(0).getText()
        txt = ctx.STRING(1).getText()
        self.tests_code.append(f"    page.wait_for_selector({sel}, state='visible', timeout=10000)")
        self.tests_code.append(f"    page.fill({sel}, {txt})")


    def visitClickCmd(self, ctx):
        sel = ctx.STRING().getText()
        self.tests_code.append(f"    page.click({sel})")

    def visitSubmitCmd(self, ctx):
        sel = ctx.STRING().getText()

        self.tests_code.append(f"    page.wait_for_selector({sel}, state='visible', timeout=10000)")
        self.tests_code.append(f"    page.click({sel})")

        self.tests_code.append(
            "    page.wait_for_selector('#example-modal-sizes-title-lg', state='visible', timeout=10000)"
        )

    def visitUploadCmd(self, ctx):
        sel = ctx.STRING(0).getText()
        file = ctx.STRING(1).getText()
        self.tests_code.append(f"    page.set_input_files({sel}, {file})")

    def visitWaitCmd(self, ctx):
        sel = ctx.STRING().getText()
        t = int(ctx.INT().getText())
        self.tests_code.append(f"    page.wait_for_selector({sel}, timeout={t})")

    def visitWaitVisibleCmd(self, ctx):
        sel = ctx.STRING().getText()
        t = int(ctx.INT().getText())
        self.tests_code.append(
            f"    page.wait_for_selector({sel}, state='visible', timeout={t})"
        )

    def visitExpectCmd(self, ctx):
        txt = ctx.STRING().getText()
        self.tests_code.append("    page.wait_for_timeout(500)")
        self.tests_code.append(f"    assert {txt} in page.content()")

    def visitPauseCmd(self, ctx):
        seconds = int(ctx.INT().getText())
        self.tests_code.append(f"    page.wait_for_timeout({seconds * 1000})")

    def visitScrollCmd(self, ctx):
        direction = ctx.STRING().getText().strip('"')
        if direction == "down":
            self.tests_code.append("    page.evaluate('window.scrollBy(0, 600)')")
        else:
            self.tests_code.append("    page.evaluate('window.scrollBy(0, -600)')")
