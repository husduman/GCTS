#!/bin/bash

siteID=ZIMM


# The first step
# Convert external format into the readable time-series format
# for the GCTS v1.0

conv2tse.py \
	-fname glorgs/*.org \
	-unit m mm \
	-fromWhich gamit \
	-dateFormat mjd \
	-siteID $siteID


# The second step
# Remove outliers for the desired component and write the outlier-
# free time-series into the same format.

removeOutliers.py \
	-fname ${siteID}.tse \
	-writeOutliers \
	-comp east north up


# The last step
# analyze GPS/GNSS campaign time-series

for comp in east north up
do
	evalCampaign.py \
		-fname ${siteID}${comp}.tse \
		-nRND 30 \
		-repeat 100 \
		-writeModel
done







