.PHONY: setup test sample all clean

setup:
	./setup.sh

test:            ## regression fixture: every element and chart type
	./hh qa _features --docx-preview

sample:          ## full sample report with live link check
	./hh make sample-decision-quality --docx-preview

all:             ## rebuild and check every report
	./hh batch --all

clean:
	rm -rf build
