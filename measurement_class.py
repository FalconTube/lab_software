# __author__ = Yannic Falke

from device_classes import *


class Measurement():
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

        print('Successfully closed everything. Exiting...')
        sys.exit()

    def ask_savename(self):
        ''' Creates savename based on user input '''
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
        print('Savename is {}'.format(self.savename))

    def create_savefile(self, savestring):
        # if not hasattr(self, self.savename):
        #     print('Savename is not defined. Please define it now: ')
        #     self.ask_savename()
        ''' Creates savefile and generates header '''
        self.savefile = open(self.savename, "w")
        self.savefile.write(savestring + "\n")
        

if __name__ == '__main__':
    print('\
    This is the file holding the general Measurement class.\
    Calling this directly is of no use.\
    Exiting ...')
    sys.exit()


    
