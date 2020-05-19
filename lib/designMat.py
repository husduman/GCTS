import numpy as np
import tseFile as tf
from dateUtilities import date as du
import math

class designMat:
    def __init__(self, filename, periods, Fs):
        self.filename = filename
        self.periods  = periods
        self.Fs       = Fs          # Frequency

    def _coefficients(self):
        header, component, offset, obs, dates = tf._read(self.filename)
        del component, obs
        cycle = _calcPeriods_inDays(self.periods)
        for line in header:
            if 'DATE FORMAT' in line:
                dateFormat = line.split(": ")[1].split("\n")[0]
                break
        datesNew  = []
        offsetNew = []
        if dateFormat == 'mjd':
            datesNew  = dates
            for j in range(len(offset)):
                offsetNew.append(float(offset[j]))
        elif dateFormat == 'decimalYear':
            for i in range(len(dates[:,0])):
                dd = du([],dates[i,0],[],[],[],[],[],[],dateFormat,'mjd')._getdate()
                datesNew.append(dd)
            for j in range(len(offset)):
                dy  = float(offset[j])
                ddo = du([],dy,[],[],[],[],[],[],dateFormat,'mjd')
                offsetNew.append(ddo._getdate())
        elif dateFormat == 'yearANDdoy':
            for i in range(len(dates[:,0])):
                dd = du([],[],dates[i,0],[],[],dates[i,1],[],[],dateFormat,'mjd')
                datesNew.append(dd._getdate())
            for j in range(len(offset)):
                yy  = int(offset[j].split(" ")[0])
                do  = int(offset[j].split(" ")[1])
                ddo = du([],[],yy,[],[],do,[],[],dateFormat,'mjd')
                offsetNew.append(ddo._getdate())
        elif dateFormat == 'gweekANDdow':
            for i in range(len(dates[:,0])):
                dd = du([],[],[],[],[],[],dates[i,0],dates[i,1],dateFormat,'mjd')
                datesNew.append(dd._getdate())
            for j in range(len(offset)):
                gw  = int(offset[j].split(" ")[0])
                dw  = int(offset[j].split(" ")[1])
                ddo = du([],[],[],[],[],[],gw,dw,dateFormat,'mjd')
                offsetNew.append(ddo._getdate())
        elif dateFormat == 'yyyymmdd':
            for i in range(len(dates[:,0])):
                dd = du([],[],int(dates[i,0]),int(dates[i,1]),int(dates[i,2]),[],[],[],dateFormat,'mjd')
                datesNew.append(dd._getdate())                
            for j in range(len(offset)):
                yy  = int(offset[j].split(" ")[0])
                mm  = int(offset[j].split(" ")[1])
                da  = int(offset[j].split(" ")[2])
                ddo = du([],[],yy,mm,da,[],[],[],dateFormat,'mjd')
                offsetNew.append(ddo._getdate())
        else:
            print("Please check date format in your [?].tse file!")


        A = np.zeros((len(datesNew),(2 + len(cycle)*2 + len(offset))), dtype=float)
        for i in range(len(datesNew)):
            A[i,[0,1]] = [1, (datesNew[i] - datesNew[0])/self.Fs]
            if offsetNew is not None:
                for j in range(len(offsetNew)):
                    if datesNew[i] < offsetNew[j]:
                        A[i,2+j] = 0
                    else:
                        A[i,2+j] = 1
            if cycle is not None:
                for k in range(len(cycle)):
                    A[i, [2+len(offset)+(2*k), 2+len(offset)+(2*k+1)]] = [math.sin(2 * math.pi * (datesNew[i] - datesNew[0]) / cycle[k]),
                         math.cos(2 * math.pi * (datesNew[i] - datesNew[0]) / cycle[k])]

        return A, cycle

def _calcPeriods_inDays(periods):
    cycle = []
    t = 365.25      # tropical year
    d = 354.60      # draconitic year
    c = 433.00      # chandler year
    for i in periods:
        if i[0] == 'T':
            for j in range(int(i[1:])):
                cycle.append(t / (2 ** j))
        elif i[0] == 'D':
            for k in range(int(i[1:])):
                cycle.append(d / (2 ** k))
        elif i[0] == 'C':
            for l in range(int(i[1:])):
                cycle.append(c / (2 ** l))
        else:
            cycle.append(float(i))

    return cycle

