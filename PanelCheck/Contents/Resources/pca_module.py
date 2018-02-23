#!/usr/bin/env python
from numpy import abs, array, average, corrcoef, mat, shape, std, sum, transpose, zeros
from numpy.linalg import svd

try:
    import c_nipals
    import_ok = True
except:
    import_ok = False
     
        
    
################### Preprocessing Methods ###################
def mean_center(X):
    (rows, cols) = shape(X)
    new_X = zeros((rows, cols), float)
    _averages = average(X, 0)
        
    for row in range(rows):
        new_X[row, 0:cols] = X[row, 0:cols] - _averages[0:cols]
    return new_X
        
        
def standardization(X):        
    (rows, cols) = shape(X)
    new_X = zeros((rows, cols))
    _STDs = std(X, 0)
        
    for value in _STDs:
        if value == 0: raise ZeroDivisionError, 'division by zero, cannot proceed'
        
    for row in range(rows):
        new_X[row, 0:cols] = X[row, 0:cols] / _STDs[0:cols]
    return new_X        


       
################### NIPALS array help functions ###################
def get_column(E):
    """
    returns a column which has a non-zero eigenvalue
    """
    (rows, cols) = shape(E)
    
    for col_ind in range(cols):
        t = E[:,col_ind] # extract a column
        if (eigenvalue_vec(t) > 0):
            return t
    raise ValueError, 'all column vectors in E have zero-eigenvalues' # error: sum of matrix is 0

def eigenvalue_vec(v):
    """
    returns: (transpose(v) * v) the eigen-value of "matrix" v as float or int
    """
    return sum(v * v);

def mat_prod(A, x):
    """
    returns: b of b = Ax    
    product of:  matrix A (m,n) * vector x (n) = vector b (m)
    """
    #m = A.shape[0]
    #b = zeros((m), float)
    
    # calc: Ax = b
    #for i in range(m):
    #    b[i] = sum(A[i,:]*x)

    return array(map(lambda a: sum(a[:]*x), A))

def remove_tp_prod(E, t, p):
    """
    sets: E = E - (t*transpose(p))
    E: (m, n)-matrix, (t*transpose(p)): (m, n)-matrix
    """
    
    m = E.shape[0]
    for i in range(m):
        E[i, :] = E[i, :] - (t[i] * p)
       

################### NIPALS Algorithm ###################
"""
  Estimation of PC components with the iterative NIPALS method: 


  E[0] = mean_center(X)  (the E-matrix for the zero-th PC)

  t = E(:, 0)  (a column in X (mean centered) is set as starting t vector)

  for i=1 to (PCs):
    
    1  p=(E[i-1]'t) / (t't)  Project X onto t to find the corresponding loading p
    
    2  p = p * (p'p)^-0.5  Normalise loading vector p to length 1
    
    3  t = (E[i-1]p) / (p'p)  Project X onto p to find corresponding score vector t
    
    4  Check for convergence, if difference between eigenval_new and eigenval_old is larger than threshold*eigenval_new return to step 1
    
    5  E[i] = E[i-1] - tp'  Remove the estimated PC component from E[i-1] 
    
"""    
def nipals_mat(X, PCs, threshold, E_matrices):
    """
    nipals python prototype (USING NUMPY MATRIX)
    
    returns:
    - Scores
    - Loadings
    - explained_var (explained variance for each PC)
    """
    (rows, cols) = shape(X)

    maxPCs = min(rows, cols) # max number of PCs is min(objects, variables)
    if maxPCs < PCs: PCs = maxPCs # change to maxPCs if PCs > maxPCs
    
    Scores = zeros((rows, PCs), float) # all Scores (T)
    Loadings = zeros((PCs, cols), float) # all Loadings (P)
    
    E = mat(X.copy()) #E[0]  (should already be mean centered)


    if E_matrices:
        Error_matrices = zeros((PCs, rows, cols), float) # all Error matrices (E)
    else:
        explained_var = zeros((PCs))
        tot_explained_var = 0
    
        # total object residual variance for PC[0] (calculating from E[0])
        e_tot0 = 0 # for E[0] the total object residual variance is 100%
        for k in range(rows):
            e_k = array(E[k, :])**2
            e_tot0 += sum(e_k)
            
    

    t = get_column(E) # extract a column
    
   
    
    # do iterations (0, PCs)
    for i in range(PCs):
        convergence = False
        ready_for_compare = False
        E_t = transpose(E)
        
        while not convergence:
            eigenval = float(transpose(t)*t)
            p = (E_t*t) / eigenval # ........................................... step 1
            
            _p = float(transpose(p)*p)        
            p = p * _p**(-0.5) # ............................................... step 2
            t = (E*p) / (transpose(p)*p) # ..................................... step 3
            
            
            eigenval_new = float(transpose(t)*t)
            if not ready_for_compare:
                ready_for_compare = True
            else: # ready for convergence check
                if (eigenval_new - eigenval_old) < threshold*eigenval_new: # ... step 4
                    convergence = True           
            eigenval_old = eigenval_new;
            
            
        p = transpose(p)
        E = E - (t*p) # ........................................................ step 5
        
        # add Scores and Loadings for PC[i] to the collection of all PCs
        _t = array(t) # NOT optimal
        Scores[:, i] = _t[:,0]; Loadings[i, :] = p[0,:] # co
     
        if E_matrices:
		# complete error matrix
		# can calculate object residual variance (row-wise) or variable resiudal variance (column-wise)
		# total residual variance can also be calculated
		
		Error_matrices[i] = E.copy()
        
        else:
		# total object residual variance for E[i]
		e_tot = 0
		
		for k in range(rows):
		    e_ = zeros((cols), float)
		    for k_col in range(cols):
		        e_[k_col] = E[k, k_col]*E[k, k_col]
		    e_tot += sum(e_)
		tot_obj_residual_var =  (e_tot / e_tot0)
		explained_var[i] = 1 - tot_obj_residual_var - tot_explained_var
		tot_explained_var += explained_var[i]
		
		
		

    if E_matrices:
        return Scores, Loadings, Error_matrices
    return Scores, Loadings, explained_var    



def nipals_arr(X, PCs, threshold, E_matrices):
    """
    nipals python (USING NUMPY ARRAY)
    
    returns:
    - Scores (T)
    - Loadings (P)
    - Error (E)
      - explained_var (explained variance for each PC)
          or
      - E-matrix (for each PC)
    """
    (rows, cols) = shape(X)
    maxPCs = min(rows, cols) # max number of PCs is min(objects, variables)
    if maxPCs < PCs: PCs = maxPCs # change to maxPCs if PCs > maxPCs

    Scores = zeros((rows, PCs), float) # all Scores (T)
    Loadings = zeros((PCs, cols), float) # all Loadings (P)
    
    E = X.copy() #E[0]  (should already be mean centered)
    
    if E_matrices:
        Error_matrices = zeros((PCs, rows, cols), float) # all Error matrices (E)
    else:
        explained_var = zeros((PCs))
        tot_explained_var = 0
    
        # total object residual variance for PC[0] (calculating from E[0])
        e_tot0 = 0 # for E[0] the total object residual variance is 100%
        for k in range(rows):
            e_k = E[k, :]**2
            e_tot0 += sum(e_k)      
            
    

    t = get_column(E) # extract a column
    p = zeros((cols), float)
    
    # do iterations (0, PCs)
    for i in range(PCs):
        convergence = False
        ready_for_compare = False
        E_t = transpose(E)
        
        while not convergence:
            _temp = eigenvalue_vec(t)
            p = mat_prod(E_t, t) / _temp # ..................................... step 1
            
            _temp = eigenvalue_vec(p)**(-0.5)
            p = p * _temp # .................................................... step 2
            
            _temp = eigenvalue_vec(p)
            t = mat_prod(E, p) / _temp # ....................................... step 3
            
            
            eigenval_new = eigenvalue_vec(t)
            if not ready_for_compare:
                ready_for_compare = True
            else: # ready for convergence check
                if (eigenval_new - eigenval_old) < threshold*eigenval_new: # ... step 4
                    convergence = True           
            eigenval_old = eigenval_new;

        remove_tp_prod(E, t, p) # .............................................. step 5
        
        # add Scores and Loadings for PC[i] to the collection of all PCs
        Scores[:, i] = t; Loadings[i, :] = p
        
        
        if E_matrices:
		# complete error matrix
		# can calculate object residual variance (row-wise) or variable resiudal variance (column-wise)
		# total residual variance can also be calculated
		
		Error_matrices[i] = E.copy()
        
        else:
		# total object residual variance for E[i]
		e_tot = 0
		for k in range(rows):
		    e_k = E[k, :]**2
		    e_tot += sum(e_k)
		tot_obj_residual_var =  (e_tot / e_tot0)
		explained_var[i] = 1 - tot_obj_residual_var - tot_explained_var
		tot_explained_var += explained_var[i]

    if E_matrices:
        return Scores, Loadings, Error_matrices
    else:
        return Scores, Loadings, explained_var 
    
    

def nipals_c(X, PCs, threshold, E_matrices):
    """
    nipals (c implementation)
    
    returns:
    T (PC Scores)
    P (PC Loadings) 
    explained_var (PC explained variance)
    """
    
    if not import_ok:
        raise ImportError, "could not import c_nipals python extension"
    else:  

        (rows, cols) = shape(X)

	maxPCs = min(rows, cols) # max number of PCs is min(objects, variables)
	if maxPCs < PCs: PCs = maxPCs # change to maxPCs if PCs > maxPCs

	Scores = zeros((rows, PCs), float) # all Scores (T)
	Loadings = zeros((PCs, cols), float) # all Loadings (P)

	E = X.copy() #E[0]  (should already be mean centered)

        if E_matrices:
            Error_matrices = zeros((PCs, rows, cols), float) # all Error matrices (E)
            c_nipals.nipals2(Scores, Loadings, E, Error_matrices, PCs, threshold)
            return Scores, Loadings, Error_matrices
        else:
	    explained_var = c_nipals.nipals(Scores, Loadings, E, PCs, threshold)
	    return Scores, Loadings, explained_var



################### Principal Component Analysis (using NIPALS) ###################
def PCA_nipals(X, standardize=True, PCs=10, threshold=0.0001, E_matrices=False):
    """ USING NUMPY MATRIX """
    X = mean_center(X)
        
    if standardize:
        X = standardization(X)
    
    return nipals_mat(X, PCs, threshold, E_matrices) 
    

def PCA_nipals2(X, standardize=True, PCs=10, threshold=0.0001, E_matrices=False):
    """ USING NUMPY ARRAY """
    X = mean_center(X)
        
    if standardize:
        X = standardization(X)
    
    return nipals_arr(X, PCs, threshold, E_matrices)     


def PCA_nipals_c(X, standardize=True, PCs=10, threshold=0.0001, E_matrices=False):
    """ USING C PYTHON EXTENSION """
    X = mean_center(X)
        
    if standardize:
        X = standardization(X)
    
    return nipals_c(X, PCs, threshold, E_matrices)      
    
    
    
################### Principal Component Analysis (using SVD) ###################
def PCA_svd(X, standardize=True):
    X = mean_center(X)
    #print X
        
    if standardize:
        X = standardization(X)    
        
    (rows, cols) = shape(X)
    
    # Singular Value Decomposition
    [U, S, V] = svd(X)
    
    # adjust if matrix shape does not match:
    if shape(S)[0] < shape(U)[0]: U = U[:, 0:shape(S)[0]]
    
    Scores = U * S # all Scores (T)
    Loadings = V # all Loadings (P)
    
    variances = S**2 / cols
    variances_sum = sum(variances)
    explained_var = variances / variances_sum
    
    return Scores, Loadings, explained_var



################### Correlation Loadings ###################
def CorrelationLoadings(X, Scores):
        """
        Returns the correlation loadings matrix based on Scores (T of PCA) 
        and X (original variables, not mean centered).
        """         
        # Creates empty matrix for correlation loadings
        PCs = shape(Scores)[1] # number of PCs
        rows = shape(X)[1] # number of objects (rows) in X
        CorrLoadings = zeros((PCs, rows), float)
        
        # Calculates correlation loadings with formula:
        # correlation = cov(x,y)/(std(x)*std(y))
        
        # For each PC in score matrix
        for i in range(PCs):
            Scores_PC_i = Scores[:, i] # Scores for PC[i]
            
            # For each variable/attribute in X 
            for row in range(rows):
                orig_vars = X[:, row] # column of variables in X
                corrs = corrcoef(Scores_PC_i, orig_vars)
                CorrLoadings[i, row] = corrs[0,1]
                
        return CorrLoadings        
