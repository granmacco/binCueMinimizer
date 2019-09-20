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

from binCueMinimizer.binCueMinimizer import BinCueMinimizer
from binCueMinimizer.cueFile import CueFile
from binCueMinimizer import osUtils
import os 
import platform

def menu():
    """
    Función que muestra el menu

    """
    
    print("\n")
    print("BIN CUE MINIMIZER")
    print("#################")
    print("\n")
    print("Seleccione un método de compresión")
    print("\t1 - CHD sin compresión        Compresión: •       Pérdida:         Extensión: .CHD")
    print("\t2 - CHD lossywav              Compresión: •••     Pérdida: †       Extensión: .lossy.CHD")
    print("\t3 - CHD lossywav hard         Compresión: ••••    Pérdida: ††      Extensión: .lossy.hard.CHD")
    print("\t4 - CHD mierdikrusterburger   Compresión: •••••   Pérdida: †††††   Extensión: .u8.CHD")
    print("\t5 - Probar todos (No recomendado para muchos ficheros, tardará MUCHO en terminar)")
    print("\t0 - Salir")
    print("\n")
    print("Si no sabe por cual decantarse, le recomiendo la opción 2 - CHD lossywav, o pruebe")
    print("la opción 5 para comprobar las diferencias entre cada uno de los diferentes formatos")
    print("\n")
    
def main():
    is_windows = platform.system() == 'Windows'
    if not is_windows: 
        command = 'clear'
    else:
        command = 'cls' 
    os.system(command)
    opcion = -1
    while int(opcion) != 0:
        menu()
        opcion = input("Seleccione una opción » ")
        if opcion == 0:
            break;
        
        try:
            if 0 < int(opcion) <= 5:
                if int(opcion) == 5:
                    modos = range(1, 5)
                else:
                    modos = [int(opcion)]
                cue_paths = osUtils.list_files(extension='cue')
                for cue_path in cue_paths:
                    for modo in modos:
                        minimizer = BinCueMinimizer(modo)
                        minimizer.check_dependencies()
                        minimizer.minimise_cue(CueFile(cue_path))
        except ValueError:
            print("Por favor, introduzca una opción del 0 al 5")
            opcion = -1
                
if __name__ == '__main__':
    main()