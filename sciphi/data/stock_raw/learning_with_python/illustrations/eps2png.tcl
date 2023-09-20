#!/usr/bin/tclsh

foreach file [glob *.fig] {
    set outfile [file root $file].png
    puts "Converting $file, creating $outfile."
    exec fig2dev -L png -m 1.2727 $file $outfile
}