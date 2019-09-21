# coding=cp1252
#
# track.py
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
import re
import os.path as osp
from binCueMinimizer.consts import Framesizes
from binCueMinimizer.index import Index
from binCueMinimizer.binFile import Bin
from binCueMinimizer.timestamp import Timestamp
import copy

class Track:
    id = None
    path = None
    type = None
    is_audio_track = False
    is_data_track = False
    indexes = None
    frames = None
    framesize = None
    tracksize = None
    parent_cue = None
    binFile = None
    
    regex_timestamp = r'(\d+):(\d+):(\d+)'
    compiled_regex_timestamp = re.compile(regex_timestamp)
    
    def __init__(self, track_id, bin_file = None, path = None, track_type = None, framesize = None, parent_cue = None):
        self.id = track_id
        self.indexes = {}
        if bin_file:
            self.path = bin_file.path
            self.bin = bin_file
        elif path:
            self.path = path
            self.bin = Bin(path)
        if framesize:
            self.framesize = framesize
            if self.bin:
                self.bin.framesize = framesize
        if track_type:
            self.type = track_type
            self.is_audio_track = self.type.casefold() == 'AUDIO'.casefold()
            self.is_data_track = not self.is_audio_track
            self.framesize = Framesizes[track_type.casefold()]
            if self.bin:
                self.bin.framesize = self.framesize
        if parent_cue:
            self.parent_cue = parent_cue
    
    def add_index(self, string, pregap = None):
        """
        Parsea el string para añadir un nuevo indice a la pista. De forma opcional, se puede indicar el pregap a esta pista en particular.

        Parameters
        ----------
        string : str
            El string que denota la pista
        pregap : str
            El pregap a aplicar

        """

        index = Index(string)
        if index.id in self.indexes:
            self.log_error_repeated_index(index)
        self.indexes[index.id] = index
        if pregap:
            # timestamp = min:sec:frames
            timestamp_pregap = Timestamp(pregap)
            timestamp_index01 = index.timestamp
            timestamp_index00 = copy.copy(timestamp_index01)
            timestamp_index00 = timestamp_index00.substract(timestamp_pregap)
            index_00 = "00 " + str(timestamp_index00)
            self.add_index(index_00)

    def check_if_exists(self):
        """
        Comprueba si el fichero indicado en la pista existe

        Returns
        -------
        bool
            True si el fichero existe
    
        """
        
        if self.path and not osp.exists(self.path):
            self.log_error_track_not_exists()
            return False
        else:
            return True
        
    def set_indexes_to_zero(self):
        """
        Pasa los indices de su base a actual a una base 0. Solo aplicable si tenemos INDEX 00 e INDEX 01, y solo es útil si hablamos de un fichero multipista
    
        """
        
        if '00' in self.indexes and '01' in self.indexes:
            timestamp_index_00 = self.indexes['00'].timestamp
            timestamp_index_01 = self.indexes['01'].timestamp
            new_index_01 = '01 ' + str(copy.copy(timestamp_index_01).substract(timestamp_index_00))
            new_index_00 = '00 ' + str(Timestamp(mins=0, secs=0, frames=0))
            logging.debug('Se ajusta el indice 00 ' + str(timestamp_index_00) +  ' a ' + new_index_00)
            logging.debug('Se ajusta el indice 01 ' + str(timestamp_index_01) +  ' a ' + new_index_01)
            self.indexes = {}
            self.add_index(new_index_00)
            self.add_index(new_index_01)
        else:
            logging.debug('Falta el indice 00 o el 01, por lo que no hace falta ajustar')

    def log_error_repeated_index(self, index):
        """
        Muestra el mensaje de error de indice repetido

        Parameters
        ----------
        index : str
            El indice repetido

        """

        msg  = '************************ ERROR EN FICHERO CUE ************************'
        msg += '\n'
        msg += 'ERROR en ' + self.parent_cue.path + ' !!!!!!'
        msg += '\n'
        msg += '\n'
        msg += 'El cue tiene varias veces definido el INDEX ' + index + ' para la pista ' + self.id
        msg += '\n'
        msg += '\n'
        msg += 'Si has modificado el CUE a mano, comprueba que no has cometido un error.'
        msg += '\n'
        msg += '************************ ERROR EN FICHERO CUE ************************'
        logging.error(msg)
        print(msg)
        
    def log_error_track_not_exists(self):
        """
        Muestra el mensaje de error de que el fichero de la pista no existe

        """
        msg  = '************************ ERROR EN FICHERO ENLAZADO ************************'
        msg += '\n'
        msg += 'ERROR en ' + self.parent_cue.path + ' !!!!!!'
        msg += '\n' 
        msg += '\n'
        msg += 'La pista ' + self.id + ' hace referencia a un fichero que no existe.'
        msg += '\n'
        msg += 'Fichero: "' + self.path + '"'
        msg += '\n'
        msg += 'Compruebe que el fichero existe y está en la misma ruta que el CUE. '
        msg += '\n'
        msg += '\n'
        msg += '¿Es posible que lo haya renombrado? Recuerde que el nombre del fichero'
        msg += '\n'
        msg += '.BIN debe coincidir con el nombre que aparece dentro del fichero .CUE'
        msg += '\n'
        msg += '************************ ERROR EN FICHERO ENLAZADO ************************'
        
        logging.error(msg)
        print(msg)