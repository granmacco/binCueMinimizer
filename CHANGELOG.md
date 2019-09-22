# binCueMinimizer changelog

## v2.1.2
* Removed lossy.flac option due to minimal differences, both in size and quality, with the rest of options.

## v2.1.1
* Various bugfixes and display accomodations.

## v2.1.0
* Added command line menu
* Added lossy.flac option
* Added option for overwriting old CHDs
* Added windows icon (thank you @AlbertoCT!!)
* Various bugfixes

## v2.0.0
* Rewrote CUE parsing code
* Script is now able to identify unique file multitrack isos and split the tracks accordingly
* Added lossy.hard option
* Added u8wav option
* Modified execution order: The script will now work game-oriented, instead of phase-oriented. This means it won't try to parse all the cues at once, instead it will parse one cue, compress the game, and then advance to the next one.
* Added lots of log info

## v1.0.0
* First release
* Convert multitrack multibin isos into CHD and CHD lossy, preprocessing audio tracks with [lossyWAV](https://wiki.hydrogenaud.io/index.php?title=LossyWAV)