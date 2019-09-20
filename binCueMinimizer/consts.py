# coding=cp1252
#
# consts.py
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

version="2.0"
# 75 frames por segundo, fuente: https://en.wikipedia.org/wiki/Track_(optical_disc)
frames_por_segundo = 75
segundos_por_minuto = 60
logging.basicConfig(level=logging.INFO, filename="binCueMinimizer.log", format='%(asctime)s - binCueMinimizer-' + version + ' %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

Framesizes={
    'AUDIO'.casefold():      2352,
    'MODE1/2352'.casefold(): 2352,
    'MODE2/2352'.casefold(): 2352,
    'CDI/2352'.casefold():   2352,
    'CDG'.casefold():        2448,
    'MODE1/2048'.casefold(): 2048,
    'MODE2/2336'.casefold(): 2336,
    'CDI/2336'.casefold():   2336
    }

