from lelouch import Logger

class MockPrinter():
    last_message: str

    def __call__(self, message):
        self.last_message = message

def test_print():
    printer = MockPrinter()
    log = Logger(printer=printer)
    log.print("test")
    assert printer.last_message == "test"

def test_info():
    printer = MockPrinter()
    log = Logger(printer=printer)
    log.info("test")
    assert printer.last_message == "\033[90minfo: test\033[0m"

def test_info_no_color():
    printer = MockPrinter()
    log = Logger(use_color=False, printer=printer)
    log.info("test")
    assert printer.last_message == "info: test"

def test_reason():
    printer = MockPrinter()
    log = Logger(printer=printer)
    log.reason("test")
    assert printer.last_message == "\033[90mreasoning: test\033[0m"

def test_reason_no_color():
    printer = MockPrinter()
    log = Logger(use_color=False, printer=printer)
    log.reason("test")
    assert printer.last_message == "reasoning: test"

def test_warn():
    printer = MockPrinter()
    log = Logger(printer=printer)
    log.warn("test")
    assert printer.last_message == "\033[33mwarning: test\033[0m"

def test_warn_no_color():
    printer = MockPrinter()
    log = Logger(use_color=False, printer=printer)
    log.warn("test")
    assert printer.last_message == "warning: test"
