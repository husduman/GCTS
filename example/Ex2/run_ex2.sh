#!/bin/bash

# Let assume here that the east component has an artificial offset
# at 2015.9826 and analyze only this component.

fname=ONSA.series


# The first step
# Convert external format into the readable time-series format
# for the GCTS v1.0

conv2tse.py \
	-fname $fname \
	-unit m mm \
	-dateFormat decimalYear \
	-comp east \
	-offset 2015.9826


# The second step
# Remove outliers for the desired component and write the outlier-
# free time-series into the same format.

removeOutliers.py \
	-fname ${fname:0:4}east.tse \
	-writeOutliers \
	-comp east 


# The last step
# analyze GPS/GNSS campaign time-series

	evalCampaign.py \
		-fname ${fname:0:4}east.tse \
		-nRND 30 \
		-repeat 100 \
		-writeModel



