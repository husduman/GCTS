#!/usr/bin/env python3

import argparse, os, sys, math
pyGCTSpath="{}/lib".format(os.environ['pyGCTS'])
if pyGCTSpath not in sys.path:
    sys.path.append(pyGCTSpath)

import numpy as np
from dateUtilities import date as du

__prog__ = 'conv2tse.py'

__description__ = '''
conv2tse -> Converts to [?].tse file.

The script converts the time series or coordinate files produced by GPS/GNSS software
such as Gipsy-Oasis II, GipsyX, Bernese, and Gamit/Globk into its own format. It has
two main part including a header beginning with "*" and an observation part. In the 
observation part, the time label located at the end. That's why the GCTS_1.0 allows
one to use any of date formats which are year, month, day [yyyymmdd], modified julian
date [mjd], year and day of year [yearANDdoy], GPS week and day of week [gweekANDdow],
and decimal year [decimalYear].
'''

__epilog__ = '''
*** EXAMPLES ***

---------
:: Ex1 ::
    Original file is from GipsyX software, the series unit is meter, it has also an
    offset happened at 2014 1 1. Let the desired unit milimeter, dateFormat yyyymmdd,
    and all GPS component included for the station TEST.


    conv2tse.py -fname TEST.series -offset 2014 1 1 -unit m mm -dateFormat yyyymmdd

        ===================================================================
        conv2tse.py is running and using the parameters:
        ===================================================================
            filename : TEST.series
           fromWhich : gipsy
           component : all
              offset : 2014 1 1
                unit : m mm
          dateFormat : yyyymmdd
        ===================================================================

        TEST.tse file has been created...


    NOTE: As clearly seen in the command, although -fromWhich and -comp arguments have
          not been introduced in the command line, they are set default as gipsy and all,
          respectively.



---------
:: Ex2 ::
    An additional offset at 58605, only for east component, and date format as modified
    julian date [mjd] in addition to the example above.


    conv2tse.py -fname TEST.series -offset 56658 -offset 58605 \\
                -unit m mm -dateFormat yyyymmdd -comp east

        ===================================================================
        conv2tse.py is running and using the parameters:
        ===================================================================
            filename : TEST.series
           fromWhich : gipsy
           component : east
              offset : 56658
              offset : 58605
                unit : m mm
          dateFormat : mjd
        ===================================================================

        TESTeast.tse file has been created...


    NOTE: As stated in description of -offset argument, each of offset should be
          introduced under -offset argument. Moreover, the date format should be
          overlapped with the specified -dateFormat.



    This file is part of GCTS v1.0.

    GCTS v1.0 is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    GCTS v1.0 is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with GCTS v1.0.  If not, see <https://www.gnu.org/licenses/>.
'''

__author__ = 'Huseyin Duman'


def _getparser():
    parser = argparse.ArgumentParser(description=__description__,
                                     epilog=__epilog__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-fname", type=argparse.FileType('r') , 
                        required=True, nargs='+',
                        help = """Original time series file supplied by a user to be converted
                        to the suitable time series format (i.e. [?].tse file)
                        """)

    parser.add_argument("-fromWhich", type=str, 
                        default='gipsy', nargs='?',
                        choices=['gipsy','gamit','bernese'],
                        help="""From which source, a GPS/GNSS data processing software, an
                        original time series has been created. For instance, Gipsy-Oasis, GipsyX,
                        Bernese, Gamit/Globk etc.""")

    parser.add_argument("-comp", nargs="?", default='all', type=str,
                        choices=['all','east','north','up'],
                        help="""Which GPS component will be taken from the original time series
                        and be converted to the *.tse format (i.e. east, north, up, or all)""")

    parser.add_argument("-offset", nargs="+", type=str, action='append',
                        help="""Offset(s) date. The date format has to be same with specified
                        format by -dateFormat argument. For multiple offset entries, -offset                print("Something went wrong!")

                        argument has to be defined just before offset date.""")

    parser.add_argument("-unit", type=str, nargs=2,
                        help="""The argument has two variable. The first one is the unit of the
                        original time series file, and the other is that of output file. The
                        unit variables must be two of mm, cm, dm, m, km.""")

    parser.add_argument("-dateFormat", type=str, nargs="?",
                        help="""Date format is specified the time label in the output time series
                        file. It could be any of the format listed in discription above.""")
                
    parser.add_argument("-siteID", type=str, nargs='+', action='append',
                        help=""" 4-digit site IDs to be extracted. If source file from gipsy, this
                        argument could not be specified, that's why site ID is extracted from filename.
                        """)

    return parser

def _dispParser(args):
    print(" ========================================================================\n",
          os.path.basename(__file__) + " is running and using the parameters:\n",
        "========================================================================")
    for ss1 in range(len(args.fname)):
        print("    filename : " + args.fname[ss1].name)
    print("   fromWhich : " + args.fromWhich + "\n",
        "  component : " + args.comp)
    if args.offset is not None:
        for i in range(len(args.offset)):
           print("      offset : " + (" ".join(args.offset[i])))
    print("        unit : " + (" ".join(args.unit)))
    print("  dateFormat : " + args.dateFormat)
    print(" ========================================================================\n")


def main():
    args = _getparser().parse_args()
    _dispParser(args)

    # computing scale factor for the data conversion
    units = ['mm', 'cm', 'dm', 'm', 'km']
    transScale = np.array([[1.0e+0, 1.0e-1, 1.0e-2, 1.0e-3, 1.0e-6],
                           [1.0e+1, 1.0e+0, 1.0e-1, 1.0e-2, 1.0e-5],
                           [1.0e+2, 1.0e+1, 1.0e+0, 1.0e-1, 1.0e-4],
                           [1.0e+3, 1.0e+2, 1.0e+1, 1.0e+0, 1.0e-3],
                           [1.0e+6, 1.0e+5, 1.0e+4, 1.0e+3, 1.0e+0]])
    unitScale = transScale[units.index(args.unit[0]), units.index(args.unit[1])]
    
    if args.fromWhich == 'gipsy':
        for ss in range(len(args.fname)):
            siteID    = args.fname[ss].name.split("/")[-1][0:4]

            if args.comp == 'all':
                newFilename = siteID + ".tse"
            else:
                newFilename = siteID + args.comp + ".tse"

            wrFile = open(newFilename, "w")
            wrFile.write("* SITE         : " + siteID + "\n")
            wrFile.write("* COMPONENT    : " + args.comp + "\n")
            wrFile.write("* UNIT         : " + args.unit[1] + "\n")
            wrFile.write("* DATE FORMAT  : " + args.dateFormat + "\n")


            if args.offset is not None:
                for i in range(len(args.offset)):
                    wrFile.write("* OFFSET       : " + (" ".join(args.offset[i])) + "\n")

            data  = np.loadtxt(args.fname[ss], usecols=(1,2,3,4,5,6, 11, 12, 13))
            dates = data[:,6:]
            datesNew_temp  = []

            if args.dateFormat == 'yyyymmdd':
                for i in range(len(dates[:,0])):
                    datesNew_temp.append((dates[i,0],dates[i,1],dates[i,2]))
                del i
            else:
                for i in range(len(dates[:,0])):
                    dd = du([],[],int(dates[i,0]),int(dates[i,1]),int(dates[i,2]),[],[],[],"yyyymmdd",args.dateFormat)
                    datesNew_temp.append(dd._getdate())
                del i
            datesNew = np.asarray(datesNew_temp)
            if args.comp == 'all':
                wrFile.write("* DATA ORDER   : E N U sE sN sU date\n")
                wrFile.write("* COMMENT      : any comment could be added under this label.\n")
                wrFile.write("* ENDOFHEADER\n")
                obs   = data[:,0:6]
                if (args.dateFormat == 'mjd') or (args.dateFormat == 'decimalYear'):
                    for i in range(len(obs[:,0])):
                        for j in range(len(obs[0,:])):
                            wrFile.write("%14.6f" % (obs[i,j]*unitScale))
                        wrFile.write("%14.6f" % datesNew[i])
                        wrFile.write("\n")
                    del i,j
                else:
                    for i in range(len(obs[:,0])):
                        for j in range(len(obs[0,:])):
                            wrFile.write("%14.6f" % (obs[i,j]*unitScale))
                        for k in range(len(datesNew[0,:])):
                            wrFile.write("%8g" % datesNew[i,k])
                        wrFile.write("\n")
                    del i,j,k

            if args.comp == 'east':
                wrFile.write("* DATA ORDER   : E sE date\n")
                wrFile.write("* COMMENT      : any comment could be added under this label.\n")
                wrFile.write("* ENDOFHEADER\n")
                
                obs   = data[:,[0,3]]
                if (args.dateFormat == 'mjd') or (args.dateFormat == 'decimalYear'):
                    for i in range(len(obs[:,0])):
                        for j in range(len(obs[0,:])):
                            wrFile.write("%14.6f" % (obs[i,j]*unitScale))
                        wrFile.write("%14.6f" % datesNew[i])
                        wrFile.write("\n")
                    del i,j
                else:
                    for i in range(len(obs[:,0])):
                        for j in range(len(obs[0,:])):
                            wrFile.write("%14.6f" % (obs[i,j]*unitScale))
                        for k in range(len(datesNew[0,:])):
                            wrFile.write("%8g" % datesNew[i,k])
                        wrFile.write("\n")
                    del i,j,k

            if args.comp == 'north':
                wrFile.write("* DATA ORDER   : N sN date\n")
                wrFile.write("* COMMENT      : any comment could be added under this label.\n")
                wrFile.write("* ENDOFHEADER\n")
                
                obs   = data[:,[1,4]]
                if (args.dateFormat == 'mjd') or (args.dateFormat == 'decimalYear'):
                    for i in range(len(obs[:,0])):
                        for j in range(len(obs[0,:])):
                            wrFile.write("%14.6f" % (obs[i,j]*unitScale))
                        wrFile.write("%14.6f" % datesNew[i])
                        wrFile.write("\n")
                    del i,j
                else:
                    for i in range(len(obs[:,0])):
                        for j in range(len(obs[0,:])):
                            wrFile.write("%14.6f" % (obs[i,j]*unitScale))
                        for k in range(len(datesNew[0,:])):
                            wrFile.write("%8g" % datesNew[i,k])
                        wrFile.write("\n")
                    del i,j,k

            if args.comp == 'up':
                wrFile.write("* DATA ORDER   : U sU date\n")
                wrFile.write("* COMMENT      : any comment could be added under this label.\n")
                wrFile.write("* ENDOFHEADER\n")
                
                obs   = data[:,[2,5]]
                if (args.dateFormat == 'mjd') or (args.dateFormat == 'decimalYear'):
                    for i in range(len(obs[:,0])):
                        for j in range(len(obs[0,:])):
                            wrFile.write("%14.6f" % (obs[i,j]*unitScale))
                        wrFile.write("%14.6f" % datesNew[i])
                        wrFile.write("\n")
                    del i,j
                else:
                    for i in range(len(obs[:,0])):
                        for j in range(len(obs[0,:])):
                            wrFile.write("%14.6f" % (obs[i,j]*unitScale))
                        for k in range(len(datesNew[0,:])):
                            wrFile.write("%8g" % datesNew[i,k])
                        wrFile.write("\n")
                    del i,j,k

            wrFile.close()
            if os.path.isfile(newFilename):
                print(" " + newFilename + " file has been created...")
            else:
                print("Something went wrong!")
        print("\n\n")

    elif args.fromWhich == 'gamit':
        for ss in range(len(args.siteID[0])):
            siteID = args.siteID[0][ss]


            obs_temp   = []
            s_obs_temp = []
            dates_temp = []
            for i in range(len(args.fname)):
                with open(args.fname[i].name, 'r') as f:
                        for line in f.readlines():
                            if 'pbo. ' + siteID + '_GPS' in line:
                                dates_temp.append((line.split("|")[0].split()[3:6]))
                                obs_temp.append((line.split("|")[2].split("\n")[0].split()[0:3]))
                                s_obs_temp.append((line.split("|")[2].split("\n")[0].split()[3:6]))
            datesNew_temp = []
            if args.dateFormat == 'yyyymmdd':
                for i in range(len(dates_temp)):
                    datesNew_temp.append((int(dates_temp[i][0]),int(dates_temp[i][1]),int(dates_temp[i][2])))
                del i
            else:          
                for i in range(len(dates_temp)):
                    dd = du([],[],int(dates_temp[i][0]),int(dates_temp[i][1]),int(dates_temp[i][2]),[],[],[],"yyyymmdd", args.dateFormat)
                    datesNew_temp.append(dd._getdate())
                del i

            datesNew = np.asarray(datesNew_temp)
            obs   = np.asarray(obs_temp,   dtype=float)
            s_obs = np.asarray(s_obs_temp, dtype=float)
            data  = np.concatenate((obs - obs[0,:], s_obs), axis=1)


            if args.comp == 'all':
                newFilename = siteID + ".tse"
            else:
                newFilename = siteID + args.comp + ".tse"

            wrFile = open(newFilename, "w")
            wrFile.write("* SITE         : " + siteID + "\n")
            wrFile.write("* COMPONENT    : " + args.comp + "\n")
            wrFile.write("* UNIT         : " + args.unit[1] + "\n")
            wrFile.write("* DATE FORMAT  : " + args.dateFormat + "\n")

            if args.offset is not None:
                for i in range(len(args.offset)):
                    wrFile.write("* OFFSET       : " + (" ".join(args.offset[i])) + "\n") 


            if args.comp == 'all':
                wrFile.write("* DATA ORDER   : E N U sE sN sU date\n")
                wrFile.write("* COMMENT      : any comment could be added under this label.\n")
                wrFile.write("* ENDOFHEADER\n")
                
                obsNew = data[:,[1,0,2,4,3,5]]
                if (args.dateFormat == 'mjd') or (args.dateFormat == 'decimalYear'):
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        wrFile.write("%14.6f" % datesNew[i])
                        wrFile.write("\n")
                    del i,j
                else:
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        for k in range(len(datesNew[0,:])):
                            wrFile.write("%8g" % datesNew[i,k])
                        wrFile.write("\n")
                    del i,j,k

            if args.comp == 'east':
                wrFile.write("* DATA ORDER   : E sE date\n")
                wrFile.write("* COMMENT      : any comment could be added under this label.\n")
                wrFile.write("* ENDOFHEADER\n")
                
                obsNew = data[:,[1,4]]
                if (args.dateFormat == 'mjd') or (args.dateFormat == 'decimalYear'):
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        wrFile.write("%14.6f" % datesNew[i])
                        wrFile.write("\n")
                    del i,j
                else:
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        for k in range(len(datesNew[0,:])):
                            wrFile.write("%8g" % datesNew[i,k])
                        wrFile.write("\n")
                    del i,j,k

            if args.comp == 'north':
                wrFile.write("* DATA ORDER   : N sN date\n")
                wrFile.write("* COMMENT      : any comment could be added under this label.\n")
                wrFile.write("* ENDOFHEADER\n")
                
                obsNew = data[:,[0,3]]
                if (args.dateFormat == 'mjd') or (args.dateFormat == 'decimalYear'):
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        wrFile.write("%14.6f" % datesNew[i])
                        wrFile.write("\n")
                    del i,j
                else:
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        for k in range(len(datesNew[0,:])):
                            wrFile.write("%8g" % datesNew[i,k])
                        wrFile.write("\n")
                    del i,j,k

            if args.comp == 'up':
                wrFile.write("* DATA ORDER   : U sU date\n")
                wrFile.write("* COMMENT      : any comment could be added under this label.\n")
                wrFile.write("* ENDOFHEADER\n")
                
                obsNew = data[:,[2,5]]
                if (args.dateFormat == 'mjd') or (args.dateFormat == 'decimalYear'):
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        wrFile.write("%14.6f" % datesNew[i])
                        wrFile.write("\n")
                    del i,j
                else:
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        for k in range(len(datesNew[0,:])):
                            wrFile.write("%8g" % datesNew[i,k])
                        wrFile.write("\n")
                    del i,j,k

            wrFile.close()
            if os.path.isfile(newFilename):
                print(" " + newFilename + " file has been created...")
            else:
                print("Something went wrong!")
        print("\n\n")  


    elif args.fromWhich == 'bernese':
        for ss in range(len(args.siteID[0])):
            siteID = args.siteID[0][ss]

            obs_temp   = []
            s_obs_temp = []
            dates_temp = [] 
            for i in range(len(args.fname)):
                idx = 0
                lineIDX = 0
                groupoflines = None
                #print(args.fname[i].name)
                with open(args.fname[i].name, 'r') as f:
                    for line in f:
                        if 'Reference epoch:' in line:
                            dates_temp.append(line.split()[2].split("-"))
                        if groupoflines is None:
                            if siteID + '                  X' in line:   
                                groupoflines = []
                                groupoflines.append(line)
                                lineIDX = idx
                        elif line == '\n':
                            if lineIDX + 7 == idx:
                                break
                        else:
                            groupoflines.append(line)
                        idx += 1

                obs_temp.append([groupoflines[0].split()[3], groupoflines[1].split()[2], groupoflines[2].split()[2]])
                s_obs_temp.append([groupoflines[5].split()[4], groupoflines[4].split()[4], groupoflines[3].split()[4]])
            lat = float(groupoflines[4].split()[2]) * (math.pi / 180)
            lon = float(groupoflines[5].split()[2]) * (math.pi / 180)
            obsXYZ = np.asarray(obs_temp, dtype=float) - np.asarray(obs_temp[0], dtype=float)
            s_obs = np.asarray(s_obs_temp, dtype=float)

            transMat = np.array([[             -math.sin(lon),               -math.cos(lon), 0],
                                [-math.sin(lat)*math.cos(lon), -math.sin(lat)*math.sin(lon), math.cos(lat)],
                                [ math.cos(lat)*math.cos(lon),  math.cos(lat)*math.sin(lon), math.sin(lat)]])
            obsENU = ((transMat @ obsXYZ.T).T)

            datesNew_temp = []
            if args.dateFormat == 'yyyymmdd':
                for i in range(len(dates_temp)):
                    datesNew_temp.append((int(dates_temp[i][0]),int(dates_temp[i][1]),int(dates_temp[i][2])))
                del i
            else:          
                for i in range(len(dates_temp)):
                    dd = du([],[],int(dates_temp[i][0]),int(dates_temp[i][1]),int(dates_temp[i][2]),[],[],[],"yyyymmdd", args.dateFormat)
                    datesNew_temp.append(dd._getdate())
                del i
            datesNew = np.asarray(datesNew_temp)
            data     = np.concatenate((obsENU, s_obs), axis=1)

            if args.comp == 'all':
                newFilename = siteID + ".tse"
            else:
                newFilename = siteID + args.comp + ".tse"

            wrFile = open(newFilename, "w")
            wrFile.write("* SITE         : " + siteID + "\n")
            wrFile.write("* COMPONENT    : " + args.comp + "\n")
            wrFile.write("* UNIT         : " + args.unit[1] + "\n")
            wrFile.write("* DATE FORMAT  : " + args.dateFormat + "\n")

            if args.offset is not None:
                for i in range(len(args.offset)):
                    wrFile.write("* OFFSET       : " + (" ".join(args.offset[i])) + "\n") 


            if args.comp == 'all':
                wrFile.write("* DATA ORDER   : E N U sE sN sU date\n")
                wrFile.write("* COMMENT      : any comment could be added under this label.\n")
                wrFile.write("* ENDOFHEADER\n")
                
                obsNew = data
                if (args.dateFormat == 'mjd') or (args.dateFormat == 'decimalYear'):
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        wrFile.write("%14.6f" % datesNew[i])
                        wrFile.write("\n")
                    del i,j
                else:
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        for k in range(len(datesNew[0,:])):
                            wrFile.write("%8g" % datesNew[i,k])
                        wrFile.write("\n")
                    del i,j,k

            if args.comp == 'east':
                wrFile.write("* DATA ORDER   : E sE date\n")
                wrFile.write("* COMMENT      : any comment could be added under this label.\n")
                wrFile.write("* ENDOFHEADER\n")
                
                obsNew = data[:,[0,3]]
                if (args.dateFormat == 'mjd') or (args.dateFormat == 'decimalYear'):
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        wrFile.write("%14.6f" % datesNew[i])
                        wrFile.write("\n")
                    del i,j
                else:
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        for k in range(len(datesNew[0,:])):
                            wrFile.write("%8g" % datesNew[i,k])
                        wrFile.write("\n")
                    del i,j,k

            if args.comp == 'north':
                wrFile.write("* DATA ORDER   : N sN date\n")
                wrFile.write("* COMMENT      : any comment could be added under this label.\n")
                wrFile.write("* ENDOFHEADER\n")
                
                obsNew = data[:,[1,4]]
                if (args.dateFormat == 'mjd') or (args.dateFormat == 'decimalYear'):
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        wrFile.write("%14.6f" % datesNew[i])
                        wrFile.write("\n")
                    del i,j
                else:
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        for k in range(len(datesNew[0,:])):
                            wrFile.write("%8g" % datesNew[i,k])
                        wrFile.write("\n")
                    del i,j,k

            if args.comp == 'up':
                wrFile.write("* DATA ORDER   : U sU date\n")
                wrFile.write("* COMMENT      : any comment could be added under this label.\n")
                wrFile.write("* ENDOFHEADER\n")
                
                obsNew = data[:,[2,5]]
                if (args.dateFormat == 'mjd') or (args.dateFormat == 'decimalYear'):
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        wrFile.write("%14.6f" % datesNew[i])
                        wrFile.write("\n")
                    del i,j
                else:
                    for i in range(len(obsNew[:,0])):
                        for j in range(len(obsNew[0,:])):
                            wrFile.write("%14.6f" % (obsNew[i,j]*unitScale))
                        for k in range(len(datesNew[0,:])):
                            wrFile.write("%8g" % datesNew[i,k])
                        wrFile.write("\n")
                    del i,j,k

            wrFile.close()
            if os.path.isfile(newFilename):
                print(" " + newFilename + " file has been created...")
            else:
                print("Something went wrong!")
        print("\n\n")
    


if __name__ == "__main__":
    main()
