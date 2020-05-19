import math, sys
import numpy as np

class date:
    def __init__(self, mjd, decimalYear, year, month, day, doy, gweek, dow, inpf, outf):
        self.mjd         = mjd
        self.decimalYear = decimalYear
        self.year        = year
        self.month       = month
        self.day         = day
        self.doy         = doy
        self.gweek       = gweek
        self.dow         = dow
        self.inpf        = inpf
        self.outf        = outf
    
    def _getdate(self):
            if self.inpf == 'mjd':
                self.year, self.month, self.day = _mjd2ymd(self.mjd)
                self.gweek, self.dow            = _ymd2gwd(self.year, self.month, self.day)
                self.doy                        = _ymd2doy(self.year, self.month, self.day)
                self.decimalYear                = self.year + self.doy/365.25

            elif self.inpf == 'decimalYear':
                self.year                       = math.floor(self.decimalYear)
                self.doy                        = math.ceil((self.decimalYear - self.year) * 365.25)
                self.month, self.day            = _doy2mday(self.year, self.doy)
                self.mjd                        = _ymd2jd(self.year, self.month, self.day) - 2400000.50
                self.gweek, self.dow            = _ymd2gwd(self.year, self.month, self.day)

            elif self.inpf == 'yearANDdoy':
                self.month, self.day            = _doy2mday(self.year, self.doy)
                self.mjd                        = _ymd2jd(self.year, self.month, self.day) - 2400000.50
                self.gweek, self.dow            = _ymd2gwd(self.year, self.month, self.day)
                self.decimalYear                = self.year + self.doy/365.25

            elif self.inpf == 'gweekANDdow':
                self.mjd                        = self.gweek*7 + self.dow + 44244
                self.year, self.month, self.day = _mjd2ymd(self.mjd)
                self.doy                        = _ymd2doy(self.year, self.month, self.day)
                self.decimalYear                = self.year + self.doy/365.25

            elif self.inpf == 'yyyymmdd':
                self.mjd                        = _ymd2jd(self.year, self.month, self.day) - 2400000.50
                self.gweek, self.dow            = _ymd2gwd(self.year, self.month, self.day)
                self.doy                        = _ymd2doy(self.year, self.month, self.day)
                self.decimalYear                = self.year + self.doy/365.25
            else:
                print("Please check your input date flag!")
                sys.exit()
                
            if self.outf == 'mjd':
                return self.mjd
            elif self.outf == 'decimalYear':
                return self.decimalYear
            elif self.outf == 'yearANDdoy':
                return self.year, self.doy
            elif self.outf == 'gweekANDdow':
                return self.gweek, self.dow
            elif self.outf == 'yyyymmdd':
                return self.year, self.month, self.day
            else:
                print("Please check your output date flag!")
                sys.exit()
            

        
def _doy2mday(year, doy):
    # convert day of year to month, and day of month
    month_day = np.array([[0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365],
        [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]])

    if ((year % 4) == 0):
        for i in range(13):
            if doy <= month_day[1,i]:
                month = i
                day = doy - month_day[1, month-1]
                break

    else:
        for i in range(13):
            if doy <= month_day[0,i]:
                month = i
                day = doy - month_day[0, month-1]
                break

    return month, day

def _mjd2ymd(mjd):
    # convert modified julian date to year, month, and day
    juliandate = mjd + 2400000.50
    a          = math.floor(juliandate + 0.5)
    b          = a + 1537
    c          = math.floor((b - 122.1) / 365.25)
    d          = math.floor(365.25 * c)
    e          = math.floor((b - d)/30.6001)

    day        = b - d - math.floor(30.6001 * e) + (math.floor(juliandate + 0.5) - (juliandate + 0.5))
    month      = e - 1 - (12 * math.floor(e / 14))
    year       = c - 4715 - math.floor((7 + month) / 10)

    return year, month, day

def _ymd2jd(year, month, day):
    # convert year, month, and day to julian date
    if month <= 2:
        y = year - 1
        m = month + 12
        juliandate = math.floor(365.25 * y) + math.floor(30.6001 * (m + 1)) + day + 1720981.50
    else:
        y = year
        m = month
        juliandate = math.floor(365.25 * y) + math.floor(30.6001 * (m + 1)) + day + 1720981.50
    
    return juliandate

def _ymd2gwd(year, month, day):
    # convert year, month, day to gps week and day of week
    jd    = _ymd2jd(year, month, day)
    gweek = math.floor((jd - 2444244.50) / 7)
    dow   = (math.floor(jd + 1.5) % 7)

    return gweek, dow

def _ymd2doy(year, month, day):
    # convert year, month, day to year and day of year
    month_day = np.array([[0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365],
        [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]])
    if ((year % 4) == 0):
        doy = month_day[1, month-1] + day
    else:
        doy = month_day[0, month-1] + day

    return doy