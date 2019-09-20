# coding=cp1252
#
# timestamp.py
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
from binCueMinimizer.consts import frames_por_segundo, segundos_por_minuto

class Timestamp:
    mins = 0
    secs = 0
    frames = 0
    separator = ":"
    # timestamp = min:sec:frames
    regex_timestamp = r'(\d+):(\d+):(\d+)'
    
    def __init__(self, string=None, mins=None, secs=None, frames=None):
        if string:
            results = re.search(self.regex_timestamp, string)
            if results:
                self.mins = int(results.group(1))
                self.secs = int(results.group(2))
                self.frames = int(results.group(3))
            else:
                raise ValueError('No se pudo determinar el timestamp. Valor: ' + string)
        elif mins is not None and secs is not None and frames is not None:
            self.mins = mins
            self.secs = secs
            self.frames = frames
        else:
            raise ValueError('No se puede instanciar un timestamp sin un string o sin los valores')
        
    def __str__(self):
        return str(self.mins).zfill(2) + self.separator + str(self.secs).zfill(2) + self.separator + str(self.frames).zfill(2)
    
    def substract(self, timestamp):
        """
        Resta al timestamp el tiempo de otro timestamp

        Parameters
        ----------
        timestamp : Timestamp
            El timestamp a restar

        """

        self.frames = self.frames - timestamp.frames
        if self.frames < 0:
            self.frames += frames_por_segundo
            self.secs -= 1
        self.secs = self.secs - timestamp.secs
        if self.secs < 0:
            self.secs += segundos_por_minuto
            self.mins -= 1
        self.mins = self.mins - timestamp.mins
        return self
        
    def add(self, timestamp):
        """
        Suma al timestamp el tiempo de otro timestamp

        Parameters
        ----------
        timestamp : Timestamp
            El timestamp a sumar

        """

        self.frames = self.frames + timestamp.frames
        if self.frames >= frames_por_segundo:
            self.frames %= frames_por_segundo
            self.secs += 1
        self.secs = self.secs + timestamp.secs
        if self.secs >= segundos_por_minuto:
            self.secs %= segundos_por_minuto
            self.mins += 1
        self.mins = self.mins + timestamp.mins
        return self