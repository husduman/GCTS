#!/bin/bash

fname=ONSA.series


# The first step
# Convert external format into the readable time-series format
# for the GCTS v1.0

conv2tse.py \
	-fname $fname \
	-unit m mm \
	-dateFormat yyyymmdd


# The second step
# Remove outliers for the desired component and write the outlier-
# free time-series into the same format.

removeOutliers.py \
	-fname ${fname:0:4}.tse \
	-writeOutliers \
	-comp east north up


# The last step
# analyze GPS/GNSS campaign time-series

for comp in east north up
do
	evalCampaign.py \
		-fname ${fname:0:4}${comp}.tse \
		-nRND 30 \
		-repeat 100 \
		-writeModel
done







