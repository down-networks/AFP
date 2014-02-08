'''
Created on Feb 7, 2014

@author: Christopher Phillippi
@summary: High level API that stores uncleaned data into cleaned store
'''

from cleaner import settings
from cleaner import filers
from cleaner import schema
from cleaner import helpers
import multiprocessing as mp
import os

def cleanSources( uncleanStore, numWorkers = settings.MAX_WORKERS ):
    """
    Cleans all files in unclean directory, using numWorkers processors
    Call this function directly to clean data
    """
    pool = mp.Pool( numWorkers )
    print "Cleaning data in <%s> with <%d> workers." % ( uncleanStore, numWorkers )
    
    def clean( source ):
        try:
            filer = filers.BatchFiler( schema.getSchema( source ) )
        except Exception as e:
            return [e]
        sourceDir = os.path.join( settings.UNCLEAN_STORE, source )
        uncleaned = ( ( filer, sourceDir, uncleaned ) for uncleaned in os.listdir( sourceDir ) )
        return pool.map( _cleanFile, uncleaned )
    results = helpers.flatten( [ clean( source ) for source in os.listdir( uncleanStore ) ] )
    added = [ result for result in results if result.added  ]
    notAdded = [ result for result in results if not result.added ]
    return { "Added" : added, "Unable To Add" : notAdded }

# Multithreading library requires this be a function rather than method or inner function
# Unpickleable otherwise
def _cleanFile( args ):
    filer, cleanDir, uncleanFile = args
    return filer.write( os.path.join( cleanDir, uncleanFile ) )

if __name__ == '__main__':
    cleanSources( settings.UNCLEAN_STORE )