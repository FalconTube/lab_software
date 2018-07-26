import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.signal
from lmfit import minimize, Parameters, fit_report
import sys
from mpl_toolkits.axes_grid1 import make_axes_locatable

from wdf_reader import wdfReader

from mpl_toolkits.mplot3d import axes3d

# plt.style.use('masterthesis')


def much_greater(value,b,c):
    if value > b+50 and value > c+50:
        return True
    else:
        return False

def smooth(z):
    for n, i in enumerate(z):
        for m, j in enumerate(i):
            if m == 0 or m >= len(i)-3:
                continue
            if much_greater(j, i[m-3], i[m+3]):
                z[n,m] = np.mean([i[m-3], i[m+3]])
    return z

def draw_waterfall(data, measured_length):
    measured_length = int(measured_length)
    Z = [[0,0],[0,0]]
    levels = range(0,measured_length+1,1)
    my_cmap = mpl.cm.rainbow
    CS3 = plt.contourf(Z, levels,\
     cmap=my_cmap)
    plt.clf()
    
    sx = data.shape[0]
    sy = data.shape[1]
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # ax.view_init(elev=19, azim=-180)
    NUM_COLORS = sx
    ax.set_prop_cycle('color',plt.cm.rainbow(np.linspace(0,1,NUM_COLORS)))

    Y = np.linspace(max(x),min(x), sy)

    plotcount = 0
    for n, i in enumerate(data):
        max_i = max(i)
        i = i/max_i
        mean_i = np.mean(i)
        if mean_i > 0.35:
            continue
        else:
            i = i + plotcount*0.02
            ax.plot(Y, i)
            plotcount += 1
    
    divider3 = make_axes_locatable(ax)
    cax = divider3.append_axes('right', size="5%", pad=0.05)
    cbar = fig.colorbar(CS3, cax=cax, label=r'Distance [$\mathrm{\mu}$m]')
    tickrange = np.linspace(0, measured_length, 5)
    cbar.set_ticks(tickrange)
    ax.set_xlabel(r"Raman Shift [cm$^{-1}$]")
    ax.set_ylabel(r"Intensity [a. u.]")
    ax.set_yticks([])
    ax.set_xlim(1200, 1850)
    plt.tight_layout()
    plt.savefig('3D_raman.png')

def DG_ratio(x,data):
    d_band = np.where(np.logical_and(1250<x, x<1420))
    g_band = np.where(np.logical_and(1550<x, x<1620))
    x_d = x[d_band]
    y_d = data[d_band]
    x_g = x[g_band]
    y_g = data[g_band]

    for i,j in zip(x_d,y_d):
        if j == max(y_d):
            initial_d = i
    for i,j in zip(x_g,y_g):
        if j == max(y_g):
            initial_g = i
    params = init_pars(initial_d, max(y_d), min(y_d))
    out_d = minimize(residual, params,
                 args=(x_d, y_d, lorentzian))
    results_d = out_d.params
    
    params = init_pars(initial_g, max(y_g), min(y_g))
    out_g = minimize(residual, params,
                 args=(x_g, y_g, lorentzian))
    results_g = out_g.params

    plot_d = np.linspace(min(x_d), max(x_d), 200)
    plot_g = np.linspace(min(x_g), max(x_g), 200)
    plot_whole = np.linspace(min(x), max(x), 1000)
    # plt.plot(plot_d, lorentzian(plot_d, results_d), 'r-', lw=3)
    # plt.plot(plot_g, lorentzian(plot_g, results_g), 'r-', lw=3)
    
    d_intensity = max(lorentzian_no_bg(plot_d, results_d))
    g_intensity = max(lorentzian_no_bg(plot_g, results_g))
    dg_ratio = d_intensity/g_intensity
    print("D/G Ratio = {}".format(dg_ratio))

    fig = plt.figure()
    
    ax = fig.add_subplot(111)
    ax.plot(x, data, 'k-')
    ax.set_xlabel(r"Raman Shift [cm$^{-1}$]")
    ax.set_ylabel(r"Intensity [a. u.]")
    ax.set_xlim(1200, 1850)
    ax.set_yticks([])
    ax.text(0.2, 0.95,'DG_ratio = {:2f}'.format(dg_ratio),
     horizontalalignment='center',
     verticalalignment='center',
     transform = ax.transAxes)
    plt.savefig('Medium_raman.png')


def linear(x, m, b):
    return m*x + b

def lorentzian(x, pars):
    gamma = pars["gamma"]
    x0 = pars["x0"]
    offset = pars["offset"]
    a = pars["a"]
    m = pars["m"]
    b = pars["b"]
    denom = np.pi * gamma * ( 1 + ((x-x0)/gamma)**2 )
    return a*(1/denom) + linear(x, m, b)

def lorentzian_no_bg(x, pars):
    gamma = pars["gamma"]
    x0 = pars["x0"]
    a = pars["a"]
    denom = np.pi * gamma * ( 1 + ((x-x0)/gamma)**2 )
    return a*(1/denom)

def residual(pars, x, data, fitfunc, eps_data=None):
    model = fitfunc(x, pars)
    if eps_data == None:
        return data-model
    else:
        return (data-model)/eps_data

def init_pars(x_init, a_init, offset_init):
    pars = Parameters()
    pars.add('gamma', value=0.5)
    pars.add('x0', value=x_init, min=x_init-200, max=x_init+200)
    pars.add('offset', value=offset_init)
    pars.add('a', value=a_init)
    pars.add('m', value=10)
    pars.add('b', value=offset_init)
    return pars

if len(sys.argv) < 2:
    print('\nUsage:\n\
1. Argument: WDF filename\n\
2. Argument: Length in micron\n')
    print('Please provide necessary input. Exiting...')
    sys.exit()
if sys.argv[1] == '-h' or sys.argv[1] == '--help':
    print('\nUsage:\n\
1. Argument: WDF filename\n\
2. Argument: Length in micron\n')
    sys.exit()

wdffile = sys.argv[1]
measured_length = sys.argv[2]

wdf = wdfReader(wdffile)
t = wdf.get_spectra()
x = wdf.get_xdata()
y = wdf.get_ydata()
length_meas = len(x)
num_meas = int(len(t)/length_meas)
t_r = np.reshape(t,(num_meas,length_meas))

mean_map = np.sum(t_r, axis=0)/len(t_r)
DG_ratio(x,mean_map)

print('Filtering/Smoothing data...')
t_smooth = smooth(t_r)
reduced_data = t_smooth[::2][::2][::2]
print('Plotting waterfall...')
draw_waterfall(reduced_data, measured_length)

