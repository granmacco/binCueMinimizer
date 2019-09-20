# coding=cp1252
#
# osUtils.py
#
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) 2019 granmacco <@granmacco>
# https://github.com/granmacco
#
# Script inspired by @krcroft's reddit post on June 25th, 2019
# https://www.reddit.com/r/RetroPie/comments/c50djy/chd_compression_summary_for_psx/
# https://github.com/krcroft
# Thank you very much, without you, this automation wouldn't have existed!
#
# Also, special thanks to the Plata o Roms team for finding @krcroft's post, 
# putting me on the right track and inspiring some of the features of this script.
# http://t.me/RaspberryPiEmuladores
# Thank you very much for sharing your knowledge and for striving for excellence!
#
# Lastly, but not least, a very special thanks to @Sergi_0, for providing new ideas and methodologies to this script.
# https://github.com/Sergi_0
# Thank you very much for your kindness and time!!
#
# This code is licensed under Creative Commons BY-NC-SA 4.0
# You may redistribute it and/or modify it under the terms of the 
# Creative Commons BY-NC-SA 4.0 License, as published by the Creative
# Commons on their website http://creativecommons.org/licenses/by-nc-sa/4.0/
#

import logging
import os
import os.path as osp
import subprocess
import sys
from subprocess import call
from ntpath import basename
from shutil import copy, rmtree
from pathlib import Path

def run(command, replacements = None):
    """
    Lanza el comando suministrado, realizando sustituciones si se especifican.

    Parameters
    ----------
    commmand : list
        El comando con sus diferentes argumentos
    replacements : dictionary { str : str }
        Los reemplazos a realizar, siendo la clave el valor a sustituir y el valor la sustitución en sí
    
    Returns
    -------
    str
        La salida de consola

    """
    
    if replacements:
        for replacement in replacements:
            command = [replacements[replacement] if x == replacement else x for x in command]
    logging.debug('Running ' + ' '.join(command))
    if not type(command) == list:
        raise TypeError(sys._getframe().f_code.co_name + ' must be called with an %r' % 'list of str')
    result = call(command, stdout=subprocess.PIPE, shell=False)
    return result

def create_dir(path = None):
    """
    Crea un directorio de trabajo

    Parameters
    ----------
    path : str
        La raiz en la que crear el directorio de trabajo

    Returns
    -------
    str
        Ruta absoluta del directorio de trabajo

    """
    
    if path is None:
        path = os.getcwd()
    name_candidate = 'temp'
    if osp.isdir(osp.join(path, name_candidate)):
        logging.debug(name_candidate + ' existe. Busquemos otro')
        count = 1
        while osp.isdir(osp.join(path, name_candidate + str(count))):
            logging.debug(name_candidate + str(count) + ' existe. Busquemos otro')
            count += 1
        name_candidate = name_candidate + str(count)
    logging.debug('Creando directorio ' + name_candidate)
    os.mkdir(osp.join(path, name_candidate))
    new_dir = osp.join(path, name_candidate)
    return new_dir

def delete_dir(path):
    """
    Borra el directorio
    
    """
    rmtree(path)
    
def enter_dir(path):
    """
    Entra en el directorio especificado
    
    """
    os.chdir(path)

def exit_dir():
    """
    Vuelve un directorio atrás
    
    """
    os.chdir('..')
    
def copy_files_to(path, files):
    """
    Copia desde ficheros al directorio original de ejecucion
    
    """
    if files:
        for file in files:
            copy(file, path)

def delete_files(files):
    """
    Borra los ficheros especificados
    
    """
    if files:
        for file in files:
            os.remove(file) 

def list_files(path = None, extension = None):
    """
    Dada una ruta, obtiene los ficheros.cue

    Parameters
    ----------
    path : str
        El directorio a comprobar. Por defecto, el directorio de ejecución

    Returns
    -------
    list [str]
        Las rutas de los ficheros cue

    """
    
    if path is None:
        path = Path().absolute()
    files_to_process = []
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if osp.isdir(filepath):
            continue
        elif os.path.splitext(filename)[1].casefold() == '.' + extension.casefold():
            logging.debug('Encontrado ' + extension + ': ' + filepath)
            files_to_process.append(filepath)
    return files_to_process