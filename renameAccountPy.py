import os
import re

PrintOnly: bool = False

AccountList: list = ['30521900', '30521901', '30521902', '30521920', '30521970', '9009002000']
CreditCardList: list = ['30521961_Kreditkarte']

AccountBaseFolder: str = fr'/home/florian/99_Unterlagen/Kontoauszuege'

RegStringAccount: str = '(\d{4}-\d{2}-\d{2}_)(\d{3})(_\d*.pdf)'
RegStringCredidCard: str = '(\d{4}-\d{2}-\d{2}_)(\d*.pdf)'

for AccountFolder in AccountList:
    ActFolder: str = fr'{AccountBaseFolder}/{AccountFolder}'

    if os.path.exists(ActFolder):
        ExpressionList = re.findall(RegStringAccount, str(os.listdir(ActFolder)))

        for StringList in ExpressionList:
            cmd: str = fr'mv -vf {ActFolder}/{"".join(StringList)} {ActFolder}/{StringList[0]}N{StringList[1]}_Kontoauszug_{StringList[2]}'
            if PrintOnly:
                print(cmd)
            else:
                os.system(cmd)
    else:
        print(f'Folder {ActFolder} not found')

for CredidCardFolder in CreditCardList:
    ActFolder: str = fr'{AccountBaseFolder}/{CredidCardFolder}'

    if os.path.exists(ActFolder):
        ExpressionList = re.findall(RegStringCredidCard, str(os.listdir(ActFolder)))

        for StringList in ExpressionList:
            cmd: str = fr'mv -vf {ActFolder}/{"".join(StringList)} {ActFolder}/{StringList[0]}Kreditkarten-Umsatzaufstellung_{StringList[1]}'
            if PrintOnly:
                print(cmd)
            else:
                os.system(cmd)
    else:
        print(f'Folder {ActFolder} not found')