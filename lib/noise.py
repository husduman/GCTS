from dateUtilities import date as du
import numpy as np
from scipy.special import gamma, factorial
import scipy.linalg as la

class noise:
    def __init__(self, dates, dateFormat, kappa, Fs):
        self.dates      = dates
        self.dateFormat = dateFormat
        self.kappa      = kappa
        self.Fs         = Fs

    def mat(self):
        mjd    = _2mjd(self.dates, self.dateFormat)
        t0     = mjd[0] - 1
        newMJD = np.concatenate((t0, mjd), axis=None)
        DT     = (np.tile(np.diff(newMJD),(len(self.dates[:,0]),1)) / self.Fs) ** (-self.kappa / 4)

        Jvec   = np.zeros(len(mjd), dtype='double')
        for i in range(len(mjd)):
            if i <= 150:
                Jvec[i] = (gamma(i - (self.kappa / 2)) / (factorial(i) * gamma(-self.kappa / 2)))
            else:
                Jvec[i] = (i ** ((-self.kappa/2) - 1) / gamma(-self.kappa/2))
            #del dT
        del i
        T = np.multiply(DT, np.tril(la.toeplitz(Jvec)))      
        J = la.blas.dgemm(1.0, T, T.T)
        return T, J


def _2mjd(dates, dateFormat):
    mjd = []
    if dateFormat == 'mjd':
            mjd  = dates
    elif dateFormat == 'decimalYear':
        for i in range(len(dates[:,0])):
            dd = du([],dates[i,0],[],[],[],[],[],[],dateFormat,'mjd')._getdate()
            mjd.append(dd)
        del i
    elif dateFormat == 'yearANDdoy':
        for i in range(len(dates[:,0])):
            dd = du([],[],dates[i,0],[],[],dates[i,1],[],[],dateFormat,'mjd')
            mjd.append(dd._getdate())
        del i
    elif dateFormat == 'gweekANDdow':
        for i in range(len(dates[:,0])):
            dd = du([],[],[],[],[],[],dates[i,0],dates[i,1],dateFormat,'mjd')
            mjd.append(dd._getdate())
        del i
    elif dateFormat == 'yyyymmdd':
        for i in range(len(dates[:,0])):
            dd = du([],[],int(dates[i,0]),int(dates[i,1]),int(dates[i,2]),[],[],[],dateFormat,'mjd')
            mjd.append(dd._getdate())                
        del i
    else:
        print("Please check date format!")
    
    return mjd