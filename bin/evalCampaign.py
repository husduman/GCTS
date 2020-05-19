#!/usr/bin/env python3

import argparse, statistics, time, os,sys
pyGCTSpath="{}/lib".format(os.environ['pyGCTS'])
if pyGCTSpath not in sys.path:
    sys.path.append(pyGCTSpath)


import leastSquares as ls
import tseFile as tf
import numpy as np
import scipy.linalg as la
import matplotlib.pylab as plt
from scipy.interpolate import griddata
from designMat import designMat as dm
from searchSpace import searchSpace as ss
from noise import noise
from dateUtilities import date as du



__prog__ = 'evalCampaign.py'

__description__ = '''
evalCampaign -> analyzes the GPS campaign time-series.

The script analyzes the campaign time-series using either a weight matrix or a unit
matrix (i.e. the ordinary least-squares estimation). The weight matrix is composed
of the white and flicker noise combination, which are estimated/interpolated via 
the new approach published by Duman and Sanli (2020). After analyzing, the model
is written into a file by specifiying -writeModel argument.

'''

__epilog__ = '''
*** EXAMPLES ***

---------
:: Ex1 ::
    Let a time-series for the east component of the site TEST. To analyze the series
    according to the new approach:


    evalCampaign.py -fname TESTeast.tse -nRND 30 -repeat 100 -writeModel

	 ======================================================================================
	 evalCampaign.py is running and using the parameters:
	 ======================================================================================
	    filename : TESTeast.tse
	       alpha : 0.05
		nRND : 30
		  Fs : 365.25
	       kappa : -1
		incr : 0.025
	      repeat : 100
	  writeModel : on
	 ======================================================================================

	 --------------------------------------------------------------------------------------
	  The statistical details of the time series file
	 --------------------------------------------------------------------------------------
	 Filename                           : /home/hduman/GCTS_1.1/example/TESTeast.tse
	 First and Last Obs.   [yyyy/mm/dd] : from 2013/11/8 to 2017/1/14
	 Length of Series         (in Days) : 1164 (3.19 years)
	 Number of Observations   (in Days) : 15
	 Percentage of Gaps                 : 98.71
	 Number of Offset                   : 0
	 --------------------------------------------------------------------------------------

	 Progress |██████████████████████████████████████████████████| 100.0% Complete


		   intercept:     4.5500 +-    2.7233 mm
		       trend:   -25.7075 +-    3.5341 mm/year


		         wna:     2.5759 mm
		         fna:    12.4394 mm/year^0.25
		          s0:     1.00000044 mm

	 TESTeast_model.tse file has been created...

	Elapsed time : 47.6 sec


    NOTE: As clearly seen in the command, although some of the arguments have
          not been introduced in the command line, they are set as default values.
	  One can specify the arguments the desired values.


---------
:: Ex2 ::
    Let a time-series for the east component of the site TEST. To analyze the series
    according to the ordinary least-sqaures estimates:


    evalCampaign.py -fname TESTeast.tse -ols

	 ======================================================================================
	 evalCampaign.py is running and using the parameters:
	 ======================================================================================
	    filename : TESTeast.tse
	       alpha : 0.05
		nRND : None
		  Fs : 365.25
	       kappa : -1
		incr : 0.025
	      repeat : None
	  writeModel : off
	 ======================================================================================

	 --------------------------------------------------------------------------------------
	  The statistical details of the time series file
	 --------------------------------------------------------------------------------------
	 Filename                           : /home/hduman/GCTS_1.1/example/TESTeast.tse
	 First and Last Obs.   [yyyy/mm/dd] : from 2013/11/8 to 2017/1/14
	 Length of Series         (in Days) : 1164 (3.19 years)
	 Number of Observations   (in Days) : 15
	 Percentage of Gaps                 : 98.71
	 Number of Offset                   : 0
	 --------------------------------------------------------------------------------------


	 Ordinary Least-squares estimation

		   intercept:     4.5158  +-    1.6092 mm
		       trend:   -24.7313  +-    1.1379 mm/year


		          s0:     4.25816374       mm


	Elapsed time : 0.0 sec


    NOTE: This example is the same with the previous one but the series analyzed via the
	  ordinary least-squares-estimates.



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
                        help = """[?](comp).tse file name to be analyzed, which
                        could contain only one GPS component or only one column
                        with its standard deviation.""")

    parser.add_argument("-periods", type=str, nargs='+', default=[],
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

    parser.add_argument("-alpha", type=float, nargs='?',
                        default = 0.05, 
                        help="""Significance level to determine the search space limits. Search
                        space is a set containing a noise amplitude with 1 - alpha confidence
                        level.""")

    parser.add_argument("-nRND", type=int, nargs='?',
                        help="""number of randomly generated values for noise amplitude within 
                        the search area.""")

    parser.add_argument("-fs", type=float, nargs='?',
                        default=365.25,
                        help="""Observation frequency, which is set to 365.25 as default.""")

    parser.add_argument("-kappa", type=float, nargs='?',
                        default=-1,
                        help="""Spectral index for colored noise. Kappa is set to -1 which is
                        for flicker noise.""")

    parser.add_argument("-incr",type=float, nargs='?',
                        default = 0.025,
                        help="""Weighted least-squares solution is made from all mutual
                        combinations of random points produced in the search area for both
                        white and flicker noise. The posterior variances calculated from all
                        solutions create a smooth and clear surface with their corresponding
                        noise amplitudes. The -incr argument is the amount of INCREMENT used
                        in order to create mesh surface.""")
    
    parser.add_argument("-repeat", type=int, nargs='?',
                        help = """Theoretically, the most appropriate solution is the solution
                        where the posterior variance is equal to 1. On the created posterior
                        variance surface, the noise amplitudes corresponding to a value of 1 are
                        estimated, then the weighted least-squares estimation are made again and
                        the solution closest to 1 is selected. For a robust analysis, this process
                        is repeated N times which is specified under -repeat argument.""")
    
    parser.add_argument("-ols", action='store_true',
                        help = """Ordinary least-squares estimation. If this argument is specified,
                        time series data are analyzed without any weight matrix.""")

    parser.add_argument("-writeModel", action='store_true',
                        help="A choice to be write down the model values or not")

    return parser

def _dispParser(args):
    print(" ======================================================================================\n",
          os.path.basename(__file__) + " is running and using the parameters:\n",
        "======================================================================================")
    print("    filename : " + args.fname.name)
    for i in args.periods: print("     periods : " + i)
    print("       alpha : " + str(args.alpha) + "\n",
          "       nRND : " + str(args.nRND) + "\n",
          "         Fs : " + str(args.fs) + "\n",
          "      kappa : " + str(args.kappa) + "\n",
          "       incr : " + str(args.incr) + "\n",
          "     repeat : " + str(args.repeat))
    if args.writeModel:
        print("  writeModel : on")
    else:
        print("  writeModel : off")
    print(" ======================================================================================\n")


def main():
    startTime = time.time()
    args = _getparser().parse_args()
    _dispParser(args)
    tf._stats(args.fname.name)

    header, _, offset, obs, dates = tf._read(args.fname.name)
    A, cycle = dm(args.fname.name, args.periods, args.fs)._coefficients()
    L   = obs[:,0].reshape(len(obs[:,0]),1)
    dof = len(A[:,0]) - len(A[0,:])
    unkOLS, sUnkOLS, s0OLS, resid = ls._lse(A, L)
    WRMS = np.sqrt((resid.T @ resid) / len(A[:,0]))[0][0]
    #print("WRMS: " + str(WRMS))
    
    for line in header:
        if 'UNIT' in line:
            unit = line.split(": ")[1].split("\n")[0]
            break
    
    unitLabel = [unit] * len(unkOLS)    
    unitLabel[1] = unitLabel[1] + "/year"
    unkLabel = ['intercept', 'trend']
    offsetLabel = ["{}{}".format(a, b) for a, b in zip(["offset at "]*len(offset), offset)]
    unkLabel = np.append(unkLabel, offsetLabel)
    seasLabel = []
    for s1 in range(len(cycle)):
        seasLabel = np.append(seasLabel, ['sin ' + "{:10.4f}".format(cycle[s1]), 'cos ' + "{:10.4f}".format(cycle[s1])])
    unkLabel = np.append(unkLabel, seasLabel)
 
    if args.ols:
        print("\n Ordinary Least-squares estimation\n")
        for o in range(len(unkOLS)):
            print("%20s: %10.4f  +- %9.4f %s" % \
                (unkLabel[o], \
                 unkOLS[o], \
                 sUnkOLS[o], \
                 unitLabel[o]))
        print("\n")
        print("%20s: %14.8f %8s\n" % ('s0', s0OLS, unit))
        print("\nElapsed time : %.1f sec\n" % (time.time() - startTime))
        return 

    for line in header:
        if 'DATE FORMAT' in line:
            dateFormat = line.split(": ")[1].split("\n")[0]
            break

    

    _, J = noise(dates, dateFormat, args.kappa, args.fs).mat()

    resultTemp = np.zeros((args.nRND**2,3))
    wnaLast = np.zeros((args.repeat,1),dtype=float)
    fnaLast = np.zeros((args.repeat,1),dtype=float)
    for i in range(args.repeat):
        printProgressBar(i+1, args.repeat, prefix=' Progress', suffix='Complete')
        _, yWNA, _, yFNA = ss(args.alpha, WRMS, dof, args.nRND)._randomPoints()

        idx = 0
        for j in range(args.nRND):
            cWN = (yWNA[j]**2 * np.eye(len(A[:,0]), dtype=float))
            for k in range(args.nRND):
                C = cWN + (yFNA[k]**2 * J)
                _, _, s0, _ = ls._lse(A, L, la.cholesky(la.inv(C)).T)
                resultTemp[idx,:] = [yWNA[j], yFNA[k], s0]
                idx += 1
        #np.savetxt('15-s0s.dat', resultTemp, fmt="%10.10f")
        xx     = np.arange(min(resultTemp[:,0]), max(resultTemp[:,0]), args.incr)
        yy     = np.arange(min(resultTemp[:,1]), max(resultTemp[:,1]), args.incr)
        XX, YY = np.meshgrid(xx, yy)
        ZZ     = griddata((resultTemp[:,0],resultTemp[:,1]), resultTemp[:,2], (XX, YY), method='cubic')
        #np.savetxt('1-XX.dat', XX, fmt="%10.4f")
        #np.savetxt('2-YY.dat', YY, fmt="%10.4f")
        #np.savetxt('3-ZZ.dat', ZZ, fmt="%10.4f")
        if (np.min(np.ma.masked_invalid(ZZ)) < 1) and (np.max(np.ma.masked_invalid(ZZ)) > 1):
            cs     = plt.contour(xx, yy, np.ma.masked_invalid(ZZ), [1])
            L1     = cs.collections[0].get_paths()[0]
            coorL1 = L1.vertices
        else:
            index  = np.where(abs(np.ma.masked_invalid(ZZ) - 1) == np.amin(abs(np.ma.masked_invalid(ZZ) - 1)))
            coorL1 = np.array([[XX[index[0][0],index[1][0]], \
                                YY[index[0][0],index[1][0]]]])
        #np.savetxt('4-coorL1.dat', coorL1, fmt="%10.4f")
        s0 = np.zeros((len(coorL1[:,0]),1),dtype=float)
        for d in range(len(coorL1[:,0])):
            C2 = (coorL1[d,0]**2 * np.eye(len(A[:,0]), dtype=float)) + \
                 (coorL1[d,1]**2 * J)
            _, _, s0[d], _ = ls._lse(A, L, la.cholesky(la.inv(C2)).T)
            
        diffIDX = np.where(abs(s0 - 1) == np.amin(abs(s0 - 1)))[0][0]
        wnaLast[i] = coorL1[diffIDX,0]
        fnaLast[i] = coorL1[diffIDX,1]

    #np.savetxt('5-noiseAmp.dat', np.concatenate((wnaLast, fnaLast), axis=1), fmt="%10.4f")
    Cfin = (statistics.median(wnaLast)**2 * np.eye(len(A[:,0]), dtype=float)) + \
           (statistics.median(fnaLast)**2 * J)

    unk_fin, sUnk_fin, s0_fin, _ = ls._lse(A, L, la.cholesky(la.inv(Cfin)).T)
    print("\n")
    for o in range(len(unk_fin)):
        print("%20s: %10.4f +- %9.4f %s" % \
            (unkLabel[o], \
            unk_fin[o], \
            sUnk_fin[o], \
            unitLabel[o]))
    print("\n")
    print("%20s: %10.4f %s" % ('wna', statistics.median(wnaLast), unit))
    print("%20s: %10.4f %s" % ('fna', statistics.median(fnaLast), unit+"/year^0.25"))
    print("%20s: %14.8f %s\n" % ('s0', s0_fin, unit))
    

    if args.writeModel:
        for ii in range(len(header)):
            if 'COMMENT' and 'outliers' in header[ii]:
                header[ii] = "* COMMENT      : Model values" + "\n"
                break
        modelFilename = (args.fname.name.split(".")[0] + "_model.tse")
        tf._write(modelFilename, \
                 header, \
                 np.concatenate(((A @ unk_fin), np.zeros((len(A[:,0]),1), dtype=float)), axis=1), \
                 dates)

    print("\nElapsed time : %.1f sec\n" % (time.time() - startTime))  


def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 50, fill = '█', printEnd = "\r"):
    #https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


if __name__ == "__main__":
    main()
