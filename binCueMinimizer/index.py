# coding=cp1252
#
# index.py
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

import re
from binCueMinimizer.consts import frames_por_segundo
from binCueMinimizer.timestamp import Timestamp

class Index:
    id = None
    timestamp = None
    length_in_frames = None
    
    regex_line = r'(\d+) (\d+:\d+:\d+)'
    regex_timestamp = r'(\d+):(\d+):(\d+)'
    compiled_regex_line = re.compile(regex_line)
    compiled_regex_timestamp = re.compile(regex_timestamp)
    
    def __init__(self, line = None, index_id = None, timestamp = None):
        if line:
            self.set_from_string(line)
        elif index_id and timestamp:
            self.set(index_id, timestamp)
        
    def set_from_string(self, line):
        """
        Parsea el indice de un string

        Parameters
        ----------
        line : str
            La linea a parsear

        """

        results = re.search(self.regex_line, line)
        if results:
            self.set(results.group(1), results.group(2))
        
    def set(self, index_id, timestamp):
        """
        Inicializa el indice con el id y timestamp indicados

        Parameters
        ----------
        index_id : str
            El numero de indice
        timestamp : str
            El timestamp, en formato string

        """

        self.id = index_id
        self.timestamp = Timestamp(timestamp)
        self.length_in_frames = self.from_timestamp_to_frames()
        
    def from_timestamp_to_frames(self):
        return self.timestamp.frames + (self.timestamp.secs * frames_por_segundo) + (self.timestamp.mins * 60 * frames_por_segundo)
