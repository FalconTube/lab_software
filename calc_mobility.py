import matplotlib.pyplot as plt
import numpy as np
import glob
import sys


print('This programm will calculate the mobility for all files' +\
'with the name "gatesweep*" in a specified folder.' )
folder = str(input('Define Foldername: '))
if not folder or folder == '':
    print('No folder specified. Exiting...')
    sys.exit()
if folder[-1] == '/':
    folder = folder[0:-1]
print('Working in Folder: {}'.format(folder))


for fn in glob.glob('{}/gatesweep*.dat'.format(folder)):
    # Set up plots
    fig = plt.figure()
    ax = fig.add_subplot(211)
    ax1 = fig.add_subplot(212)
    ax1.set_xlabel('Gatevoltage [V]')
    ax1.set_ylabel(r'Resistance [$\Omega$]')
    ax.set_ylabel(r'Mobility')
    title = fn.split('.')[0]

    # Read gatevoltage and Resistance            
    resistance_col = 4 # Define number, that resistance is in (currently 4 everywhere)
    gV, resistance = np.loadtxt(fn, usecols=(0,resistance_col),
    delimiter=',', unpack=True) 
    R = resistance * 2*np.pi/np.log(2) # Sheet resistance
    sigma = 1/R # Conductivity
    C = 11.5E-9 # 11.5 nanofarad
    curr = gV/R
    mob = 1/C * np.diff(sigma)/np.diff(gV)
    
    # Plot values
    gV_mob = gV[0:-1]
    ax.plot(gV_mob,mob,label='Mobility')
    ax1.plot(gV,resistance,label='Resistance')
    fig.suptitle(title)
    # plt.tight_layout()    
    ax.legend()
    ax1.legend()

    # Save to mobility file
    savename = fn.split('/')[-1].split('.')[0] + '_mobility.dat'
    np.savetxt(savename, np.c_[gV_mob, mob],
     header="Gatevoltage    Mobility")
plt.show()


