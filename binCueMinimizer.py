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
# Also, special thanks to @Kactius and @Jcarliman for finding @krcroft's post, 
# putting me on the right track and inspiring some of the features of this script.
# https://github.com/kactius
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

import os
import os.path as osp
import sys
import copy
import subprocess
from subprocess import call
from pathlib import Path
from shutil import copy, rmtree
import re
import logging
from ntpath import basename
import platform
from cueparser import CueSheet

version="1.0"
# 75 frames por segundo, fuente: https://en.wikipedia.org/wiki/Track_(optical_disc)
frames_por_segundo = 75
logging.basicConfig(level=logging.DEBUG, filename="binCueMinimizer.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

Blocksizes={
    'AUDIO'.casefold():      2352,
    'MODE1/2352'.casefold(): 2352,
    'MODE2/2352'.casefold(): 2352,
    'CDI/2352'.casefold():   2352,
    'CDG'.casefold():        2448,
    'MODE1/2048'.casefold(): 2048,
    'MODE2/2336'.casefold(): 2336,
    'CDI/2336'.casefold():   2336
    }

class Bin:
    path = None
    num = 0
    blocksize = None
    is_audio_bin = False
    
    def __init__(self, path, num = None):
        self.path = path
        if num:
            self.num = num
    
    def is_audio_bin(self):
        return self.is_audio_bin
    
    def is_data_bin(self):
        return not self.is_audio_bin

class Index:
    id = None
    timestamp = None
    length_in_frames = None
    
    regex_line = r'(\d+) (\d+:\d+:\d+)'
    regex_timestamp = r'(\d+) (\d+):(\d+):(\d+)'
    compiled_regex_line = re.compile(regex_line)
    compiled_regex_timestamp = re.compile(regex_timestamp)
    
    def __init__(self, line = None, index_id = None, timestamp = None):
        if line:
            self.set_from_string(line)
        elif index_id and timestamp:
            self.set(index_id, timestamp)
        
    def set_from_string(self, line):
        results = self.compiled_regex_line(line)
        if results:
            self.set(results.group(1), results.group(2))
        
    def set(self, index_id, timestamp):
        self.id = index_id
        self.timestamp = timestamp
        self.length_in_frames = self.from_timestamp_to_frames(timestamp)
        
    def from_timestamp_to_frames(self, timestamp):
        # timestamp = min:sec:frames
        results = self.compiled_regex_timestamp.match(timestamp)
        mins = int(results.group(1))
        secs = int(results.group(2))
        frames = int(results.group(3))
        
        return frames + (secs * frames_por_segundo) + (mins * 60 * frames_por_segundo)
        

class Track:
    id = None
    path = None
    num = 0
    type = None
    is_audio_track = False
    indexes = None
    blocksize = None
    tracksize = None
    parent_cue = None
    
    regex_timestamp = r'(\d+):(\d+):(\d+)'
    compiled_regex_timestamp = re.compile(regex_timestamp)
    
    def __init__(self, track_id, path = None, track_type = None, blocksize = None, parent_cue = None):
        self.id = track_id
        self.indexes = {}
        if path:
            self.path = path
        if blocksize:
            self.blocksize = blocksize
        if track_type:
            self.type = track_type
            self.is_audio_track = self.type.casefold() == 'AUDIO'.casefold()
            self.blocksize = Blocksizes[track_type.casefold]
        if parent_cue:
            self.parent_cue = parent_cue
        
    
    def is_audio_track(self):
        return self.is_audio_track
    
    def is_data_track(self):
        return not self.is_audio_track
    
    def add_index(self, string):
        index = Index(string)
        self.indexes[index.id] = index
        
    def check_if_exists(self):
        if self.path and not osp.exists(self.path):
            logging.error('******** ERROR EN FICHERO ENLAZADO ********')
            logging.error('ERROR !!!! - La pista ' + self.id + ' del CUE ' + self.parent_cue.path + ' hace referencia a un fichero que no existe')
            logging.error('Compruebe que el fichero "' + self.path + '" existe y está en la misma ruta que el CUE. ¿Es posible que lo haya renombrado?')
            logging.error('Recuerde que el nombre del fichero .BIN debe coincidir con el nombre que aparece dentro del fichero .CUE')
            logging.error('****** FIN ERROR EN FICHERO ENLAZADO ******')
            return False
        else:
            return True
            

class CueFile:
    path = None
    blocksize = None
    bins = None
    tracks = None
    has_audio_tracks = False
    has_data_tracks = False
    is_processable = True
    
    regex_file_line = r'(?:FILE|file|File) (?:\'|\")(.*)(?:\'|\").*'
    regex_track_line = r'(?:TRACK|track|Track) (\d+) (\S)'
    regex_index_line = r'(?:INDEX|index|Index) (\d+ \d+:\d+:\d+)'
    compiled_regex_file_line = re.compile(regex_file_line)
    compiled_regex_track_line = re.compile(regex_track_line)
    compiled_regex_index_line = re.compile(regex_index_line)
    
    def __init__(self, cue = None):
        self.tracks = []
        self.bins = []
        if cue:
            self.path = cue
            self.parse_cue(cue)
    
    def is_monofile_multitrack(self):
        return len(self.bins) < len(self.tracks)
    
    def parse_cue(self, cue):
        """
        Parsea un fichero cue e inicializa la estructura de datos
    
        Parameters
        ----------
        cue : str
            El cue a procesar

        """
    
        self.path = cue
        cue_contents = None
        last_bin = None
        last_track = None
        with open(cue, "r") as file:
            cue_contents = file.read().split('\n')

        for line in cue_contents.split('\n'):
        
            # ¿Es linea de fichero?    
            results = re.search(self.regex_file_line, line)
            if results:
                last_bin = Bin(os.path.join(os.path.dirname(cue), results.group(1)))
                self.bins.append(last_bin)
                
            # ¿Es linea de pista?
            results = re.search(self.regex_track_line, line)
            if results:
                last_track = Track(path=last_bin, track_id=results.group(1), track_type = results.group(2), parent_cue = self)
                last_track.check_if_exists()
                self.tracks.append(last_track)
                if last_track.blocksize and not self.blocksize:
                    self.blocksize = last_track.blocksize
                self.has_audio_tracks |= last_track.is_audio_track()
              
            # ¿Es linea de indice?
            results = re.search(self.regex_index_line, line)
            if results:
                last_track.add_index(results.group(1))

        if self.is_processable():
            if len(self.bins) == len(self.tracks):
                logging.debug("El CUE [ " + self.path + " ] tiene tantas pistas como ficheros, se continua de forma normal.")
            else:
                if len(self.bins) != 1:
                    self.is_processable = False
                    msg = "El CUE [ " + self.path + " ] es multifichero, pero no se corresponde con las listas. Este caso no está contemplado, lo siento."
                    logging.debug(msg)
                else:
                    logging.debug("El CUE [ " + self.path + " ] es multipista con un solo fichero. Se partirá antes de continuar.")
                    bin_file = self.bins[0]
                    max_offset = bin_file.size // self.globalBlocksize
                    logging.debug("El fichero " + bin_file.path + " tiene " + str(max_offset) + " frames. Empezamos a mapear con las pistas de audio desde el final.")
                    actual_offset = max_offset
                    for track in reversed(bin_file.tracks):
                        track.tracksize = (actual_offset - track.indexes["01"].length_in_frames) * track.blocksize
                        actual_offset = track.indexes["01"].length_in_frames

        logging.debug("Resultados del parseo del fichero: " + cue)
        logging.debug("Bins: " + str(len(self.bins)))
        logging.debug("Pistas: " + str(len(self.tracks)))
        logging.debug("Se puede comprimir: " + ( "si" if self.is_processable() else "NO"))
        
    def is_processable(self):
        if self.is_processable:
            if len(self.bins) == 0:
                self.is_processable = False
                msg = "No se encontraron ficheros BIN en el CUE [ " + self.path + " ]. No se realizará ninguna operación sobre este CUE."
                logging.debug(msg)
            else:
                for track in self.tracks:
                    self.is_processable &= track.check_if_exists()
                if not self.is_processable:
                    msg = "No se pueden procesar ficheros CUE para el cual no dispone de todos los archivos BIN enlazados"
                    logging.debug(msg)
        return self.is_processable
    
    def copy_to_dir(self, path):
        logging.debug('Copiando juego ' + self.path + ' al directorio ' + path)
        for bin_file in self.bins:
            copy(os.path.join(path, bin_file.path), path)
        copy(self.path, path)
        new_cue = copy.copy(self)
        new_cue.path = os.path.join(path, basename(self.path))
        return new_cue

    def get_audio_bins(self):
        files_to_process = []
        for track in self.tracks:
            if track.is_audio_track():
                files_to_process.append(track)
        return files_to_process
    
    def split_tracks(self):
        """
        Separa el bin único en multiples pistas, creando un nuevo cue, el cual devuelve.
    
        Returns
        -------
        CueFile
            El nuevo cue
    
        """
        new_cue = copy.copy(self)
        new_cue.tracks = []
        if self.is_monofile_multitrack():
            # use calculated sectors, read the same amount, start new file when equal
            for track in self.tracks:
                source_bin = track.path
                written = 0
                chunksize = 1024 * 1024
                target_bin = basename(track.path) + ' (Track ' + str(track.num) + ').bin'
                new_track = copy.copy(track)
                new_track.path = target_bin
                with open(source_bin.path, 'rb') as source_file:
                    with open(target_bin, 'wb') as target_file:
                        while written != track.tracksize:
                            if chunksize + written > track.tracksize:
                                chunksize = track.tracksize - written
                            chunk = source_file.read(chunksize)
                            target_file.write(chunk)
                            written += chunksize
        

class BinCueMinimizer:

    def __init__(self):
        self.base_cue_to_chd_command = "chdman createcd -i %INPUT -o %OUTPUT"
        self.base_bin_to_wav_command = "ffmpeg -y -hide_banner -nostats -loglevel panic -f s16le -ar 44.1k -ac 2 -i %INPUT -f wav -flags +bitexact -acodec pcm_s16le -ar 44100 -ac 2 %OUTPUT"
        self.base_lossywav_command = "lossywav %INPUT -o ./ -q X -D 2 -U 4 -m -a 4 -s h -A --feedback 3 --limit 15848"
        self.base_lossywav_compliance_command = "ffmpeg -y -hide_banner -nostats -loglevel panic -i %INPUT -f wav -flags +bitexact -acodec pcm_s16le -ar 44100 -ac 2 %OUTPUT"
        self.base_wav_to_bin_command = "ffmpeg -y -hide_banner -nostats -loglevel panic -ac 2 -i %INPUT -f s16le -ar 44.1k -ac 2 %OUTPUT"
        self.filename_chdman = "chdman"
        self.filename_lossywav = "lossyWAV"
        self.filename_ffmpeg = "ffmpeg"
        self.regex_file_line = re.compile(r'(?:FILE|file|File) (?:\'|\")(.*)(?:\'|\").*')
        self.regex_track_line = re.compile(r'(?:TRACK|track|Track) \d* (AUDIO|audio|Audio)')
        
        self.original_dir = Path().absolute()
        self.working_dir = None


    def run(self, command, replacements = None):
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
        print("\n$ " + ' '.join(command) + "\n")
        if not type(command) == list:
            raise TypeError(sys._getframe().f_code.co_name + ' must be called with an %r' % 'list of str')
        result = call(command, stdout=subprocess.PIPE, shell=False)
        return result
    
    def get_dependencies(self):
        is_windows = platform.system() == 'Windows'
        dependencies = [self.filename_chdman, self.filename_ffmpeg, self.filename_lossywav]
        dependencies = [ filename + '.exe' if is_windows else filename for filename in dependencies]
        return dependencies
    
    def check_dependencies(self):
        for dependency in self.get_dependencies():
            logging.debug('Comprobando ' + dependency)
            if not os.path.isfile(os.path.join(self.get_original_dir(), dependency)):
                msg = 'Error: No se encuentra el fichero necesario \"' + dependency + '\". Asegurese de tenerlo en la misma ruta que el script'
                logging.debug(msg)
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
        logging.debug('Creando directorio ' + name_candidate)
        os.mkdir(os.path.join(path, name_candidate))
        self.working_dir = os.path.join(path, name_candidate)
        # Copia las dependencias para poder ser usadas despues
        for dependency in self.get_dependencies():
            copy(os.path.join(path, dependency), self.working_dir)
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
        os.chdir(self.get_working_dir())
    
    def exit_working_dir(self):
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
            copy(os.path.join(self.get_working_dir(), file), self.get_original_dir())
    
    def delete_files(self, files):
        if files:
            for file in files:
                os.remove(file) 
    
    def copy_game_to_dir(self, cues, new_path = None):
        """
        Copia un juego al directorio especificado, por defecto, el de trabajo
    
        Para ello, se debe suministrar la ruta del .cue. Entonces se parseará,
        y sólo se moverán aquellos ficheros especificados en el cue.
    
        Parameters
        ----------
        cues : list [str]
            Las rutas al fichero cue
        new_path : str
            La ruta a la que copiar el juego. Por defecto, el directorio de trabajo
    
        Returns
        -------
        list [str]
            Las nuevas rutas de los ficheros cue
    
        """
        
        if type(cues) is not list:
            cues = [cues]
        if new_path is None:
            new_path = self.get_working_dir()
        files_to_process = []
        path = self.get_original_dir()
        for cue in cues:
            logging.debug('Copiando juego ' + cue + ' al directorio ' + self.get_working_dir())
            bins = self.from_cue_to_bin(cue)
            for fbin in bins:
                copy(os.path.join(path, fbin['bin']), new_path)
            copy(os.path.join(path, cue), new_path)
            files_to_process.append(os.path.join(new_path, basename(cue)))
        return files_to_process
    
    def write_cues_text(self, cues, filename):
        text_file = open(filename, "w")
        for cue in cues:
            text_file.write(cue)
            text_file.write("\n")
        text_file.close()
    
    def get_cues(self, path = None):
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
            path = self.get_original_dir()
        files_to_process = []
        for filename in os.listdir(path):
            filepath = os.path.join(path, filename)
            if osp.isdir(filepath):
                continue
            elif os.path.splitext(filename)[1].lower() == '.cue':
                logging.debug('Encontrado cue: ' + filepath)
                files_to_process.append(filepath)
        return files_to_process
    
    def get_cues_without_audio_tracks(self, cues):
        """
        Elimina los juegos con pistas de audio de la lista de cues suministrada
    
        Parameters
        ----------
        cues : list [str]
            Los cues a filtrar
    
        Returns
        -------
        list [str]
            Aquellos cues que pertenecen al listado original, y que no contienen pistas de audio
    
        """
        
        cues_with_audio_tracks = self.get_cues_with_audio_tracks(cues)
        return [cue for cue in cues if cue not in cues_with_audio_tracks]
    
    def get_cues_with_audio_tracks(self, cues):
        """
        Elimina los juegos sin pistas de audio de la lista de cues suministrada
    
        Parameters
        ----------
        cues : list [str]
            Los cues a filtrar
    
        Returns
        -------
        list [str]
            Aquellos cues que pertenecen al listado original, y que contienen pistas de audio
    
        """
    
        if type(cues) is not list:
            cues = [cues]
        files_to_process = []
        for cue in cues:
            cue_contents = []
            has_audio_tracks = False
            with open(cue, "r") as file:
                cue_contents = file.read().split('\n')
            for line in cue_contents:
                regex_result = self.regex_track_line.search(line)
                if regex_result:
                    has_audio_tracks |= regex_result.group(1).lower() == 'audio'
            if has_audio_tracks:
                logging.debug('Cue con audio tracks: ' + cue)
                files_to_process.append(cue)
            else:
                logging.debug('Cue SIN audio tracks: ' + cue)
        return files_to_process
    
    def from_cue_to_bin(self, cues):
        """
        Parsea un fichero cue y devuelve los bin asociados
        
        No tiene sentido llamarlo con un cue que no tenga pistas de audio
    
        Parameters
        ----------
        cues : list [str]
            Los cues a procesar
    
        Returns
        -------
        list [str]
            Las rutas absolutas de los ficheros bin
    
        """
    
        if type(cues) is not list:
            cues = [cues]
        files_to_process = []
        for cue in cues:
            result = {}
            cue_contents = []
            with open(cue, "r") as file:
                cue_contents = file.read().split('\n')
            for line in cue_contents:
                if 'bin' in result:
                    regex_result = self.regex_track_line.search(line)
                    if regex_result:
                        result['audio'] = regex_result.group(1).lower() == 'audio'
                        logging.debug('Encontrado audio para bin ' + result['bin'])
                    else:
                        result['audio'] = False
                        logging.debug('Encontrado pista de datos para bin ' + result['bin'])
                    files_to_process.append(result)
                    result = {}
                else:
                    regex_result = self.regex_track_line.search(line)
                    if regex_result:
                        logging.debug('!!! OJO !!! El juego ' + cue + ' tiene pistas de audio sin fichero asociado !!! OJO !!!')
                regex_result = self.regex_file_line.search(line)
                if regex_result:
                    result['bin'] = regex_result.group(1)
                    logging.debug('Encontrado bin: ' + result['bin']) 
        return files_to_process
    
    def filter_audio_tracks(self, bins):
        """
        Filtra las pistas de datos de la lista suministrada
    
        Parameters
        ----------
        bins : list [str]
            Los bins a procesar
    
        Returns
        -------
        list [str]
            Las rutas absolutas de los ficheros bin de pistas de audio
    
        """
        
        if type(bins) is not list:
            bins = [bins]
        files_to_process = []
        # Uso fbin en lugar de bin porque bin es una palabra reservada
        for fbin in bins:
            if fbin['audio']:
                files_to_process.append(fbin)
                logging.debug('Tiene pistas de audio, se queda: ' + fbin['bin'])
            else:
                logging.debug('NO tiene pistas de audio, FUERA: ' + fbin['bin'])
        return files_to_process
    
    def from_bin_to_wav(self, bins):
        """
        Convierte los ficheros bin PCM suministrados en wav
    
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
            if fbin['audio']: # Solo por si acaso
                source = fbin['bin']
                target = source[:-3] + 'WAV'
                self.run(self.base_bin_to_wav_command.split(), {'%INPUT': source, '%OUTPUT': target})
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
    
        if type(wavs) is not list:
            wavs = [wavs]
        files_to_process = []
        for wav in wavs:
            source = wav
            target = source[:-3] + 'lossy.WAV'
            self.run(self.base_lossywav_command.split(), {'%INPUT': source})
            files_to_process.append(target)
        return files_to_process
    
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
            self.run(self.base_lossywav_compliance_command.split(), {'%INPUT': source, '%OUTPUT': target})
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
            self.run(self.base_wav_to_bin_command.split(), {'%INPUT': source, '%OUTPUT': target})
            files_to_process.append(target)
        return files_to_process
    
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
            print('Processing ' + source + '...')
            self.run(self.base_cue_to_chd_command.split(), {'%INPUT': source, '%OUTPUT': target})
            files_to_process.append(target)
        return files_to_process
    
        def minimise_cue(self, cue):
            if cue.is_processable():
                # Tanto si se puede comprimir, como si no, haremos la version normal
                self.from_cue_to_chd(cue.path)
                if cue.has_audio_tracks:
                    self.create_working_dir()
                    try:
                        cue = cue.copy_to_dir()
                        self.enter_working_dir()
                        try:
                            if cue.is_monofile_multitrack():
                                continue
                            audio_bins = []
                            for audio_bin in cue.get_audio_bins():
                                audio_bins.append(audio_bin.path)
                            wavs = self.from_bin_to_wav(audio_bins)
                            lossy_wavs = self.apply_lossywav_to_wav(wavs)
                            compliant_lossy_wavs = self.fix_lossywav_compliance(lossy_wavs)
                            self.delete_files(lossy_wavs)
                            lossywav_bins = self.from_wav_to_bin(compliant_lossy_wavs)
                            self.delete_files(compliant_lossy_wavs)
                            lossywav_chds = self.from_cue_to_chd(cue.path, suffix="lossy")
                            self.delete_files(lossywav_bins)
                            self.copy_files_to_original_dir(lossywav_chds)
                        finally:
                            self.exit_working_dir()
                    finally:
                        self.delete_working_dir()


def main():
    minimizer = BinCueMinimizer()
    minimizer.check_dependencies()
    cues = minimizer.get_cues()
    cues_with_audio_tracks = minimizer.get_cues_with_audio_tracks(cues)
    cues_without_audio_tracks = minimizer.get_cues_without_audio_tracks(cues)
    minimizer.write_cues_text(cues_with_audio_tracks, "games.with.audio.txt")
    minimizer.write_cues_text(cues_without_audio_tracks, "games.without.audio.txt")

    # Como el procesado de los juegos con pistas de audio ocupa más, se hará primero

    # Los juegos con pistas han de preprocesarse.
    if cues_with_audio_tracks:
        minimizer.create_working_dir()
        try:
            # Primero, hago la version lossy, para ocupar disco duro el minimo tiempo posible
            temp_cues_with_audio_tracks = minimizer.copy_game_to_dir(cues_with_audio_tracks)
            minimizer.enter_working_dir()
            try:
                bins = minimizer.from_cue_to_bin(temp_cues_with_audio_tracks)
                audio_bins = minimizer.filter_audio_tracks(bins)
                wavs = minimizer.from_bin_to_wav(audio_bins)
                lossy_wavs = minimizer.apply_lossywav_to_wav(wavs)
                compliant_lossy_wavs = minimizer.fix_lossywav_compliance(lossy_wavs)
                minimizer.delete_files(lossy_wavs)
                lossywav_bins = minimizer.from_wav_to_bin(compliant_lossy_wavs)
                minimizer.delete_files(compliant_lossy_wavs)
                lossywav_chds = minimizer.from_cue_to_chd(temp_cues_with_audio_tracks, suffix="lossy")
                minimizer.delete_files(lossywav_bins)
                minimizer.copy_files_to_original_dir(lossywav_chds)
            finally:
                minimizer.exit_working_dir()
        finally:
            minimizer.delete_working_dir()
        # Ahora, hago el CHD version no lossy, por si acaso para comparar
        minimizer.from_cue_to_chd(cues_with_audio_tracks)

    # Los juegos sin pistas se pueden procesar del tiron
    if cues_without_audio_tracks:
        minimizer.from_cue_to_chd(cues_without_audio_tracks)
        
        
    cues = minimizer.get_cues()
    parsed_cues = []
    for cue in cues:
        parsed_cues.append(CueFile(cue))

    for cue in parsed_cues:
        if cue.is_processable():
            minimizer.create_working_dir()
            try:
                cue = cue.copy_to_dir()
                minimizer.enter_working_dir()
                try:
                    if cue.has_audio_tracks:
                        if cue.is_monofile_multitrack():
                            continue
                        
                        audio_bins = cue.get_audio_bins()
                        minimizer.apply_lossywav_to_bins
                        wavs = minimizer.from_bin_to_wav(audio_bins)
                        lossy_wavs = minimizer.apply_lossywav_to_wav(wavs)
                        compliant_lossy_wavs = minimizer.fix_lossywav_compliance(lossy_wavs)
                        minimizer.delete_files(lossy_wavs)
                        lossywav_bins = minimizer.from_wav_to_bin(compliant_lossy_wavs)
                        minimizer.delete_files(compliant_lossy_wavs)
                        lossywav_chds = minimizer.from_cue_to_chd(temp_cues_with_audio_tracks, suffix="lossy")
                        minimizer.delete_files(lossywav_bins)
                    
                    
                    
                    minimizer.from_cue_to_chd(cue.path)
                finally:
                    minimizer.exit_working_dir()
            finally:
                minimizer.delete_working_dir()
'''
obten los cues
procesa los cues
para cada cue
  si es procesable
    metete en la carpeta de trabajo
    si no tiene audio
      convierte
    si si tiene audio
      si es monofichero
        separalo
      procesa los wavs
      convierte
'''
                
if __name__ == '__main__':
    main()