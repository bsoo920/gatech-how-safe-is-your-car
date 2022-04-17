# git add vehicle2018.csv
# git commit -am "add vehicle2018.csv"
# git push

# vehicle2001.csv \
# vehicle2002.csv 

for x in \
vehicle2003.csv \
vehicle2004.csv \
vehicle2005.csv \
vehicle2006.csv \
vehicle2007.csv \
vehicle2008.csv \
vehicle2009.csv \
vehicle2010.csv \
vehicle2011.csv \
vehicle2012.csv \
vehicle2013.csv \
vehicle2014.csv \
vehicle2017.csv
do
  echo "$x **********"
  git add $x
  git commit -am "add $x"
  git push
done
