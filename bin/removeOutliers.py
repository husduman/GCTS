#!/usr/bin/env python3

import argparse, os, sys, statistics
pyGCTSpath="{}/lib".format(os.environ['pyGCTS'])
if pyGCTSpath not in sys.path:
    sys.path.append(pyGCTSpath)

import numpy as np
import tseFile as tf
import scipy.linalg as la
import leastSquares as ls
from designMat import designMat as dm

__prog__ = 'removeOutliers.py'

__description__ = '''
removeOutliers -> Removes outliers in the series file.

The scripts removes the outliers in the converted time series file using one of the
Interquartile range, median and Nsigma methods. If one or more outliers are detected
by the outlier detection method, they are removed from the series file, and outliers
are written into a seperate time series file named [?]_outliers.tse by specifiying
-writeOutliers argument.
'''

__epilog__ = '''
*** EXAMPLES ***

---------
:: Ex1 ::
    Let the time series file includes all components for the TEST station. To remove
    outliers according to the IQrange (interquartile range) method.


    removeOutliers.py -fname TEST.tse -comp east north up -writeOutliers

        ===================================================================
        removeOutliers.py is running and using the parameters:
        ===================================================================
            filename : TEST.tse
              method : IQrange
               scale : 3
           component : east
           component : north
           component : up
        ===================================================================


                ******* east *******
        # 	 Method 	 Scale 		 nOutliers
        ---	--------	-------		-----------
        1	IQrange	           3		     0


        TESTeast.tse file has been created...

                ******* north *******
        # 	 Method 	 Scale 		 nOutliers
        ---	--------	-------		-----------
        1	IQrange	           3		     0


        TESTnorth.tse file has been created...

                ******* up *******
        # 	 Method 	 Scale 		 nOutliers
        ---	--------	-------		-----------
        1	IQrange	           3		     1
        2	IQrange	           3		     0


        TESTup.tse file has been created...
        TESTup_outliers.tse file has been created...


    NOTE: As clearly seen in the command, although -scale and -method arguments have
          not been introduced in the command line, they are set default as 3 and IQrange,
          respectively. Component order under -comp flag is not necessary, so it could be
          as up east north.


---------
:: Ex2 ::
    Let's remove the outliers only for up component with the same configuration in Ex1.


    removeOutliers.py -fname TESTup.tse -comp up -writeOutliers

        ===================================================================
        removeOutliers.py is running and using the parameters:
        ===================================================================
            filename : TESTup.tse
              method : IQrange
               scale : 3
           component : up
        ===================================================================


                ******* up *******
        # 	 Method 	 Scale 		 nOutliers
        ---	--------	-------		-----------
        1	IQrange	           3		     1
        2	IQrange	           3		     0


        TESTup.tse file has been created...
        TESTup_outliers.tse file has been created...


    NOTE: Although time series file contains only up component, -comp flag has been introduced.
          That is because the -comp flag is a required argument.


---------
:: Ex3 ::
    Introducing some cycles to examples above.


    removeOutliers.py -fname TESTup.tse -comp up -writeOutliers -periods 13.66 T1

        ===================================================================
        removeOutliers.py is running and using the parameters:
        ===================================================================
            filename : TESTup.tse
              method : IQrange
               scale : 3
           component : up
             periods : 13.66
             periods : T1
        ===================================================================


                ******* up *******
        # 	 Method 	 Scale 		 nOutliers
        ---	--------	-------		-----------
        1	IQrange	           3		     0


        TESTup.tse file has been created...




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
                        required=True, nargs='?',
                        help = """[?](comp).tse file name to be removed outliers, which
                        could contain either only one GPS component or all GPS component.
                        """)

    parser.add_argument("-method", type=str, 
                        default='IQrange', nargs='?',
                        choices=['IQrange','median','Nsigma'],
                        help="""To choose which method will be used to detect and remove
                        outliers from the time series. The methods are IQrange, median, and
                        Nsigma.""")

    parser.add_argument("-scale", nargs="?", default=3, type=float,
                        help="""Scale factor used to determine the upper and lower limits 
                        in the outlier(s) detection analysis.                        
                        """)

    parser.add_argument("-comp", nargs="+", type=str, required=True,
                        help="""Outliers in which GPS component to be removed. The argument
                        is required and suitable for multiple entries. Multiple entry order
                        is not necessary.""")

    parser.add_argument("-periods", type=str, nargs='+',
                        default=[],
                        help="""Seasonal periodicities to detrend the data. Frequently used
                        cycles is tropical, chandler, draconitic years, and its/theirs
                        harmonics. These have some label to make the usage easier. The label
                        has two digit. The first digit is the first letter of corresponding
                        cycle (i.e. one of T, C, and D), and the second digit is for the number
                        of harmonics. For example, T2 stands for from a tropical year through
                        its second harmonic (e.g. 365.2500 and 183.6250 days). Another example
                        is C1 which is for a chandler year (e.g. 433 days). Beyond these label
                        one may introduce one or more cycle as float number in days
                        (e.g. 14.66 days). Please check Ex3.""")

    parser.add_argument("-writeOutliers", action='store_true',
                        help="A choice to be write down the outliers or not")

    return parser

def _dispParser(args):
    print(" ===================================================================\n",
          os.path.basename(__file__) + " is running and using the parameters:\n",
        "===================================================================")
    print("    filename : " + args.fname.name + "\n",
          "     method : " + args.method + "\n",
          "      scale : " + str(args.scale))
    for i in args.comp:
        print("   component : " + i)
    if args.periods is not None:
        for j in args.periods:
            print("     periods : " + j)
    print(" ===================================================================\n")
    


def main():
    args = _getparser().parse_args()
    _dispParser(args)    
    
    for i in args.comp:
        A,_ = dm(args.fname.name, args.periods, 365.25)._coefficients()
        header, _, _, obs, dates = tf._read(args.fname.name)
        for line in header:
            if 'COMPONENT' in line:
                component = line.split(": ")[1].split("\n")[0]
                break
        if component == 'all':
            if i == 'east':
                col = [0,3]
            elif i == 'north':
                col = [1,4]
            elif i == 'up':
                col = [2,5]
        elif component == 'east' or component == 'north' or component == 'up':
            col = [0,1]
        else:
            print("Please check your component flag!")
            sys.exit()



        print("\n         ******* %s *******" % i)
        print(" # \t Method \t Scale \t\t nOutliers")
        print("---\t--------\t-------\t\t-----------")
        iteration   = 0
        outlierOBS  = np.empty([0,2])
        outlierDATE = np.empty([0,len(dates[0,:])])
        cond = True
        L = obs[:,col]
        if args.method == 'IQrange':            
            while cond:
                iteration += 1
                _, _, _, resid = ls._lse(A, L[:,0])
                sorted_resid = np.sort(resid, axis=0, kind='quicksort', order=None)

                IQ = (sorted_resid[int(np.floor(0.75 * len(resid)))] - 
                      sorted_resid[int(np.floor(0.25 * len(resid)))])
                MED = sorted_resid[int(np.floor(0.50 * len(resid)))]
                del sorted_resid

                lowerBoundary = MED - (args.scale * IQ)
                upperBoundary = MED + (args.scale * IQ)

                lowerBool     = lowerBoundary < resid
                upperBool     = upperBoundary > resid
                nonOutlBool   = lowerBool * upperBool
                nOutlires     = len(resid) - sum(nonOutlBool)
                nonOutlBool_idx = [i for i, val in enumerate(nonOutlBool == False) if val]
                del resid, lowerBoundary, upperBoundary, lowerBool, upperBool, MED, IQ

                if nOutlires == 0:
                    cond = False
                else:
                    outlierOBS  = np.append(outlierOBS, L[nonOutlBool_idx,:], axis=0)
                    outlierDATE = np.append(outlierDATE, dates[nonOutlBool_idx,:], axis=0)
                    A     = np.delete(A, nonOutlBool_idx, axis=0)
                    L     = np.delete(L, nonOutlBool_idx, axis=0)
                    dates = np.delete(dates, nonOutlBool_idx, axis=0)
                    

                print("%2d\t%7s\t%12d\t\t%6d" % (iteration, args.method,args.scale,nOutlires))
                del nOutlires, nonOutlBool_idx, nonOutlBool     

        elif args.method == 'median':
            while cond:
                iteration += 1
                _, _, _, resid = ls._lse(A, L[:,0])
                median_ith = np.abs(resid - statistics.median(resid))
                if statistics.median(median_ith) == 0:
                    MAD = (1.2533 / len(resid)) * sum(median_ith)
                else:
                    MAD = 1.4826 * statistics.median(median_ith)

                nonOutlBool   = (median_ith < args.scale*MAD)
                nOutlires     = len(resid) - sum(nonOutlBool)
                nonOutlBool_idx = [i for i, val in enumerate(nonOutlBool == False) if val]
                del resid, MAD

                if nOutlires == 0:
                    cond = False
                else:
                    outlierOBS  = np.append(outlierOBS, L[nonOutlBool_idx,:], axis=0)
                    outlierDATE = np.append(outlierDATE, dates[nonOutlBool_idx,:], axis=0)
                    A     = np.delete(A, nonOutlBool_idx, axis=0)
                    L     = np.delete(L, nonOutlBool_idx, axis=0)
                    dates = np.delete(dates, nonOutlBool_idx, axis=0)

                print("%2d\t%7s\t%12d\t\t%6d" % (iteration, args.method,args.scale,nOutlires))
                del nOutlires, nonOutlBool_idx, nonOutlBool

        elif args.method == 'Nsigma':
            while cond:
                iteration += 1
                _, _, _, resid = ls._lse(A, L[:,0])
                WRMS = np.sqrt((resid.T @ resid) / len(A[:,0]))[0][0]
                nonOutlBool = (np.abs(resid) < args.scale*WRMS)
                nOutlires = len(resid) - sum(nonOutlBool)
                nonOutlBool_idx = [i for i, val in enumerate(nonOutlBool == False) if val]
                del resid, WRMS

                if nOutlires == 0:
                    cond = False
                else:
                    outlierOBS  = np.append(outlierOBS, L[nonOutlBool_idx,:], axis=0)
                    outlierDATE = np.append(outlierDATE, dates[nonOutlBool_idx,:], axis=0)
                    A     = np.delete(A, nonOutlBool_idx, axis=0)
                    L     = np.delete(L, nonOutlBool_idx, axis=0)
                    dates = np.delete(dates, nonOutlBool_idx, axis=0)

                print("%2d\t%7s\t%12d\t\t%6d" % (iteration, args.method,args.scale,nOutlires))
                del nOutlires, nonOutlBool_idx, nonOutlBool


        print("\n")


        for k in range(len(header)):
            if 'COMPONENT' in header[k]:
                header[k] = "* COMPONENT    : " + i + "\n"
            if 'DATA ORDER' in header[k]:
                header[k] = "* DATA ORDER   : " + i + " s_" + i + " dates" + "\n"
            if 'ENDOFHEADER' in header[k]:
                header.insert(k, "* COMMENT      : All outliers have been removed wrt. " + args.method + "\n")
        

        newFilename = (args.fname.name[0:4] + i + ".tse")
        tf._write(newFilename, header, L, dates)
        del k

        if args.writeOutliers and (len(outlierOBS) != 0):
            for k in range(len(header)):
                if 'COMMENT' and 'outliers' in header[k]:
                    header[k] = "* COMMENT      : All outliers have been detected wrt. " + args.method + "\n"
                    break

            outliersFilename = (args.fname.name[0:4] + i + "_outliers.tse")
            tf._write(outliersFilename, header, outlierOBS, outlierDATE)
            del k 


if __name__ == "__main__":
    main()
