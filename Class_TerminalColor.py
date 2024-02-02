class TerminalColor:
    # Colors
    __DEFAULT: str = '\033[0m'
    __RED: str = '\033[31m'
    __BLUE: str = '\033[94m'
    __GREEN: str = '\033[92m'
    __YELLOW: str = '\033[93m'
    __CYAN: str = '\033[96m'
    __PURPLE: str = '\033[95m'
    # Decoration
    __BOLD: str = '\033[1m'
    __UNDERLINE: str = '\033[4m'

    # to set
    __WARNING: str
    __ERROR: str
    __INFO: str

    def __init__(self, *, info: str = '\033{94m', warning: str = '\033[93m', error: str = '\033[96m'):
        self.warning = warning
        self.error = error
        self.info = info
        pass

    def __repr__(self):
        return f'TerminalColor(info=\'{self.info}\',warning=\'{self.warning}\',error=\'{self.error}\')'

    def __str__(self):
        return self.default()

    @staticmethod
    def colored_string(color: str, text: str) -> str:
        return f'{color}{text}{TerminalColor.default()}'

    @property
    def warning(self) -> str:
        return self.__WARNING

    @warning.setter
    def warning(self, value: str):
        self.__WARNING = value

    @property
    def error(self) -> str:
        return self.__ERROR

    @error.setter
    def error(self, value: str):
        self.__ERROR = value

    @property
    def info(self) -> str:
        return self.__INFO

    @error.setter
    def info(self, value: str):
        self.__INFO = value

    @staticmethod
    def default() -> str:
        return TerminalColor.__DEFAULT

    @staticmethod
    def color_green() -> str:
        return TerminalColor.__GREEN

    @staticmethod
    def color_purple() -> str:
        return TerminalColor.__PURPLE

    @staticmethod
    def decor_underline() -> str:
        return TerminalColor.__UNDERLINE

    @staticmethod
    def decor_bold() -> str:
        return TerminalColor.__BOLD

    @staticmethod
    def color_blue() -> str:
        return TerminalColor.__BLUE

    @staticmethod
    def color_yellow() -> str:
        return TerminalColor.__YELLOW

    @staticmethod
    def color_red() -> str:
        return TerminalColor.__RED
