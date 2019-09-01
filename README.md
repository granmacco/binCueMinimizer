# binCueMinimizer
Python 3 script to compress .bin/.cue isos to .chd format 

## Getting Started

binCueMinimizer is a script that preprocesses cue files in order 
to find isos with audio tracks, in order to treat them with lossyWAV,
a lossy encoder that optimizes original wavs to be more compressed
when converted to FLAC, which is the format CHDMAN uses.

### Prerequisites

Apart from Python 3, it requires ffmpeg and lossyWAV, along with chdman.

* [ffmpeg](https://ffmpeg.org/) - Needed for BIN-WAV conversion
* [lossyWAV](https://wiki.hydrogenaud.io/index.php?title=LossyWAV) - Needed for WAV processing
* [chdman](https://www.mamedev.org/) - Distributed as part of MAME Tools

## How to use

First, copy the this repo's contents, ffmpeg, chdman and lossyWAV to
the folder you have your .bin and .cue files. Then, depending of your
OS or preferences, execute:

### Windows
```
binCueMinimizer.bat
```

### Unix
```
./binCueMinimizer.sh
```

### Windows
```
python binCueMinimizer.py
```

The script will generate CHD files in the same path. Also, if it can
compress any further the audio tracks, it will generate a .lossy.CHD file.
It's up to you compare both files and decide which one to keep, but keep 
in mind lossyWAV is a lossy codec, so you are losing audio date when you 
use it, so it's not ideal for archiving purposes. CHD itself, on the other
hand, is lossless and reversible to the original .bin and .cue.

In case something goes wrong, you can check the binCueMinimizer.log that
will appear in the same path as the script. In this file, ths script dumps
info about the process, helping you in the task of finding what went wrong.

## License

The script is licensed under 
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) 2019

You can check the license terms on http://creativecommons.org/licenses/by-nc-sa/4.0/ 
or checking the LICENSE file.
