'''
.. module:: normalize

This module contains the functors which normalize all types of inputs, 
from matrices to articles, to an expected format.

.. moduleauthor:: Christopher Phillippi <c_phillippi@mfe.berkeley.edu>
'''

import numpy as np
import scipy.sparse as sparse
from itertools import chain

class NormalizerBase( object ):
    """Base class for Normalizing Functors
    
    Extending Requires method: **normalize()**
    """
    def __call__( self, raw ):
        return self.normalize( raw )
    
    def normalize( self, matrix ):
        NotImplemented

class TfIdf( NormalizerBase ):
    """Functor normalizing count matrices to tf-idf matrices
    """
    def normalize( self, counts ):
        """Normalizes count matrix into tf-idf matrix
        
        :param counts: Counts of words in each article. Elements *may* be negative. Sign is passed-through.
        :type counts: numpy matrix, sparse scipy matrix, or Pandas Dataframe
        """
        n = counts.shape[ 0 ]
        def normalizeScipy():
            absCounts = np.abs( counts )
            def tf():
                return counts.sign().multiply( absCounts.log1p() )
            def idf():
                occurred = ( absCounts > 0 ).asfptype()
                occurrences = sum( occurred, 0 ).todense() 
                occurrences[ occurrences == 0 ] = 1
                return sparse.csr_matrix( np.log( float( n ) / occurrences ) )
            return tf().multiply( idf() )
        def normalizeDf():
            def occurred( count ): return count != 0
            def tfidf( counts ):
                absCounts = counts.abs()
                def tf( counts ):
                    return np.sign( counts ).mul( np.log1p( absCounts ) )
                def idf():
                    likelihood = max( 1.0, occurred( absCounts ).sum() ) / float( n )
                    return -np.log( likelihood )
                return tf( counts ).mul( idf() )
            return counts.apply( tfidf )
        def normalizeRolling():
            def occurred( count ): return count != 0
            absCounts = np.abs( counts )
            def tf():
                return np.sign( counts ) * np.log1p( absCounts )
            def idf():
                likelihood = max( 1.0, sum( occurred( absCounts ) ) ) / float( n )
                return -np.log( likelihood )
            return tf() * idf()
        try:
            return normalizeScipy()
        except:
            try:
                return normalizeDf()
            except:
                return normalizeRolling()
            
class Article( NormalizerBase ):
    """Functor normalizing articles to be searched for keywords
    
    Replaces the following: 
    
    ======  ========  ============  =============== 
    From    To        Example       Result     
    ======  ========  ============  ===============
    ''s'    ''        boogle's      boogle    
    'n\'t'   ' not'    didn't        did not     
    '/'     ' or '    addle/boogle  addle or boogle 
    ======  ========  ============  ===============
    
    """
    wordReplacements = [  # FROM, TO
                         ( '\'s', '' ),
                         ( 'n\'t', ' not' ),
                         ( '/', ' or ' ),
                       ]
        
    def normalize( self, article ):
        """Normalizes article to be outputed in iterable of words where each word has 
        been replaced according to member: *wordReplacements*. Also forces all-lowercase.
        """
        def getPossibleKeywords( line ):
            def normalizeKeyword( word ):
                def replaceFromTo( interWord, fromTo ):
                    replFrom, to = fromTo
                    return interWord.replace( replFrom, to )
                return reduce( replaceFromTo, self.wordReplacements, word )
            return ( normalizeKeyword( word ) for word in line.split( " " ) )
        return chain.from_iterable( ( getPossibleKeywords( line ) 
                                      for line in article.lower().split( "\n" ) ) )
        
        #=======================================================================
        # def extractKeywords( sent ):
        #     def concatNamedEntities( sentTree ):
        #         try:
        #             tag = sentTree.node
        #         except AttributeError:
        #             word = sentTree[ 0 ]
        #             return word
        #         else:
        #             if( tag == 'NE' ):
        #                 return " ".join( ( name for name, tag in sentTree ) )
        #             return ( concatNamedEntities( subTree ) for subTree in sentTree )
        #     tokenized = nltk.word_tokenize( sent )
        #     tagged = nltk.pos_tag( tokenized )
        #     chunked  = nltk.ne_chunk( tagged, binary=True )
        #     return concatNamedEntities( chunked )
        # return [ keyword.strip().lower() 
        #          for sent in nltk.sent_tokenize( article )
        #          for keyword in extractKeywords( sent ) ] 
        #=======================================================================
        

