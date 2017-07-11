set terminal postscript enhanced color
set output "../../../../Dokument/graphics/characteristics_results.ps"
set datafile separator ";"
set size 0.75, 0.75
set size ratio 0.4
set grid
set key off
#
set format x "%G"
set xrange [1E-15:1E-14]
set xtics 2E-15
set xlabel "error probability per 100 milli seconds"
#set logscale x
#
set yrange [1E9:1E12]
set ytics 2E11 nomirror
set format y "%G"
set ylabel "number of transfers"
#
set y2range [1E13:1E15]
set y2tics 2E14 nomirror
#set y2tics 1E25,2E29,1E30 nomirror
set y2label 'time (ms)' 
#
plot 'characteristics_paper_exact.csv' using 1:2 with linespoints pointtype 5 title 'expected successful transfers until crash' axes x1y1,\
     'characteristics_paper_exact.csv' using 1:3 with linespoints pointtype 11 title 'expected time in ms until crash' axes x1y2
