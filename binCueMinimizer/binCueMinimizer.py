# coding=cp1252
#
# binCueMinimizer.py
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
import platform
import shutil
import re
from binCueMinimizer.osUtils import run, delete_files
from binCueMinimizer.consts import MODE_NORMAL_CHD, MODE_LOSSYWAV,\
    MODE_LOSSYWAV_HARD, MODE_U8WAV
from pathlib import Path
from shutil import rmtree

class BinCueMinimizer:

    def __init__(self, operation_mode = 2, overwrite_chd = False):
        self.base_cue_to_chd_command = "chdman createcd -i %INPUT -o %OUTPUT"
        self.base_bin_to_wav_command = "ffmpeg -y -hide_banner -nostats -loglevel panic -f s16le -ar 44.1k -ac 2 -i %INPUT -f wav -flags +bitexact -acodec pcm_s16le -ar 44100 -ac 2 %OUTPUT"
        self.base_bin_to_wav_u8_command = "ffmpeg -y -hide_banner -nostats -loglevel panic -f s16le -ar 44.1k -ac 2 -i %INPUT -f wav -flags +bitexact -acodec pcm_u8 -ar 44100 -ac 2 %OUTPUT"
        self.base_lossywav_command = "lossywav %INPUT -o ./ -q X -D 2 -U 4 -m -a 4 -s h -A --feedback 3 --limit 15848"
        self.base_lossywav_hard_command = "lossywav %INPUT -o ./ -q X -D 1 -U 2 -m -a 7 -s h -A --feedback 0 --limit 12500"
        self.base_lossywav_compliance_command = "ffmpeg -y -hide_banner -nostats -loglevel panic -i %INPUT -f wav -flags +bitexact -acodec pcm_s16le -ar 44100 -ac 2 %OUTPUT"
        self.base_wav_to_bin_command = "ffmpeg -y -hide_banner -nostats -loglevel panic -ac 2 -i %INPUT -f s16le -ar 44.1k -ac 2 %OUTPUT"
        self.filename_chdman = "chdman"
        self.filename_lossywav = "lossyWAV"
        self.filename_ffmpeg = "ffmpeg"
        self.regex_file_line = re.compile(r'(?:FILE|file|File) (?:\'|\")(.*)(?:\'|\").*')
        self.regex_track_line = re.compile(r'(?:TRACK|track|Track) \d* (AUDIO|audio|Audio)')
        self.operation_mode = operation_mode
        self.overwrite_chd = overwrite_chd
        logging.info('Inicializando BinCueMinimizer en modo ' + str(operation_mode))
        
        self.original_dir = Path().absolute()
        self.working_dir = None

    def get_dependencies(self):
        """
        Devuelve una lista de dependencias, ajustada al sistema operativo

        """
        
        is_windows = platform.system() == 'Windows'
        dependencies = [self.filename_chdman, self.filename_ffmpeg, self.filename_lossywav]
        dependencies = [ filename + '.exe' if is_windows else filename for filename in dependencies]
        return dependencies
    
    def check_dependencies(self):
        """
        Busca las dependencias y da un error en caso de no encontrarlas

        """
        
        for dependency in self.get_dependencies():
            logging.debug('Comprobando ' + dependency)
            if not os.path.isfile(os.path.join(self.get_original_dir(), dependency)):
                msg = 'Error: No se encuentra el fichero necesario \"' + dependency + '\". Asegurese de tenerlo en la misma ruta que el script'
                logging.error(msg)
                raise SystemExit(msg)
    
    def create_working_dir(self, path = None):
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
            path = self.get_original_dir()
        name_candidate = 'temp'
        if os.path.isdir(os.path.join(path, name_candidate)):
            logging.debug(name_candidate + ' existe. Busquemos otro')
            count = 1
            while os.path.isdir(os.path.join(path, name_candidate + str(count))):
                logging.debug(name_candidate + str(count) + ' existe. Busquemos otro')
                count += 1
            name_candidate = name_candidate + str(count)
        logging.info('Creando directorio ' + name_candidate)
        os.mkdir(os.path.join(path, name_candidate))
        self.working_dir = os.path.join(path, name_candidate)
        # Copia las dependencias para poder ser usadas despues
        for dependency in self.get_dependencies():
            logging.debug('Copiando dependencia ' + dependency)
            shutil.copy(os.path.join(path, dependency), self.working_dir)
        return self.working_dir
    
    def get_working_dir(self):
        """
        Devuelve el directorio de trabajo
    
        Returns
        -------
        str
            Ruta absoluta del directorio de trabajo
    
        """
        
        return self.working_dir
    
    def delete_working_dir(self):
        """
        Borra el directorio de trabajo
        
        """
        
        rmtree(self.get_working_dir())
        
    def enter_working_dir(self):
        """
        Entra al directorio de trabajo
        
        """
        
        logging.debug('Entrando en ' + self.get_working_dir())
        os.chdir(self.get_working_dir())
    
    def exit_working_dir(self):
        """
        Sale del directorio de trabajo
        
        """
        
        logging.debug('Entrando en ' + str(self.get_original_dir()))
        os.chdir(self.get_original_dir())
    
    def get_original_dir(self):
        """
        Devuelve el directorio original de ejecución
    
        Returns
        -------
        str
            Ruta absoluta del directorio original de ejecución
    
        """
        
        return self.original_dir
    
    def copy_files_to_original_dir(self, files):
        """
        Copia desde ficheros al directorio original de ejecucion
        
        """
        
        for file in files:
            shutil.copy(os.path.join(self.get_working_dir(), file), self.get_original_dir())

    def from_bin_to_wav_common(self, bins, command):
        """
        Bloque común de conversión de BIN a WAV
    
        Parameters
        ----------
        bins : list [str]
            Los bin a procesar
    
        Returns
        -------
        list [str]
            Las rutas absolutas de los ficheros wav
    
        """
        
        if type(bins) is not list:
            bins = [bins]
        files_to_process = []
        # Uso fbin en lugar de bin porque bin es una palabra reservada
        for fbin in bins:
            source = fbin
            target = source[:-3] + 'WAV'
            logging.info('Transformando ' + source + ' a ' + target)
            run(command.split(), {'%INPUT': source, '%OUTPUT': target})
            files_to_process.append(target)
        return files_to_process
    
    def from_bin_to_wav(self, bins):
        """
        Convierte los ficheros bin suministrados en wav s16le
    
        Parameters
        ----------
        bins : list [str]
            Los bin a procesar
    
        Returns
        -------
        list [str]
            Las rutas absolutas de los ficheros wav
    
        """
        
        return self.from_bin_to_wav_common(bins, self.base_bin_to_wav_command)
    
    def from_bin_to_wav_u8(self, bins):
        """
        Convierte los ficheros bin suministrados en wav u8
    
        Parameters
        ----------
        bins : list [str]
            Los bin a procesar
    
        Returns
        -------
        list [str]
            Las rutas absolutas de los ficheros wav
    
        """
        
        return self.from_bin_to_wav_common(bins, self.base_bin_to_wav_u8_command)
    
    def apply_lossywav_common_to_wav(self, wavs, command):
        """
        Bloque comun de aplicación de lossywav a una lista de wavs
    
        Parameters
        ----------
        wavs : list [str]
            Los wavs a procesar
    
        Returns
        -------
        list [str]
            Las rutas absolutas de los ficheros wavs procesados con lossywav
    
        """
    
        if type(wavs) is not list:
            wavs = [wavs]
        files_to_process = []
        for wav in wavs:
            source = wav
            target = source[:-3] + 'lossy.WAV'
            logging.info('Transformando ' + source + ' a ' + target)
            run(command.split(), {'%INPUT': source})
            files_to_process.append(target)
        return files_to_process
    
    def apply_lossywav_to_wav(self, wavs):
        """
        Aplica el lossywav a una lista de wavs
    
        Parameters
        ----------
        wavs : list [str]
            Los wavs a procesar
    
        Returns
        -------
        list [str]
            Las rutas absolutas de los ficheros wavs procesados con lossywav
    
        """
    
        return self.apply_lossywav_common_to_wav(wavs, self.base_lossywav_command)
    
    def apply_lossywav_hard_to_wav(self, wavs):
        """
        Aplica el lossywav hard a una lista de wavs
    
        Parameters
        ----------
        wavs : list [str]
            Los wavs a procesar
    
        Returns
        -------
        list [str]
            Las rutas absolutas de los ficheros wavs procesados con lossywav
    
        """
    
        return self.apply_lossywav_common_to_wav(wavs, self.base_lossywav_hard_command)
    
    def fix_lossywav_compliance(self, wavs):
        """
        Elimina impurezas de los ficheros de lossywav suministrados en la lista
    
        Parameters
        ----------
        wavs : list [str]
            Los wavs a procesar
    
        Returns
        -------
        list [str]
            Las rutas absolutas de los ficheros wavs procesados
    
        """
    
        if type(wavs) is not list:
            wavs = [wavs]
        files_to_process = []
        for wav in wavs:
            source = wav
            target = source[:-9] + 'WAV'
            logging.info('Depurando ' + source + ' y convirtiendolos a ' + target)
            run(self.base_lossywav_compliance_command.split(), {'%INPUT': source, '%OUTPUT': target})
            files_to_process.append(target)
        return files_to_process
    
    def from_wav_to_bin(self, wavs):
        """
        Convierte los ficheros wav suministrados a bin PCM
    
        Parameters
        ----------
        wavs : list [str]
            Los wavs a procesar
    
        Returns
        -------
        list [str]
            Las rutas absolutas de los ficheros bin
    
        """
    
        if type(wavs) is not list:
            wavs = [wavs]
        files_to_process = []
        for wav in wavs:
            source = wav
            target = source[:-3] + 'BIN'
            logging.info('Transformando ' + source + ' a ' + target)
            run(self.base_wav_to_bin_command.split(), {'%INPUT': source, '%OUTPUT': target})
            files_to_process.append(target)
        return files_to_process
    
    def get_chd_command(self):
        command = self.base_cue_to_chd_command
        if self.overwrite_chd:
            command += " --force"
        return command
    
    def from_cue_to_chd(self, cues, suffix = None):
        """
        Convierte los cues suministrados en CHD
    
        Parameters
        ----------
        cues : list [str]
            Los cues a procesar
    
        Returns
        -------
        list [str]
            Las rutas absolutas de los CHD resultantes
    
        """
    
        if type(cues) is not list:
            cues = [cues]
        files_to_process = []
        for cue in cues:
            source = cue
            target = source[:-3]
            if suffix:
                target += suffix + "."
            target += 'CHD'
            msg = 'Procesando ' + source + '...'
            logging.info(msg)
            print(msg)
            run(self.get_chd_command().split(), {'%INPUT': source, '%OUTPUT': target})
            files_to_process.append(target)
            msg = source + ' transformado a CHD'
            logging.info(msg)
            print(msg)
        return files_to_process
    
    def minimise_cue(self, cue):
        """
        Minimiza el CueFile suministrado
    
        Parameters
        ----------
        cues : CueFile
            El cue a procesar

        """
        self.check_dependencies()
        if cue.is_processable():
            if self.operation_mode != 1 and not cue.has_audio_tracks:
                msg  = '************************ PRECAUCION ************************'
                msg += '\n'
                msg += 'El cue ' + cue.path + ' no contiene pistas de audio.'
                msg += '\n'
                msg += '\n'
                msg += 'Sólo se puede aplicar el método ' + str(MODE_NORMAL_CHD) + ' - CHD sin compresión adicional'
                msg += '\n'
                msg += '************************ PRECAUCION ************************'
                logging.info(msg)
                print(msg)
            if self.operation_mode == MODE_NORMAL_CHD or not cue.has_audio_tracks:
                self.from_cue_to_chd(cue.path)
            elif self.operation_mode != MODE_NORMAL_CHD and cue.has_audio_tracks:
                working_dir = self.create_working_dir()
                try:
                    cue = cue.copy_to_dir(working_dir)
                    self.enter_working_dir()
                    try:
                        if cue.is_monofile_multitrack():
                            cue = cue.split_tracks()
                        audio_bins = []
                        for audio_bin in cue.get_audio_bins():
                            audio_bins.append(audio_bin.path)
                        suffix = ""
                        if self.operation_mode in [MODE_LOSSYWAV, MODE_LOSSYWAV_HARD]:
                            wavs = self.from_bin_to_wav(audio_bins)
                            if self.operation_mode  == MODE_LOSSYWAV:
                                suffix = "lossy"
                                lossy_wavs = self.apply_lossywav_to_wav(wavs)
                            else:
                                suffix = "lossy.hard"
                                lossy_wavs = self.apply_lossywav_hard_to_wav(wavs)
                            compliant_lossy_wavs = self.fix_lossywav_compliance(lossy_wavs)
                            delete_files(lossy_wavs)
                            new_bins = self.from_wav_to_bin(compliant_lossy_wavs)
                            delete_files(compliant_lossy_wavs)
                            new_chds = self.from_cue_to_chd(cue.path, suffix=suffix)
                        elif self.operation_mode == MODE_U8WAV:
                            suffix = "u8"
                            u8_wavs = self.from_bin_to_wav_u8(audio_bins)
                            new_bins = self.from_wav_to_bin(u8_wavs)
                        new_chds = self.from_cue_to_chd(cue.path, suffix=suffix)
                        delete_files(new_bins)
                        self.copy_files_to_original_dir(new_chds)
                    finally:
                        self.exit_working_dir()
                finally:
                    self.delete_working_dir()
