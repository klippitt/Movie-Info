"""This contains unit tests for the movieinfo package."""


import unittest

import sys
import os

#import the program from the src directory
pathname = os.path.dirname(sys.argv[0])

sys.path.append(os.path.join(os.path.abspath(pathname), '..', 'src'))
from main import *


class UnitTests(unittest.TestCase):

    _test_cache_file = "test.p"

    @classmethod
    def setUpClass(self):
        self.matcher = Matcher(Config.movie_match_regex, Config.allowed_file_types)
        self.movieLookup = MovieLookup()
        self.normaliser = Normaliser()
        self.idFinder = IdFinder()
        self.cache = Cache(self._test_cache_file)
        #Ensure the cache was deleted previously
        self.cache.delete_cache()

    @classmethod
    def tearDownClass(self):
        #Delete the cache now that we're done
        self.cache.delete_cache()

    #####################################################
    #Test the Config Class
    #####################################################
    def testConfigVarsExist(self):
        self.assertGreater(Config.timeout, 0)
        self.assertGreater(len(Config.allowed_file_types), 0)

    def testConfigVarsNotExist(self):
        with self.assertRaises(AttributeError):
            print Config.fake

    #####################################################
    #Test the Matcher Class
    #####################################################

    def testFileExtensionValidation(self):
        is_valid_extension = self.matcher._is_valid_extension("avi")
        self.assertTrue(is_valid_extension)

    def testFindInDirectory(self):
        directory = "./tests/testMovieDirectory"
        self.matcher.find_in_directory(directory)

        movieMatches = self.matcher.get_matches()
        unMatched = self.matcher.get_ignored()

        numberOfMatches = len(movieMatches)
        numberOfNonMatches = len(unMatched)

        self.assertEquals(numberOfMatches, 11)
        self.assertEquals(numberOfNonMatches, 1)

    #####################################################



    #####################################################
    #Test the MovieLookup Class
    #####################################################
    def testBadMovieLookup(self):
        title = "Film Does Not Exist"
        lookupResult = self.movieLookup.lookup_by_title(title)
        isValidLookup = MovieDataUtil.is_valid_lookup_result(lookupResult)
        self.assertFalse(isValidLookup)

    def testGoodMovieLookup(self):
        title = "true grit"
        lookupResult = self.movieLookup.lookup_by_title(title)
        isValidLookup = MovieDataUtil.is_valid_lookup_result(lookupResult)
        self.assertTrue(isValidLookup)
    #####################################################


    #####################################################
    #Test the IdFinder Class
    #####################################################
    def testFindKnownMovie(self):
        knownId = "tt0105793"
        lookupId = self.idFinder.find_id_by_title("Waynes World 1992")
        self.assertEquals(lookupId, knownId)

    def testFindNonExistantMovie(self):
        lookupId = self.idFinder.find_id_by_title(" !!^&*#@ Some fake film title...")
        self.assertIsNone(lookupId)


    #####################################################
    #Test the Cache Class
    #####################################################
    def testCacheEmpty(self):
        self.cache = Cache(self._test_cache_file)

        cache_size = self.cache.get_cache_size()
        self.assertEquals(cache_size, 0)

        self.cache.delete_cache()

    def testCacheNotEmpty(self):
        self.cache = Cache(self._test_cache_file)

        self.cache.add_to_cache("key","value")
        cache_size = self.cache.get_cache_size()
        self.assertEquals(cache_size, 1)

        self.cache.delete_cache()

    def testCacheFind(self):
        self.cache = Cache(self._test_cache_file)

        self.cache.add_to_cache("key","value")
        item = self.cache.get("key")
        self.assertEquals(item, "value")

        self.cache.delete_cache()

    def testCacheCantFind(self):
        self.cache = Cache(self._test_cache_file)

        item = self.cache.get("invalid_key")
        self.assertIsNone(item)

        self.cache.delete_cache()

    #####################################################
    #Integration Tests
    #####################################################

    def testIdFindAndMovieLookup(self):
        """
        Lookup a movie with an incorrect title,
        Find the IMDB id for this movie,
        Find the correct title
        """
        title = "Waynes world 2"
        actualTitle = "Wayne's World 2"

        lookupResult = self.movieLookup.lookup_by_title(title)
        isValidLookup = MovieDataUtil.is_valid_lookup_result(lookupResult)
        #Check that this isn't a correct title (it is missing an apostrophe)
        self.assertFalse(isValidLookup)

        foundId = self.idFinder.find_id_by_title(title)
        #check that we found an id for this movie
        self.assertIsNotNone(foundId)

        lookupResult = self.movieLookup.lookup_by_id(foundId)
        isValidLookup = MovieDataUtil.is_valid_lookup_result(lookupResult)
        self.assertTrue(isValidLookup)

        #now check the new title compares to the actual title
        self.assertEquals(lookupResult['Title'], actualTitle)


if __name__ == '__main__':
    unittest.main()
