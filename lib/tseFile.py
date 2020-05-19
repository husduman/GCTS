import numpy as np
import os
from dateUtilities import date as du


def _read(filename):
    offset = []
    header = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            header.append(line)
            if 'COMPONENT' in line:
                component = line.split(": ")[1].split("\n")[0]
            if 'OFFSET' in line:
                offset.append((line.split(": ")[1].split("\n")[0]))
            if 'ENDOFHEADER' in line:
                break
    data = np.loadtxt(filename, comments='*')
    if component != 'all':
        obs   = data[:,0:2]
        dates = data[:,2:]
    else:
        obs   = data[:,0:6]
        dates = data[:,6:]
    return header, component, offset, obs, dates


def _write(newFilename, header, observations, dates):
    wrFile = open(newFilename,'w')
    for i in range(len(header)):
        wrFile.write(header[i])
        
    for j in range(len(observations[:,0])):
        for k in range(len(observations[0,:])):
            wrFile.write("%14.6f" % observations[j,k])
        for l in range(len(dates[0,:])):
            wrFile.write("%8i" % dates[j,l])
        wrFile.write("\n")

    if os.path.isfile(newFilename):
        print(" " + newFilename + " file has been created...")
    else:
        print("Something went wrong!\n")


def _stats(filename):
    header, component, offset, obs, dates = _read(filename)
    for line in header:
        if '* SITE' in line:
            siteID = line.split(": ")[1].split("\n")[0]
            break
    for line in header:
        if 'DATE FORMAT' in line:
            dateFormat = line.split(": ")[1].split("\n")[0]
            break

    datesNew  = []
    if dateFormat == 'mjd':
        firstOBSdate = du(dates[0],[],[],[],[],[],[],[],dateFormat,'yyyymmdd')._getdate()
        lastOBSdate  = du(dates[-1],[],[],[],[],[],[],[],dateFormat,'yyyymmdd')._getdate()
        datesNew  = dates
    elif dateFormat == 'decimalYear':
        firstOBSdate = du([],dates[0],[],[],[],[],[],[],dateFormat,'yyyymmdd')._getdate()
        lastOBSdate  = du([],dates[-1],[],[],[],[],[],[],dateFormat,'yyyymmdd')._getdate()
        for i in range(len(dates[:,0])):
            dd = du([],dates[i,0],[],[],[],[],[],[],dateFormat,'mjd')._getdate()
            datesNew.append(dd)
    elif dateFormat == 'yearANDdoy':
        firstOBSdate = du([],[],dates[0,0],[],[],dates[0,1],[],[],dateFormat,'yyyymmdd')._getdate()
        lastOBSdate  = du([],[],dates[-1,0],[],[],dates[-1,1],[],[],dateFormat,'yyyymmdd')._getdate()
        for i in range(len(dates[:,0])):
            dd = du([],[],dates[i,0],[],[],dates[i,1],[],[],dateFormat,'mjd')
            datesNew.append(dd._getdate())
    elif dateFormat == 'gweekANDdow':
        firstOBSdate = du([],[],[],[],[],[],dates[0,0],dates[0,1],dateFormat,'yyyymmdd')._getdate()
        lastOBSdate  = du([],[],[],[],[],[],dates[-1,0],dates[-1,1],dateFormat,'yyyymmdd')._getdate()
        for i in range(len(dates[:,0])):
            dd = du([],[],[],[],[],[],dates[i,0],dates[i,1],dateFormat,'mjd')
            datesNew.append(dd._getdate())
    elif dateFormat == 'yyyymmdd':
        firstOBSdate = dates[0,:]
        lastOBSdate  = dates[-1,:]
        for i in range(len(dates[:,0])):
            dd = du([],[],int(dates[i,0]),int(dates[i,1]),int(dates[i,2]),[],[],[],dateFormat,'mjd')
            datesNew.append(dd._getdate()) 
    else:
        print("Please check date format in your [?].tse file!")

    print(" --------------------------------------------------------------------------------------\n",
          " The statistical details of the time series file\n",
          "--------------------------------------------------------------------------------------\n",
          "Filename                           : " + os.path.abspath(filename))
    print(" First and Last Obs.   [yyyy/mm/dd] : from %d/%d/%d to %d/%d/%d" % \
        (firstOBSdate[0], firstOBSdate[1], firstOBSdate[2], \
         lastOBSdate[0], lastOBSdate[1], lastOBSdate[2]))
    print(" Length of Series         (in Days) : %d (%.2f years)" % \
        ((datesNew[-1] - datesNew[0] + 1), (datesNew[-1] - datesNew[0] + 1)/365.25))
    print(" Number of Observations   (in Days) : %d" % len(datesNew))
    print(" Percentage of Gaps                 : %.2f" % \
         ((1 - (len(datesNew) / (datesNew[-1] - datesNew[0] + 1)))*100))
    print(' Number of Offset                   : %d' % len(offset))
    print(" --------------------------------------------------------------------------------------\n")