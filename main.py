# coding=cp1252
#
# main.py
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
import platform
from binCueMinimizer.binCueMinimizer import BinCueMinimizer
from binCueMinimizer.cueFile import CueFile
from binCueMinimizer import osUtils
from binCueMinimizer.consts import MODE_NORMAL_CHD, MODE_LOSSYWAV,\
    MODE_LOSSYWAV_HARD, MODE_U8WAV, MODE_EVERYTHING, EXIT,\
    SWITCH_FORCE
from termcolor import colored, cprint

def menu(force_enabled):
    """
    Función que muestra el menu

    """
    
    print("BIN CUE MINIMIZER")
    print("¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯")
    print("Seleccione un método de compresión:")
    print("\t" + str(MODE_NORMAL_CHD)    + " - CHD sin compresión adicional   Extensión: .CHD")
    print("\t    Compresión: •                  Pérdida:")
    print("\t" + str(MODE_LOSSYWAV)      + " - CHD lossywav                   Extensión: .lossy.CHD")
    print("\t    Compresión: ••                 Pérdida: †")
    print("\t" + str(MODE_LOSSYWAV_HARD) + " - CHD lossywav hard              Extensión: .lossy.hard.CHD")
    print("\t    Compresión: •••                Pérdida: ††")
    print("\t" + str(MODE_U8WAV)         + " - CHD mierdikrusterburger        Extensión: .u8.CHD")
    print("\t    Compresión: •••••              Pérdida: †††††")
    print("\t" + str(MODE_EVERYTHING)    + " - Probar todos (¡¡OJO!! Procesamiento MUY lento)")
    print("\t" + str(SWITCH_FORCE)    + " - Sobreescribir CHDs anteriores (Estado: " + ("HABILITADO" if force_enabled else "deshabilitado") + ")")
    print("\t" + str(EXIT)               + " - Salir")
    print("Se recomienda utilizar la opción " + str(MODE_LOSSYWAV) + " para una compresión aceptable,")
    print("o probar todas (" + str(MODE_EVERYTHING) + ") para que saques tus propias conclusiones.")
    print("")
def warning(opcion):
    if opcion == MODE_U8WAV:
        print("")
        cprint("!!!!!!!!!!!!!!!!!!!!!!!!!! PRECAUCION !!!!!!!!!!!!!!!!!!!!!!!!!!", 'yellow', attrs=['reverse', 'bold', 'blink'])
        print("")
        print("El método mierdikrusterburger es un sistema de compresión MUY extremo")
        print("Sólo se recomienda su utilización con altavoces de baja calidad o si") 
        print("tiene un grave problema de espacio en el dispositivo de emulación")
        print("")
        cprint("!!!!!!!!!!!!!!!!!!!!!!!!!! PRECAUCION !!!!!!!!!!!!!!!!!!!!!!!!!!", 'yellow', attrs=['reverse', 'bold', 'blink'])
        print("")
        seguro = input("¿Está seguro de querer continuar? (s/N) » ")
        if seguro.casefold() != "s".casefold():
            raise ValueError("Volviendo al menú principal...")
    
def main():
    force_enabled = False
    is_windows = platform.system() == 'Windows'
    if not is_windows: 
        command = 'clear'
    else:
        command = 'cls' 
    os.system(command)
    opcion = -1
    while int(opcion) != 0:
        menu(force_enabled)
        opcion = input("Seleccione una opción » ")
        if opcion == 0:
            break;
        try:
            warning(int(opcion))
            if 0 < int(opcion) <= 5:
                if int(opcion) == 5:
                    modos = range(1, 5)
                else:
                    modos = [int(opcion)]
                cue_paths = osUtils.list_files(extension='cue')
                for cue_path in cue_paths:
                    for modo in modos:
                        minimizer = BinCueMinimizer(operation_mode=modo, overwrite_chd=force_enabled)
                        minimizer.check_dependencies()
                        minimizer.minimise_cue(CueFile(cue_path))
            elif int(opcion) == 6:
                force_enabled = not force_enabled
        except ValueError:
            print("Por favor, introduzca una opción del 0 al 6")
            opcion = -1
                
if __name__ == '__main__':
    main()