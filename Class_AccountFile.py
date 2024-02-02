import os
import re
import logging

from enum import Enum

from Class_TerminalColor import TerminalColor


class FileType(Enum):
    NotDefined = 0
    AccountFile = 1
    CreditCardFile = 2


# FileType = Enum('FileType', 'AccountFile CredidCardFile')

class AccountFile:
    _type: FileType

    __regular_expression: str

    __has_number: bool
    __is_valid: bool

    __day: str
    __month: str
    __year: str

    _text: str
    _account_no: str
    _statement_no: str

    _folder: str
    __input_file: str
    _output_file: str

    def __init__(self, file_name: str):
        # set regular expression
        self.__regular_expression = '(?:(.*)_(\d*)_(Nr\.)(\d*)|(.*)_(\d*))_(.*)_vom_(\d*)\.(\d*)\.(\d*)'
        # init variables
        self.__init_vars()
        # run startup
        self.__scan_file(file_name)
        pass

    def __repr__(self):
        return f'konto_file(\'{self.__input_file}\')'

    def __str__(self):
        return self.__return_str(fr'[{self._type.value}] ./{self._folder}/{self._output_file}')

    @property
    def date(self) -> str:
        return self.get_date()

    def get_date(self, *, iso: bool = True) -> str:
        if iso:
            return self.__return_str(f'{self.__year}-{self.__month}-{self.__day}')
        else:
            return self.__return_str(f'{self.__year}-{self.__month}-{self.__day}')

    #def get_account_no(self) -> str:
    @property
    def account(self) -> str:
        return self.__return_str(self._account_no)

    #def get_statement_no(self) -> str:
    @property
    def statement_no(self) -> str:
        return self.__return_str(self._statement_no)

    #def get_input_file(self) -> str:
    @property
    def input_file(self) -> str:
        return self.__return_str(self.__input_file)

    #def get_output_file(self) -> str:
    @property
    def output_file(self) -> str:
        return self.__return_str(self._output_file)

    #def get_folder_name(self) -> str:
    @property
    def folder_name(self) -> str:
        return self._folder

    def get_destination(self, path='.') -> str:
        if not path.endswith(r'/'):
            path += r'/'
        return fr'{path}{self._folder}/{self._output_file}'

    #def get_type(self) -> FileType:
    @property
    def type(self) -> FileType:
        return self._type

    def is_valid(self) -> bool:
        return self.__is_valid

    def debug_output(self, log: logging.Logger, *, debug_color: str = TerminalColor.color_purple(),
                     error_color: str = TerminalColor.color_red()):
        if self.is_valid():
            # debug output
            log.debug('')
            log.debug(TerminalColor.colored_string(debug_color, 'Found the following elements in filename:'))
            log.debug(TerminalColor.colored_string(debug_color, f'Day:           {self.__day}'))
            log.debug(TerminalColor.colored_string(debug_color, f'Month:         {self.__month}'))
            log.debug(TerminalColor.colored_string(debug_color, f'Year:          {self.__year}'))
            log.debug(TerminalColor.colored_string(debug_color, f'Account No.:   {self._account_no}'))
            log.debug(TerminalColor.colored_string(debug_color, f'Statement No.: {self._statement_no}'))
            log.debug(TerminalColor.colored_string(debug_color, f'Text:          {self._text}'))
            log.debug('')
            log.debug(TerminalColor.colored_string(debug_color, f'input file:      {self.__input_file}'))
            log.debug(TerminalColor.colored_string(debug_color, f'output file:      {self._output_file}'))
            log.debug('')
            log.debug(TerminalColor.colored_string(debug_color, f'type:          {self._type}'))
            log.debug(TerminalColor.colored_string(debug_color, f'folder:        {self._folder}'))
        else:
            log.error('')
            log.error(TerminalColor.colored_string(error_color, 'Object is not defined'))
        pass

    def __return_str(self, string) -> str:
        if not self.is_valid():
            #  None
            return 'Unkown Type'
        else:
            return string

    def __init_vars(self):
        # init all necessary variables
        self.__input_file = 'None'
        self._output_file = 'None'

        self.__has_number = False
        self.__is_valid = False
        self._type = FileType.NotDefined
        # add 2021-04-15
        self.__day = '01'
        self.__month = '01'
        self.__year = '1970'

        self._text = 'Info'
        self._account_no = '00000000'
        self._statement_no = '000'

        self._folder = 'None'
        pass

    def __scan_file(self, file_name: str):
        self.__input_file = os.path.basename(file_name)

        # Generate regular expression
        expression_list = re.findall(self.__regular_expression, self.__input_file)
        # Check if
        if len(expression_list) == 1:
            str_list = expression_list[0]
            
            # Get dates from regular expression
            # Check date for iso
            if len(str_list[7]) > 2:
                # iso
                self.__day = str_list[9]
                self.__month = str_list[8]
                self.__year = str_list[7]
            else:
                # de
                self.__day = str_list[7]
                self.__month = str_list[8]
                self.__year = str_list[9]
            # Set text and replace spaces
            self._text = str_list[6].replace(' ','_')

            # Check if file has konto number
            if str_list[0] != '':
                self._account_no = str_list[0]
                self._statement_no = str_list[3]
                # Generate new file name
                self._output_file = f'{self.__year}-{self.__month}-{self.__day}_N{self._statement_no}_{self._text}_{self._account_no}.pdf'
            else:
                self._account_no = str_list[4]
                self._statement_no = '<no number>'
                # Generate new file name
                self._output_file = f'{self.__year}-{self.__month}-{self.__day}_{self._text}_{self._account_no}.pdf'

            # Set folder
            self._folder = self._account_no

            # Set filetype
            self._type = FileType.AccountFile

            # Set class ist valid
            self.__is_valid = True
        else:
            # Set class is invlid
            self.__is_valid = False
        pass


class CreditCardFile(AccountFile):
    __cc_accout_no: str
    __cc_folder: str
    __delimeter: str

    def __init__(self, file_name: str, cc_accounts: list, cc_folder_names: list = [], delimeter: str = '_'):
        self.__delimeter = delimeter
        self.__cc_accout_no = 'xxxxxxxxxxxxxxxx'
        self.__cc_folder = '<creaditcard>'

        AccountFile.__init__(self, file_name)

        self.__check_credit_card(cc_accounts, cc_folder_names)
        pass

    def __repr__(self):
        return f'CreditCardFile({self.input_file}, [{self.__cc_accout_no}], [{self.__cc_folder}])'

    def __check_credit_card(self, cc_accounts: list, cc_folder_names: list):
        # Check if file is valid and account no is decimal
        if self.is_valid():
            for i in range(0, len(cc_accounts)):
                if self._account_no[-3:] == str(cc_accounts[i])[-3:]:
                    # Set filetype
                    self._type = FileType.CreditCardFile
                    # set new account no
                    self._account_no = str(cc_accounts[i])
                    self.__cc_accout_no = str(cc_accounts[i])
                    # check if len is the same if not do not use account name
                    if len(cc_accounts) == len(cc_folder_names):
                        self._folder = str(cc_folder_names[i])
                    else:
                        self._folder = self._account_no
                    # check if there is a number in the name
                    if self.statement_no.isdecimal():
                        self._output_file = f'{self.get_date()}_N{self._statement_no}_{self._text}_{self._account_no}.pdf'
                    else:
                        self._output_file = f'{self.get_date()}_{self._text}_{self._account_no}.pdf'
    pass
