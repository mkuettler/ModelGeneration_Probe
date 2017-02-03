set terminal postscript enhanced color
set output "/Users/linda/Mercurial/Publikationen/HotOS17/Dokument/graphics/characteristics_results.ps" 
set datafile separator ";"
set size 0.75, 0.75
set size ratio 0.4
set grid
set key off
set format x "%G"
set xrange [0:1E-6]
set xtics 2E-7
set xlabel "error probability per 0.1 milli seconds"
set yrange [0:15000] 
set ytics 2000 nomirror
set ylabel "number of sends"
set y2range [21000:270000]
set y2tics 25000,50000,260000 nomirror
set y2label 'time (ms)' 
plot 'characteristics_paper.csv' using 1:2 with linespoints pointtype 5 title 'expected successful sends until crash' axes x1y1,\
     'characteristics_paper.csv' using 1:3 with linespoints pointtype 11 title 'expected time in ms until crash' axes x1y2
