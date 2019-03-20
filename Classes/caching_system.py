import time
import numpy as np
import sys
import os


class CachingSystem():
    def __init__(self):
        self.use_cache = False
        self._initial_caching = 0
        self.cache_counter = 0
        self.cachefile = '.own_cache'
        self.ask_for_cache()
        if os.path.isfile(self.cachefile):
            self.cached_vals = self.read_cache()
        

    def ask_for_cache(self):
        usage = input(
            'Would you like to use the cached values' +
            ' from the last session? (y/n)' or 'n')
        if usage.lower().strip() == 'y':
            print('Okay, using cached values...')
            self.use_cache = True
        else:
            print('Will not use the cache.')
            self.use_cache = False

    def write_cache(self, argument):
        if self._initial_caching == 0:
            open(self.cachefile, 'w').close()  # Clear cachefile

        with open(self.cachefile, 'a') as f:
            f.write('{}\n'.format(argument))

    def read_cache(self):
        values = []
        with open(self.cachefile, 'r') as f:
            for line in f:
                stripline = line.rstrip()
                values.append(stripline)
        return values

    def cache_input(self, input_arg, default=''):
        ''' Use this instead of standard input if you want to cache. '''
        if self.use_cache == False:
            outval = input(input_arg)
        else:
            outval = self.cached_vals[self.cache_counter]
            print('{} {}'.format(input_arg, outval))
        if outval == '':
            outval = default
        self.write_cache(outval)
        self._initial_caching += 1
        self.cache_counter += 1
        return outval


if __name__ == '__main__':
    print('Calling this caching class directly is of no use. Exiting...')
    sys.exit()
