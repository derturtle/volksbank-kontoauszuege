#! /usr/bin/python3
#
# Script runs over Kontoauszuege
#
import os
import re
import sys
import glob
import logging
import subprocess

import Class_AccountFile as CAF
from Class_TerminalColor import TerminalColor as CTC


# Globale configuration
class __Config:
    # 1. Account - Config
    # Account numbers start with
    accounts = [
        '305219',
        '9009002000',
    ]
    # 2. Credit card config
    # Credit card account no
    cc_account = [
        '457038xxxxxx4148',
        '548699xxxxxx2155'
    ]
    # Credit card folder supplement
    cc_storage = [
        'Visa_4570_38xx_xxxx_4148',
        'MasterCard_5486_99xx_xxxx_2155'
    ]

    # 3. Folder
    # for linux expand home folder
    home: str = os.path.expanduser('~')
    # Source folder - input folder
    source: str = fr'{home}/Downloads'
    # Destination folder -> to find
    destination: str = fr'{home}/02_cloud/99_Unterlagen/Kontoauszuege'
    # 4. For zip
    # Zip start sting to get the right files
    zip_start: str = f'PostfachDokumente_'
    # Zip file subfolder
    zip_output: str = f'{source}/__out_dir'


def __create_line(size: int = 80, sign: str = '*') -> str:
    line = ''
    for index in range(0, size):
        line += sign[0]
    return line


def __create_header(header: str, log_obj: logging.Logger, *, color: str = CTC.default(), size: int = 80,
                    sign: str = '*'):
    top_bottom = __create_line(size, sign)

    log_obj.info(CTC.colored_string(color, top_bottom))
    log_obj.info(CTC.colored_string(color, f'{sign[0]} {header}'))
    log_obj.info(CTC.colored_string(color, top_bottom))
    pass


def __create_logger(*, log_level: int = logging.DEBUG, log_file: str = None) -> logging.Logger:
    # ---- Create logger ----
    # Geeral Formatter
    logging.basicConfig(format='%(asctime)s %(levelname)-8s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG)
    log_format = logging.Formatter(fmt='%(asctime)s %(levelname)-8s] %(message)s',
                                   datefmt='%Y-%m-%d %H:%M:%S')
    # Create logger obj.
    logger = logging.Logger("Logger")
    # Create console handler
    term_log = logging.StreamHandler(sys.stdout)
    term_log.setLevel(log_level)
    term_log.setFormatter(log_format)
    # Add Handler to logger
    logger.addHandler(term_log)

    # Create log file
    if log_file is not None:
        # of path doesn't exist
        if not os.path.exists(os.path.basename(log_file)):
            # create
            os.system(fr'mkdir -vp {os.path.basename(log_file)}')

        # Create file handler
        file_log = logging.FileHandler(log_file)
        file_log.setLevel(log_level)
        file_log.setFormatter(log_format)
        # Add handler to logger
        logger.addHandler(file_log)

    return logger


def __replace_german_umlaute(file: str, logger: logging.Logger)-> [str, None]:
    if os.path.exists(file):
        file_path = os.path.dirname(file)
        file_name = os.path.basename(file)
        
        new_file = file_name.replace('ä', 'ae').replace('ü', 'ue').replace('ö', 'oe')
        
        if file_name != new_file:
            file_name = file_name.replace(' ', '\\ ').replace('(', '\\(').replace(')', '\\)')
            new_file = new_file.replace(' ', '\\ ').replace('(', '\\(').replace(')', '\\)')
            cmd = fr'mv -vf {file_path}/{file_name} {file_path}/{new_file}'
            
            logger.debug('')
            logger.debug(CTC.colored_string(CTC.color_purple(), f'Rename {file} to {new_file}'))
            logger.debug(CTC.colored_string(CTC.color_purple(), f'With command: {cmd}'))
            
            # Rename file
            os.system(cmd)
            
            return f'{file_path}/{new_file}'
        else:
            return f'{file}'
    else:
        return None
            
            
    
    

def __main_fkt(*, delete_files: bool = True, log_level: int = logging.INFO, log_file: str = None,
               pdf_viewer: str = None, pdf_open_all: bool = False) -> int:
    
    # Generate logger
    logger = __create_logger(log_level=log_level, log_file=None)

    #Check if destination exits
    #tmp_des = glob.glob(fr'{__Config.home}/*{__Config.destination}')
    tmp_des = glob.glob(fr'{__Config.destination}')
    if len(tmp_des) == 0:
        logger.error('')
        logger.error(CTC.colored_string(CTC.color_red(), f'Destination: {__Config.destination} could not be found'))
        logger.info('')
        logger.info('End processing account')
        return 11

    __Config.destination = tmp_des[0]
    logger.info(fr'Set destination to {__Config.destination}')
    logger.info(fr'Set logfile to {__Config.destination}/{os.path.basename(log_file)}')

    # Generate logger
    logger = __create_logger(log_level=log_level, log_file=fr'{__Config.destination}/{os.path.basename(log_file)}')

    # Output header
    __create_header('Verarbeite Kontoauszuege', logger)
    logger.info('')
    logger.info(CTC.colored_string(CTC.decor_bold(), f'Suche *.zip Datei'))


    # Search for zip file
    zip_list = []
    # 1. VB starts zip with see __Confi.zip
    zip_list = glob.glob(fr'{__Config.source}/{__Config.zip_start}*.zip')

    # 2. zip hast has value
    if len(zip_list) == 0:
        for zip in glob.glob(fr'{__Config.source}/*.zip'):
            if re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}.zip', os.path.basename(zip)) is not None:
                zip_list.append(zip)
    
    # Search for other pdf in download
    pdf_file_list = glob.glob(fr'{__Config.source}/*.pdf')

    # Output and exit if no zip file found
    if len(zip_list) == 0:
        logger.warning('')
        logger.warning(CTC.colored_string(CTC.color_yellow(), f'No valid zip file found'))
#        logger.info('')
#        logger.info('End processing account')
#        return 1
    else:
        # ---- Debug output start ----
        # Show zip files
        logger.debug('')
        logger.debug(CTC.colored_string(CTC.color_purple(), f'Found following zip files:'))
        for zip_file in zip_list:
            logger.debug(CTC.colored_string(CTC.color_purple(), f'- {os.path.basename(zip_file)}'))
    
        # Show files in each zip file
        for zip_file in zip_list:
            # Run unzip cmd for files
            sub_out = subprocess.Popen(f'7z l {zip_file} | grep pdf', shell=True, stdout=subprocess.PIPE)
            out_list = str(sub_out.communicate()[0])  # Create string
            out_list = out_list.replace('b\'', '').replace('\\n\'', '')  # Remove first and last signs
            out_list = out_list.split('\\n')  # Create list
    
            logger.debug('')
            logger.debug(
                CTC.colored_string(CTC.color_purple(), f'Files in {os.path.basename(zip_file)}'))
            for file in out_list:
                for entry in file.split('  '):
                    if entry.endswith('.pdf'):
                        logger.debug(CTC.colored_string(CTC.color_purple(), f'- {entry}'))
        # ---- Debug output end ----
    
        # ----- Extracting zip and delte zip arcive -----
        for zip_file in zip_list:
            # Extract each zip file
            logger.info('')
            logger.info(f'Extracting {os.path.basename(zip_file)} to {__Config.zip_output}')
            # Create extracting command
            cmd = f'7z e -aoa -o{__Config.zip_output} {zip_file}'
    
            logger.debug('')
            logger.debug(
                CTC.colored_string(CTC.color_purple(), fr'Extract zip file {zip_file} with command:'))
            logger.debug(CTC.colored_string(CTC.color_purple(), fr'{cmd}'))
    
            # Run Command
            if os.system(cmd) != 0:
                # In case of error -> show message
                logger.error(
                    CTC.colored_string(CTC.color_red(), f'Extracting of Archive {zip_file} failed'))
                # If only one zip file was in list exit with error
                if len(zip_list) == 1:
                    logger.info('')
                    logger.info('End processing account')
                    return 2
            else:
                # Create command delete zip file
                cmd = f'rm -frv {zip_file}'
    
                logger.debug('')
                logger.debug(CTC.colored_string(CTC.color_purple(),
                                                fr'Delete zip file {zip_file} with command:'))
                logger.debug(CTC.colored_string(CTC.color_purple(), fr'{cmd}'))
    
                # Run command
                if delete_files:
                    os.system(cmd)
    
                if os.path.exists(zip_file):
                    logger.warning(CTC.colored_string(CTC.color_yellow(),
                                                      f'{os.path.basename(zip_file)} zip file could not deleted'))
                else:
                    logger.info(f'Deleted {os.path.basename(zip_file)}')
        # ----- End: Extracting zip and delte zip arcive -----
    
        # ---- Replace german umlaute and rename file -----
        logger.info('')
        for file in os.listdir(__Config.zip_output):
            __replace_german_umlaute(fr'{__Config.zip_output}/{file}', logger)
        
#        # Generate new file name
#        new_file = file.replace('ä', 'ae').replace('ü', 'ue').replace('ö', 'oe')
#
#        if file != new_file:
#            file = file.replace(' ', '\\ ')
#            new_file = new_file.replace(' ', '\\ ')
#            cmd = fr'mv -vf {__Config.zip_output}/{file} {__Config.zip_output}/{new_file}'##
#
#            logger.debug('')
#            logger.debug(CTC.colored_string(CTC.color_purple(), f'Rename {file} to {new_file}'))
#            logger.debug(CTC.colored_string(CTC.color_purple(), f'With command: {cmd}'))
#
#            # Rename file
#            os.system(cmd)
#    # ---- End: Replace german umlaute and rename file -----

    # ---- Replace german umlaute and rename file  in pdf list-----
    for i in range(0, len(pdf_file_list)):
        pdf_file_list[i] = __replace_german_umlaute(pdf_file_list[i], logger)
    
    
    #for file in pdf_file_list:
    #    __replace_german_umlaute(file, logger)

    # ----- Start rename and move account files -----
    pdf_file_list.extend(glob.glob(fr'{__Config.zip_output}/*.pdf'))

    # Check if there are files
    if len(pdf_file_list) == 0:
        logger.info('')
        logger.info(f'No PDF Files found - End processing account')
        return 3

    # Scan files
    account_obj_dict = dict()

    for pdf_file in pdf_file_list:
        logger.debug('')
        logger.debug(CTC.colored_string(CTC.color_purple(), fr'Scan file {pdf_file}'))

        account_obj = CAF.CreditCardFile(pdf_file, __Config.cc_account, __Config.cc_storage)
        account_obj.debug_output(logger)
        if account_obj.type.value != 0:
            account_obj_dict[f'{str(account_obj)}'] = account_obj
        logger.debug(CTC.colored_string(CTC.color_purple(), f'{__create_line(80, "_")}'))

    this = None
    for key in sorted(account_obj_dict.keys()):
        last = this
        this = account_obj_dict[key]

        if last is None:
            logger.info('')
            __create_header('Verarbeite Kontoauszüge', logger, color=CTC.color_blue())
        elif this.type == CAF.FileType.CreditCardFile and last.type != CAF.FileType.CreditCardFile:
            logger.info('')
            __create_header('Verarbeite Kreditkarten', logger, color=CTC.color_blue())
        # else:
        #    logger.warning(CTC.colored_string(CTC.color_yellow(),f'Unknown Type')

        logger.info(
            CTC.colored_string(CTC.color_blue(), f'Verarbeite Datei: {this.input_file}'))

        # Generate Full inout and output file
        # todo workaround aber nicht schoen
        if os.path.exists(fr'{__Config.zip_output}/{this.input_file}'):
            full_input_file: str = fr'{__Config.zip_output}/{this.input_file}'
        else:
            full_input_file: str = fr'{__Config.source}/{this.input_file}'
        full_output_file: str = fr'{this.get_destination(__Config.destination)}'

        full_output_path: str = os.path.dirname(full_output_file)
        # check if output folder exits
        if not os.path.exists(full_output_path):
            # Create command to make folder
            cmd = f'mkdir -vp {full_output_path}'

            logger.debug('')
            logger.debug(
                CTC.colored_string(CTC.color_purple(), f'Create folder {full_output_path}'))
            logger.debug(CTC.colored_string(CTC.color_purple(), f'with command: {cmd}'))

            # run cmd
            os.system(cmd)

            # Check if command was successful
            if not os.path.exists(os.path.dirname(full_output_file)):
                logger.error('')
                logger.error(
                    CTC.colored_string(CTC.color_red(), fr'Could not create {full_output_path}'))
                logger.error(CTC.colored_string(CTC.color_red(), f'End processing account'))
                return 4

            logger.info('')
            logger.info(
                CTC.colored_string(CTC.color_blue(), f'Verzeichniss {os.path.dirname(full_output_file)} erstellt'))

        # Create command to move file
        # 1. Replace spaces
        full_input_file = full_input_file.replace(' ', '\\ ')
        full_output_file = full_output_file.replace(' ', '_')
        # 2. Generate cmd
        cmd = fr'mv -vf {full_input_file} {full_output_file}'

        logger.debug('')
        logger.debug(CTC.colored_string(CTC.color_purple(), f'Move file to new destination'))
        logger.debug(CTC.colored_string(CTC.color_purple(), f'with command: {cmd}'))

        # Run command
        if delete_files:
            file_to_open = full_output_file
            os.system(cmd)

            if not os.path.exists(full_output_file):
                logger.warning('')
                logger.warning(CTC.colored_string(CTC.color_yellow(), f'{full_output_file} not exits'))
            else:
                logger.info('')
                logger.info(CTC.colored_string(CTC.color_blue(), f'Datei erfolgreich verschoben'))
                logger.info(CTC.colored_string(CTC.color_blue(), f'{full_output_file}'))

        else:
            file_to_open = full_input_file

        if pdf_viewer is not None:
            # os.system(fr'{pdf_viewer} {full_input_file}')
            sub = subprocess.Popen(fr'{pdf_viewer} {file_to_open}', shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            if not pdf_open_all:
                sub.communicate()

        # empty line at the end
        logger.info(__create_line(size=80, sign='_'))

    if os.path.exists(fr'{__Config.zip_output}'):
        if len(os.listdir(fr'{__Config.zip_output}')) == 0:
            cmd = fr'rm -rv {__Config.zip_output}'
            os.system(cmd)
        else:
            logger.warning('')
            logger.warning(CTC.colored_string(CTC.color_yellow(),
                                              f'Extracting dir not empty. Please check files and delete manually'))


# __main_fkt(delete_files=False, log_file='/home/florian/text.log', pdf_viewer='evince', pdf_open_all=False)
__main_fkt(log_level=logging.DEBUG, log_file='Kontoauszuege.log',
           pdf_viewer='evince', pdf_open_all=False)
# __main_fkt(log_level=logging.DEBUG)
# __main_fkt()
