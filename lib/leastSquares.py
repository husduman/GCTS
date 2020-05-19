import scipy.linalg as la
import numpy as np


def _lse(A, L, p = None):
    # A - coefficient matrix
    # L - observation vector
    # p - lower triangular weight matrix

    if p is not None:
        # solve the equation with any weight matrix
        Anew = la.blas.dgemm(1, p.T, A)        
        Lnew = la.blas.dgemv(1, p.T, L).reshape(len(L),1)  
        nEq  = la.blas.dgemm(1, Anew.T, Anew)
        rhs  = la.blas.dgemv(1, Anew.T, Lnew).reshape(len(Anew.T),1)        
        _,_, X,_ = la.lapack.dgesv(nEq, rhs)
        resid    = np.subtract((A @ X).reshape(len(A@X),1), L.reshape(len(L),1))
        residNew = la.blas.dgemv(1, p.T, resid).reshape(len(resid),1)
        f        = len(Anew[:,0]) - len(Anew[0,:])
        #s0       = np.sqrt(la.blas.ddot(residNew, residNew) / f)
        s0       = np.sqrt(np.sum(residNew**2) / f)
        Qx       = la.inv(nEq)
        sX       = np.zeros(len(Qx[:,0]), dtype='float')
        for i in range(len(Qx[:,0])):
            sX[i] = s0 * np.sqrt(Qx[i,i])
    else:
        # solve the equation without any weight matrix
        nEq = la.blas.dgemm(1, A.T, A)
        rhs = la.blas.dgemv(1, A.T, L)
        _,_, X,_ = la.lapack.dgesv(nEq, rhs)
        resid    = np.subtract((A @ X).reshape(len(A@X),1), L.reshape(len(L),1))
        f        = len(A[:,0]) - len(A[0,:])
        #s0       = np.sqrt(la.blas.ddot(resid, resid) / f)
        s0       = np.sqrt(np.sum(resid**2) / f)
        Qx       = la.inv(nEq)
        sX       = np.zeros(len(Qx[:,0]), dtype='float')
        for i in range(len(Qx[:,0])):
            sX[i] = s0 * np.sqrt(Qx[i,i])

    return X, sX, s0, resid