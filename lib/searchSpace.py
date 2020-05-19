import numpy as np
import math, glob, re, os
from qReg import _quantileReg as qr
from scipy.stats.distributions import chi2

class searchSpace:
    def __init__(self, alpha, WRMS, dof, nRND):
        self.alpha = alpha
        self.WRMS  = WRMS
        self.dof   = dof
        self.nRND  = nRND

    def _extremePoints(self):
        WRMS = []
        WNA  = []
        FNA  = []
        pyGCTSpath="{}".format(os.environ['pyGCTS'])
        for file in glob.iglob(pyGCTSpath + '/metaData/results*', recursive=True):
            with open(file,'r') as ff:
                for line in ff.readlines():
                    WRMS.append(float(line.split()[1]))
                    WNA.append(float(line.split()[2]))
                    FNA.append(float(line.split()[3]))
        

        ff.close()
        WRMSnew = (np.asarray(WRMS)).reshape(len(WRMS),1)
        WNAnew  = (np.asarray(WNA)).reshape(len(WNA),1)
        FNAnew  = (np.asarray(FNA)).reshape(len(FNA),1)

        alphaNew   = 1 - np.sqrt(1 - self.alpha)
        pLower_wna = qr(WRMSnew, WNAnew, (1 - alphaNew/2))
        pUpper_wna = qr(WRMSnew, WNAnew, (alphaNew/2))

        pLower_fna = qr(WRMSnew, FNAnew, (1 - alphaNew/2))
        pUpper_fna = qr(WRMSnew, FNAnew, (alphaNew/2))

        funWRMS    = lambda wrms, alp, dof: np.array([np.sqrt((dof * wrms**2) / chi2.ppf(1-alp/2,dof)), 
                                            np.sqrt((dof * wrms**2) / chi2.ppf(alp/2,dof))])
        WRMSlims = funWRMS(self.WRMS, alphaNew, self.dof)

        funWNA     = lambda horlims, pUpwna, pLowna: np.array([pUpwna[0] * horlims[0] + pUpwna[1],
                                                               pUpwna[0] * horlims[1] + pUpwna[1],
                                                               pLowna[0] * horlims[1] + pLowna[1],
                                                               pLowna[0] * horlims[0] + pLowna[1]])
        extWNAs = funWNA(WRMSlims, pUpper_wna, pLower_wna)

        funFNA     = lambda horlims, pUpfna, pLofna: np.array([pUpfna[0] * horlims[0] + pUpfna[1],
                                                               pUpfna[0] * horlims[1] + pUpfna[1],
                                                               pLofna[0] * horlims[1] + pLofna[1],
                                                               pLofna[0] * horlims[0] + pLofna[1]])
        extFNAs = funFNA(WRMSlims, pUpper_fna, pLower_fna)
        #np.savetxt('6-extWNAs.dat', extWNAs, fmt="%10.4f")
        #np.savetxt('7-extFNAs.dat', extFNAs, fmt="%10.4f")
        #np.savetxt('8-WRMSlims.dat', WRMSlims, fmt="%10.4f")
        #np.savetxt('11-wna_lo.dat', pLower_wna, fmt="%10.4f")
        #np.savetxt('12-wna_up.dat', pUpper_wna, fmt="%10.4f")
        #np.savetxt('13-fna_lo.dat', pLower_fna, fmt="%10.4f")
        #np.savetxt('14-fna_up.dat', pUpper_fna, fmt="%10.4f")
        return extWNAs, extFNAs, WRMSlims

        

    def _randomPoints(self):
        extWNAs, extFNAs, WRMSlims = self._extremePoints()
        px = np.concatenate((WRMSlims, WRMSlims[::-1]), axis=0)
        transMat = np.array([[1, 0, 0, 0],
                             [1, 1, 0, 0],
                             [1, 1, 1, 1],
                             [1, 0, 1, 0]])
        a     = np.linalg.inv(transMat) @ px.T
        b_wna = np.linalg.inv(transMat) @ (extWNAs).T
        b_fna = np.linalg.inv(transMat) @ (extFNAs).T

        xWNA, yWNA = _pointsIn(a, b_wna, self.nRND)
        xFNA, yFNA = _pointsIn(a, b_fna, self.nRND)
        yWNA[yWNA <= 0] = math.nan
        yFNA[yFNA <= 0] = math.nan
        #np.savetxt('9-rndWNA.dat', np.concatenate((xWNA, yWNA), axis=1), fmt="%10.4f")
        #np.savetxt('10-rndFNA.dat', np.concatenate((xFNA, yFNA), axis=1), fmt="%10.4f")
        return xWNA, yWNA, xFNA, yFNA

def _pointsIn(a, b, nRND):
    # a - 4x1 vector including logical x coordinates
    # b - 4x1 vector including logical y coordinates
    x = np.empty((nRND,1), dtype='float')
    y = np.empty((nRND,1), dtype='float')
    for i in range(nRND):
        lx = np.random.rand()
        ly = np.random.rand()
        x[i] = a[0] + a[1]*lx + a[2]*ly + a[3]*lx*ly
        y[i] = b[0] + b[1]*lx + b[2]*ly + b[3]*lx*ly

    return x, y
