
from testing.testTools import *

import Manhattan_Plot
import unittest


accuracy_high = 6
accuracy_low = 2

class TestPanelCheck(unittest.TestCase):   
    
    def testManhattanCalc6PCs1a(self):
        
        print "Manhattan Plot tests (8) ..."
        
        
        # get averaged data for assessor 12 of the cheese data set:
        data = cheese["ass12"]
       
                
        # get correct results
        res = manh_res["ass12_6pc"]
        
        scores, loadings, e_variable_variances = Manhattan_Plot.ManhattanCalc(data, PCs=6, standardize=False)    
        
        self.failUnlessEqual(e_variable_variances.shape, res.shape, 'wrong shape')
        
        for i in range(len(res)):
            for j in range(len(res[0])):
                self.failUnlessAlmostEqual(e_variable_variances[i,j], res[i,j], accuracy_high, 'wrong value in explained_variable_variances[%i,%i] (Manhattan Calculation) (correct: %f, incorrect: %f)' % (i,j,res[i,j],e_variable_variances[i,j]))      


    def testManhattanCalc6PCs1b(self):
        
        # get averaged data for assessor 12 of the cheese data set:
        data = cheese["ass12"]
        
        # get correct results
        res = manh_res["ass12_6pc_std"]
        
        scores, loadings, e_variable_variances = Manhattan_Plot.ManhattanCalc(data, PCs=6, standardize=True)
        
        self.failUnlessEqual(e_variable_variances.shape, res.shape, 'wrong shape')
        
        for i in range(len(res)):
            for j in range(len(res[0])):
                self.failUnlessAlmostEqual(e_variable_variances[i,j], res[i,j], accuracy_high, 'wrong value in explained_variable_variances[%i,%i] (Manhattan Calculation) (correct: %f, incorrect: %f)' % (i,j,res[i,j],e_variable_variances[i,j]))
                
       
       
    def testManhattanCalc6PCs2a(self):
        
        # get averaged data for assessor 12 of the cheese data set:
        data = cheese["ass12"]
                
        # get correct results
        res = manh_res["ass12_6pc_scores"]
        
        scores, loadings, e_variable_variances = Manhattan_Plot.ManhattanCalc(data, PCs=6, standardize=False)

        self.failUnlessEqual(scores.shape, res.shape, 'wrong shape')
        
        for i in range(len(res)):
            for j in range(len(res[0])):
                self.failUnlessAlmostEqual(scores[i,j], res[i,j], accuracy_high, 'wrong value in scores[%i,%i] (Manhattan Calculation) (correct: %f, incorrect: %f)' % (i,j,res[i,j],scores[i,j]))
                
    def testManhattanCalc6PCs2b(self):
        
        # get averaged data for assessor 12 of the cheese data set:
        data = cheese["ass12"]
                
        # get correct results
        res = manh_res["ass12_6pc_std_scores"]
        
        scores, loadings, e_variable_variances = Manhattan_Plot.ManhattanCalc(data, PCs=6, standardize=True)
        
        self.failUnlessEqual(scores.shape, res.shape, 'wrong shape')
        
        for i in range(len(res)):
            for j in range(len(res[0])):
                self.failUnlessAlmostEqual(scores[i,j], res[i,j], accuracy_high, 'wrong value in scores[%i,%i] (Manhattan Calculation) (correct: %f, incorrect: %f)' % (i,j,res[i,j],scores[i,j]))
                       
     
     
    def testManhattanCalc6PCs3a(self):
        
        # get averaged data for assessor 12 of the cheese data set:
        data = cheese["ass12"]
        
                
        # get correct results
        res = manh_res["ass12_6pc_loadings"]
        
        scores, loadings, e_variable_variances = Manhattan_Plot.ManhattanCalc(data, PCs=6, standardize=False)
        
        
        self.failUnlessEqual(loadings.shape, res.shape, 'wrong shape')
        
        for i in range(len(res)):
            for j in range(len(res[0])):
                self.failUnlessAlmostEqual(loadings[i,j], res[i,j], accuracy_high, 'wrong value in loadings[%i,%i] (Manhattan Calculation) (correct: %f, incorrect: %f)' % (i,j,res[i,j],loadings[i,j]))

    def testManhattanCalc6PCs3b(self):
        
        # get averaged data for assessor 12 of the cheese data set:
        data = cheese["ass12"]
        
                
        # get correct results
        res = manh_res["ass12_6pc_std_loadings"]
        
        scores, loadings, e_variable_variances = Manhattan_Plot.ManhattanCalc(data, PCs=6, standardize=True)
        
        self.failUnlessEqual(loadings.shape, res.shape, 'wrong shape')
        
        for i in range(len(res)):
            for j in range(len(res[0])):
                self.failUnlessAlmostEqual(loadings[i,j], res[i,j], accuracy_high, 'wrong value in loadings[%i,%i] (Manhattan Calculation) (correct: %f, incorrect: %f)' % (i,j,res[i,j],loadings[i,j])) 



    def testManhattanCalc6PCs4(self):
        
        # get averaged data for assessor 12 of the cheese data set:
        data = cheese["ass12"]
                
        # get correct results
        res = manh_res["ass12_14pc"]
        
        scores, loadings, e_variable_variances = Manhattan_Plot.ManhattanCalc(data, PCs=14, standardize=False)
             
        self.failUnlessEqual(e_variable_variances.shape, res.shape, 'wrong shape')
        
        for i in range(len(res)):
            for j in range(len(res[0])):
                self.failUnlessAlmostEqual(e_variable_variances[i,j], res[i,j], accuracy_high, 'wrong value in explained_variable_variances[%i,%i] (Manhattan Calculation) (correct: %f, incorrect: %f)' % (i,j,res[i,j],e_variable_variances[i,j]))      
  
  
  
    def testManhattanCalc6PCs5(self):
        
        # get averaged data for assessor 12 of the cheese data set:
        data = cheese["ass3"]
        
        # get correct results
        res = manh_res["ass3_6pc"]
        
        
        scores, loadings, e_variable_variances = Manhattan_Plot.ManhattanCalc(data, PCs=6, standardize=False)
      
        self.failUnlessEqual(e_variable_variances.shape, res.shape, 'wrong shape')
        
        for i in range(len(res)):
            for j in range(len(res[0])):
                self.failUnlessAlmostEqual(e_variable_variances[i,j], res[i,j], accuracy_high, 'wrong value in explained_variable_variances[%i,%i] (Manhattan Calculation) (correct: %f, incorrect: %f)' % (i,j,res[i,j],e_variable_variances[i,j]))      





if __name__ == '__main__':
    unittest.main()