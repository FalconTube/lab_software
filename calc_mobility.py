import matplotlib.pyplot as plt
import numpy as np
import glob
import sys
import os

print('This programm will calculate the mobility for all files' +
      ' with a specified name in a specified folder.')
folder = str(input('Define Foldername: '))
filename = str(
    input('Define base of filenames (standard is gatesweep): ') or 'gatesweep')
if not folder or folder == '' or filename == False or filename == '':
    print('No folder or filename specified. Exiting...')
    sys.exit()
if folder[-1] == '/':
    folder = folder[0:-1]
print('Working in Folder: {}'.format(folder))

os.chdir(folder)
for fn in glob.glob('{}*.dat'.format(filename)):
    if '_mobility' in fn:
        continue
    # Set up plots
    fig = plt.figure()
    ax = fig.add_subplot(211)
    ax1 = fig.add_subplot(212)
    ax1.set_xlabel('Gatevoltage [V]')
    ax1.set_ylabel(r'Resistance [$\Omega$]')
    ax.set_ylabel(r'Mobility')
    title = fn.split('.')[0]

    # Read gatevoltage and Resistance
    # Define number, that resistance is in (currently 4 everywhere)
    resistance_col = 4
    gV, resistance = np.loadtxt(
        fn, usecols=(0, resistance_col), delimiter=',', unpack=True)
    # R = resistance * 2*np.pi/np.log(2) # Sheet resistance infinite sheet
    R = resistance * np.pi / np.log(2)  # Sheet resistance finite sheet

    sigma = 1 / R  # Conductivity
    C = 11.5E-9  # 11.5 nanofarad
    curr = gV / R
    mob = 1 / C * np.diff(sigma) / np.diff(gV)

    # Plot values
    gV_mob = gV[0:-1]
    ax.plot(gV_mob, mob, label='Mobility')
    ax1.plot(gV, resistance, label='Resistance')
    fig.suptitle(title)
    # plt.tight_layout()
    ax.legend()
    ax1.legend()
    figname = fn.split('.')[0] + '_mobility.png'
    plt.savefig(figname)
    # Save to mobility file
    savename = fn.split('.')[0] + '_mobility.dat'
    np.savetxt(savename, np.c_[gV_mob, mob], header="Gatevoltage    Mobility")
plt.show()
