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

### You know what you're doing
```
python binCueMinimizer.py
```

The script will generate CHD files in the same path. Also, if it can
compress any further the audio tracks, it will generate a .lossy.CHD file.

It's up to you compare both files and decide which one to keep, but keep 
in mind lossyWAV is a lossy codec, so you are losing audio data when you 
use it, so it's not ideal for archiving purposes. CHD itself, on the other hand,
is lossless and reversible to the original .bin and .cue.

In case something goes wrong, you can check the binCueMinimizer.log that
will appear in the same path as the script. In this file, ths script dumps
info about the process, helping you in the task of finding what went wrong.

## What to expect

In my tests, the compression ratio was 64% in average, meaning a 55% performance
increase in average. This way, 100 gigabytes of data will occupy around 65 gigabytes.
With some isos filled with audio tracks, its size went from 516 megabytes to 177 megabytes, 
a performance increase of 191%! You can check an expected size result [here] (https://pastebin.com/9u37am8N)

This is particularly interesting when using systems with reduced drive space, such as
Raspberry Pi, RetroPie, Batocera or Recalbox. Less data occupied means more space to
fill with something else!

And in case you're wondering, .CHD is compatible with [PCSX ReARMed] (https://docs.libretro.com/library/pcsx_rearmed/), [PicoDrive] (https://docs.libretro.com/library/picodrive/), [FlyCast and Reicast] (https://docs.libretro.com/library/flycast/)

## License

The script is licensed under 
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) 2019

You can check the license terms on http://creativecommons.org/licenses/by-nc-sa/4.0/ 
or checking the LICENSE file.
