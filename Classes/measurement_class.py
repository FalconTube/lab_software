# __author__ = Yannic Falke

from Classes.device_classes import *


class Measurement():
    initial_fastplot = 0
    def __init__(self):
        pass

    def finish_measurement(self):
        ''' Close all Keithleys or Lakeshore devices, close savefile '''
        print("Finished measurement successfully. Closing all devices\
        and savefile.")
        self.savefile.close()
        for i in Keithley.instances:
            i.close()
        for i in Lakeshore.instances:
            i.close()
        if plt.get_fignums():
            # If plots exists, then save them
            print('Saving a PNG of the measurement...')
            plt.savefig(self.savename_png)
        else:
            pass

        print('Successfully closed everything. Exiting...')
        sys.exit()

    def ask_savename(self):
        ''' Creates savename based on user input\n
            Creates self.savename and self.savename'''
        savefolder = str(input('Input name of DIRECTORY: ') or 'testfolder') 
        self.savename = str(input('Input name of FILENAME: ') or 'testfile')
        if len(self.savename) >= 4:
            if not self.savename[-4] == '.':
                self.savename += ".dat"
        if not os.path.exists(savefolder):
            os.makedirs(savefolder)
        os.chdir(savefolder)
        if os.path.isfile(self.savename):
            choice = str(input("File already exists. Do you want to rename? [y/n] ")\
            or "n")
            if choice == 'y':
                self.savename = input("New filename: ")
                if not "." in self.savename:
                    self.savename += ".dat"
            if choice == 'n':
                i = 1
                save_tmp = self.savename.split('.')[0]
                while os.path.isfile(save_tmp + "_{}.dat".format(i)):
                    i += 1
                self.savename = save_tmp + "_{}.dat".format(i)
        basename = self.savename.split('.')[0]
        self.savename_png = basename + ".png"
        print('Savename is {}'.format(self.savename))

    def create_savefile(self, savestring):
        # if not hasattr(self, self.savename):
        #     print('Savename is not defined. Please define it now: ')
        #     self.ask_savename()
        ''' Creates savefile and generates header '''
        self.savefile = open(self.savename, "w")
        self.savefile.write(savestring + "\n")
    
    def fast_plotter(self, x: list, y: list, ax_num=1, ax_pos=0, p=40,
        plotstyle='k.', labels=("","")) -> None:
        """ Fast plotter for x and y, both as lists.\n
        ax_num: Values = 1 or 2, number of axes to create.\n
        ax_pos: Values = 1 or 2, upper or lower position.\n
        p: Controls how much percentage to ax boundaries is added.
        """
        self.currx, self.curry = x[-1], y[-1]

        def percentage(x, p=p):
            return x + x/100*p
        
        def check_boundaries(ax_num=1, ax_pos=0):
            ax_pos = int(ax_pos-1)
            if ax_num == 2:
                fast_ax = self.fast_fig.axes[ax_pos]
            else:
                fast_ax = self.fast_ax
            xlim_min, xlim_max = fast_ax.get_xlim()
            ylim_min, ylim_max = fast_ax.get_ylim()
            triggered = 0
            # print(self.curry, percentage_added(ylim_min, p=5))
            if self.curry >= percentage(ylim_max, p=-5):
                newval = percentage(self.curry)
                fast_ax.set_ylim(ylim_min, newval)
                triggered += 1
            if self.currx >= percentage(xlim_max, p=-5):
                # print(percentage(ylim_max), self.curry)
                newval = percentage(self.currx)
                fast_ax.set_xlim(xlim_min, newval)
                triggered += 1
            if self.currx <= percentage(xlim_min, p=5):
                newval = percentage(self.currx)
                print(self.currx,newval)
                fast_ax.set_xlim(newval, xlim_max)
                triggered += 1
            if self.curry <= percentage(ylim_min, p=5):
                newval = percentage(self.curry)
                fast_ax.set_ylim(newval, ylim_max)
                triggered += 1
            if triggered >= 1:
                return True
            else:
                return False



        # Perform fastplot    

        # Create figures
        if self.initial_fastplot == 0:
            x, y = [], []
            self.fast_fig = plt.figure()
            # Hard coded number of axes for now...
            if ax_num == 1:
                self.fast_ax = self.fast_fig.add_subplot(111)
                self.fast_line, = self.fast_ax.plot(x, y, plotstyle) 

            if ax_num == 2:
                self.fast_ax_1 = self.fast_fig.add_subplot(211)
                self.fast_line_1, = self.fast_ax_1.plot(x, y, plotstyle) 
                self.fast_ax_2 = self.fast_fig.add_subplot(212)
                self.fast_line_2, = self.fast_ax_2.plot(x, y, plotstyle) 
            plt.pause(0.001)
            self.initial_fastplot +=1 
        
        # Set labels
        if self.initial_fastplot <2:
            if ax_num == 1:
                thisax = self.fast_fig
                plt.xlabel(labels[0])
                plt.ylabel(labels[1])
        if ax_num == 2:
            thisax = self.fast_fig.axes[int(ax_pos-1)]
            if str(thisax.get_xlabel()) == '':
                thisax.set_xlabel(labels[0])
                thisax.set_ylabel(labels[1])
        

        # Initial plot has been created, now start plotting
        else:
            
            if check_boundaries(ax_num, ax_pos):
                # Sets new axes and replots whole plot
                if ax_num == 1:
                    self.fast_line.set_data(x,y)
                if ax_num == 2:
                    if ax_pos == 1:
                        self.fast_line_1.set_data(x,y)
                    if ax_pos == 2:
                        self.fast_line_2.set_data(x,y)
                plt.pause(0.001)
            else:
                # Only redraws points
                if ax_num == 1:
                    self.fast_line.set_data(x,y)
                    # self.fast_ax.draw_artist(self.fast_ax.patch)
                    self.fast_ax.draw_artist(self.fast_line)
                    self.fast_fig.canvas.update()
                    self.fast_fig.canvas.flush_events()
                if ax_num == 2:
                    if ax_pos == 1:
                        self.fast_line_1.set_data(x,y)
                        self.fast_ax_1.draw_artist(self.fast_line_1)
                    if ax_pos == 2:
                        self.fast_line_2.set_data(x,y)
                        self.fast_ax_2.draw_artist(self.fast_line_2)
                        self.fast_fig.canvas.update()
                        self.fast_fig.canvas.flush_events()
            
            
        

if __name__ == '__main__':
    print('\
    This is the file holding the general Measurement class.\
    Calling this directly is of no use.\
    Exiting ...')
    sys.exit()


    
