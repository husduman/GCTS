import numpy as np
import sys
import leastSquares as ls
from scipy.optimize import fmin
#https://uk.mathworks.com/matlabcentral/fileexchange/32115-quantreg-x-y-tau-order-nboot
"""Reference:
Aslak Grinsted (2020). quantreg(x,y,tau,order,Nboot) 
(https://www.mathworks.com/matlabcentral/fileexchange/32115-quantreg-x-y-tau-order-nboot),
MATLAB Central File Exchange. Retrieved February 13, 2020.
"""
def _quantileReg(x, y, tau):
    if (tau <= 0) or (tau >= 1):
        print("tau must be between 0 and 1!")
        sys.exit()

    if len(x) != len(y):
        print("The length of x and y must be same!")
        sys.exit()

    x = np.column_stack((x, np.ones((len(x),1))))
    unk, sUnk, s0, resid = ls._lse(x, y)
    del sUnk, s0, resid
    rho      = lambda r: sum(abs(r * (tau - (r < 0))))
    phi      = lambda p: rho(np.subtract((x @ p).reshape(len(x @ p),1), y))
    #phi      = lambda p: rho(resid)
    unkFinal = fmin(func=phi, x0 = unk, disp=False)
    #print(unkFinal)
    return unkFinal