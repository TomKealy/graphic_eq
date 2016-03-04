import Tkinter as Tk
import scipy.signal as sig
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as pl


class EQModel(object):
    def __init__(self, signal_in, gains):
        self.signal = signal_in
        self.gains = gains
        self.Q = 3.5
        
    def apply_gains(self):
        fs = 44100.0
        NB = len(self.gains)
        fc = 31.25*2**np.arange(5)
        A = np.zeros((NB, 3))
        B = np.zeros((NB, 3))

        for k in range(NB):
            [b, a] = self.peaking(self.gains[k], fc[k], self.Q)
            B[k,:] = b
            A[k,:] = a

        y = np.zeros(len(self.signal))
        for k in range(NB):
            if k == 0:
                y = sig.lfilter(B[k,:], A[k,:], self.signal)
            else:
                y = sig.lfilter(B[k,:], A[k,:], y)
        return y

    def peaking(self, gain, fc, Q=3.5, fs=44100.):
        mu = 10**(gain/20.)
	kq = 4/(1 + mu)*np.tan(2*np.pi*fc/fs/(2*Q))
	Cpk = (1 + kq *mu)/(1 + kq)
	b1 = -2*np.cos(2*np.pi*fc/fs)/(1 + kq*mu)
	b2 = (1 - kq*mu)/(1 + kq*mu)
	a1 = -2*np.cos(2*np.pi*fc/fs)/(1 + kq)
	a2 = (1 - kq)/(1 + kq)
	b = Cpk*np.array([1, b1, b2])
	a = np.array([1, a1, a2])
	return b,a
        
class EQView(object):
    def __init__(self, master):
        self.frame = Tk.Frame(master)
        self.guiElements = {}
        for i in range(0, 5):
            self.guiElements['Scale' + str(i)] = Tk.Scale(master)
        self.guiElements['Scale0'].grid(row=0, column=0)
        self.guiElements['Scale1'].grid(row=0, column=1)
        self.guiElements['Scale2'].grid(row=0, column=2)
        self.guiElements['Scale3'].grid(row=0, column=3)
        self.guiElements['Scale4'].grid(row=0, column=4)
        self.button = Tk.Button(master, text="Apply filters")
        self.button.grid(row=1, column=0)


class EQController(object):
    def __init__(self):
        self.root = Tk.Tk()
        self.t = np.arange(0, 0.05, 1/44100.0)
        self.x = np.cos(2*np.pi*31.25*self.t)+np.cos(2*np.pi*4000*self.t)
        self.gains = np.zeros(5)
        self.model = EQModel(self.x, self.gains)
        self.view = EQView(self.root)
        self.view.button.config(command=self.apply_gains)

    def run(self):
        self.root.deiconify()
        self.root.mainloop()

    def apply_gains(self):
        for i in range(0, 5):
            self.model.gains[i] = self.view.guiElements['Scale' + str(i)].get()
        out =self.model.apply_gains()
        pl.plot(self.t, self.x, label='orig')
        pl.plot(self.t, out, label='equalised')
        pl.legend()
        pl.show()

def main():
    app = EQController()
    app.run()

if __name__ == '__main__':
    main()
