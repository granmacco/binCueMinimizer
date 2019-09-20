# coding=cp1252
#
# cueFile.py
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

import copy
import logging
import re
import os.path as osp
import shutil
from binCueMinimizer.binFile import Bin
from binCueMinimizer.track import Track
from ntpath import basename

class CueFile:
    path = None
    framesize = None
    bins = None
    tracks = None
    has_audio_tracks = False
    has_data_tracks = False
    was_found_processable = True
    
    regex_file_line = r'(?:FILE|file|File) (?:\'|\")(.*)(?:\'|\").*'
    regex_track_line = r'(?:TRACK|track|Track) (\d+) (\S+)'
    regex_index_line = r'(?:INDEX|index|Index) (\d+ \d+:\d+:\d+)'
    regex_pregap_line = r'(?:PREGAP|pregap|Pregap) (\d+:\d+:\d+)'
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
        """
        Determina si el cue denotado por este objeto es monofichero con pistas de audio
    
        Returns
        -------
        bool
            True si tiene varias pistas y un solo fichero bin
    
        """
        
        return len(self.bins) < len(self.tracks) and len(self.bins) == 1

    def get_audio_bins(self):
        files_to_process = []
        for track in self.tracks:
            if track.is_audio_track:
                files_to_process.append(track)
        return files_to_process

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
        last_pregap = None
        with open(cue, "r") as file:
            cue_contents = file.read().split('\n')

        for line in cue_contents:
        
            # ¿Es linea de fichero?    
            results = re.search(self.regex_file_line, line)
            if results:
                last_bin = Bin(osp.join(osp.dirname(cue), results.group(1)))
                self.bins.append(last_bin)
                
            # ¿Es linea de pista?
            results = re.search(self.regex_track_line, line)
            if results:
                last_track = Track(bin_file=last_bin, track_id=results.group(1), track_type = results.group(2), parent_cue = self)
                last_track.check_if_exists()
                self.tracks.append(last_track)
                if last_track.framesize and not self.framesize:
                    self.framesize = last_track.framesize
                self.has_audio_tracks |= last_track.is_audio_track
                self.has_data_tracks |= last_track.is_data_track
              
            # ¿Es linea de indice?
            results = re.search(self.regex_index_line, line)
            if results:
                last_track.add_index(results.group(1), pregap = last_pregap)
                last_pregap = None
                
            # ¿Es linea de pregap?
            results = re.search(self.regex_pregap_line, line)
            if results:
                last_pregap = results.group(1)

        if self.is_processable():
            if len(self.bins) == len(self.tracks):
                logging.info("El CUE [ " + self.path + " ] tiene tantas pistas como ficheros, se continua de forma normal.")
            else:
                if len(self.bins) != 1:
                    self.was_found_processable = False
                    msg = "El CUE [ " + self.path + " ] es multifichero, pero hay menos ficheros que pistas. Este caso no está contemplado, lo siento."
                    logging.error(msg)
                else:
                    logging.info("El CUE [ " + self.path + " ] es multipista con un solo fichero. Se debería partir antes de continuar.")

        logging.info("Resultados del parseo del fichero: " + cue)
        logging.debug("Bins: " + str(len(self.bins)))
        logging.debug("Pistas: " + str(len(self.tracks)))
        logging.info("Se puede comprimir: " + ( "si" if self.is_processable() else "NO"))
        
    def is_processable(self):
        """
        Determina si este fichero cue puede comprimirse
    
        Returns
        -------
        bool
            True si se puede comprimir

        """
    
        if self.was_found_processable:
            if len(self.bins) == 0:
                self.was_found_processable = False
                msg = "No se encontraron ficheros BIN en el CUE [ " + self.path + " ]. No se realizará ninguna operación sobre este CUE."
                logging.error(msg)
            else:
                for track in self.tracks:
                    self.was_found_processable &= track.check_if_exists()
                if not self.was_found_processable:
                    msg = "No se pueden procesar ficheros CUE para el cual no dispone de todos los archivos BIN enlazados"
                    logging.error(msg)
        return self.was_found_processable
    
    def copy_to_dir(self, path):
        """
        Copia los ficheros relativos a este cue a la ruta especificada
    
        Parameters
        ----------
        path : str
            La nueva ruta

        """
    
        logging.debug('Copiando juego ' + self.path + ' al directorio ' + path)
        for bin_file in self.bins:
            shutil.copy(osp.join(path, bin_file.path), path)
        shutil.copy(self.path, path)
        new_cue = copy.copy(self)
        new_cue.update_path(path)
        return new_cue
    
    def update_path(self, parent_path):
        """
        Actualiza las rutas de todos los ficheros relativos a este cue
    
        Parameters
        ----------
        parent_path : str
            La nueva ruta

        """
        
        self.path = osp.join(parent_path, basename(self.path))
        for track in self.tracks:
            track.path = osp.join(parent_path, basename(track.path))
        for binFile in self.bins:
            binFile.path = osp.join(parent_path, basename(binFile.path))

    def write_cue(self, path = None):
        """
        Escribe el cue en la ruta especificada. Si no se especifica, entonces lo hace en su ruta original.
    
        Parameters
        ----------
        path : str
            La ruta en la que escribir el cue

        """
        
        if not path:
            path = self.path
        cue_contents = ""
        if not self.is_monofile_multitrack():
            cue_contents += 'FILE "' + basename(self.bins[0].path) + '" BINARY' + '\n'
            for track in self.tracks:
                cue_contents += '  TRACK ' + track.id + ' ' + track.type + '\n'
                for index in track.indexes:
                    cue_contents += '    INDEX ' + track.indexes[index].id + ' ' + str(track.indexes[index].timestamp) + '\n'
        else:
            for track in self.tracks:
                cue_contents += 'FILE "' + basename(track.path) + '" BINARY' + '\n'
                cue_contents += '  TRACK ' + track.id + ' ' + track.type + '\n'
                for index in track.indexes:
                    cue_contents += '    INDEX ' + track.indexes[index].id + ' ' + str(track.indexes[index].timestamp) + '\n'
        with open(path, 'w') as file:
            file.write(cue_contents)
    
    def split_tracks(self):
        """
        Separa el bin único en multiples pistas, creando un nuevo cue, el cual devuelve.
    
        Returns
        -------
        CueFile
            El nuevo cue
    
        """
        if self.is_monofile_multitrack() and self.is_processable():
            new_cue = copy.copy(self)
            source_bin_file = new_cue.bins[0]
            max_offset = source_bin_file.filesize // new_cue.framesize
            logging.debug("El fichero " + source_bin_file.path + " tiene " + str(max_offset) + " frames. Empezamos a mapear con las pistas de audio desde el final.")
            actual_offset = max_offset
            new_cue.bins = []
            for track in reversed(new_cue.tracks):
                starting_point = track.indexes["01"].length_in_frames
                track.tracksize = (actual_offset - starting_point) * track.framesize
                actual_offset = starting_point
                original_track_basename = basename(track.path)
                new_track_basename = original_track_basename.split('.')[0] + ' (Track ' + track.id + ').' + original_track_basename.split('.')[1] 
                track.path = track.path.replace(original_track_basename, new_track_basename)
                track.parent_cue = new_cue
                track.set_indexes_to_zero()
                
            # Tras calcular las nuevas longitudes de pista y los nuevos nombres, partimos el bin original
            with open(source_bin_file.path, 'rb') as source_file:
                for track in new_cue.tracks:
                    logging.debug('Separando la pista ' + track.id + ' del fichero ' + source_bin_file.path)
                    written = 0
                    chunksize = 8192
                    with open(track.path, 'wb') as target_file:
                        while written != track.tracksize:
                            if chunksize + written > track.tracksize:
                                chunksize = track.tracksize - written
                            chunk = source_file.read(chunksize)
                            target_file.write(chunk)
                            written += chunksize
                new_cue.bins.append(Bin(track.path))
            new_cue.write_cue()
            return new_cue
        else:
            return self
