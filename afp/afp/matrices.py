'''
.. module:: matrices

This module contains the matrix generating functions

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import cleaner.retrieve as retrieve
import afp.keywords as keywords
import afp.count as count
import afp.normalize as normalize
import afp.linalg as linalg
import afp.settings as settings
import numpy as np
   
def tfIdf( articles, keywordMap = keywords.getKeywordToIndexMap() ):
    """Returns a sparse tf-idf Matrix
    
    :param articles: An iterable of article strings. See :func:`cleaner.retrieve.getCleanArticles`
    :param keywordMap: A mapping of keywords to their matrix column indices. See :func:`afp.keywords.getKeywordToIndexMap`
    """
    counts = count.WordCounter( keywordMap )( articles )
    return normalize.TfIdf()( counts )

if __name__ == "__main__":
    corr = linalg.corr( tfIdf( retrieve.getCleanArticles() ) )
    np.savetxt( settings.RESULTS_DIR + '/corr2012.csv', corr, delimiter = ',' )
