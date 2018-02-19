#!/usr/bin/env python
#This is the matrix data loader for Numeric

#from Numeric import *
from numpy import array, nan, zeros, shape
import string, re, sys, codecs, wx, os
from SensoryData import SensoryData
#from win32com.client import Dispatch
import mvt
import xlrd 

class DataFile:
    """
    Initializes variables and defines methods for use while loading the file. 
    Can open text files, error check and view dialogs.
    The class also contains return methods for interesting variables.
    """
#---Diverse methods:---#FFFFFF#FF8040--------------------------------------------
    def __init__(self, parent, name):
        """
        Looks up which codec to use and initializes variables.
        
        @type parent:     object
        @param parent:    self object from PanelCheck_GUI module.
        """
        self.parent = parent
        self.name = name # file path
        self.s_data = SensoryData(self.name)
        self.filename = self.split_path(self.name)[1] # file name
        self.fileRead = False # file read status
        self.text = [] # for lines from text file. Note: only used with the openTextFile function
        self.amountOfUnnameds = 0 # unnamed assessors/attributes/samples/replicates counter
        self.drop = False # for use in YES_NO dialogs if error occurs
        self.duplicate_keys = []
        
        self.inputValue = "" # value from input dialog
        self.inputValueSat = False # True if self.inputValue is sat
        
        # system encoding:
        self.encoding1 = sys.getfilesystemencoding()# can be:   'mbcs' win32
        self.encoding2 = sys.stdin.encoding         # can be:  	'cp850' win32 extended latin-1 type
        self.encoding3 = sys.getdefaultencoding()   # usually:  'ascii'
        
        self.codec = self.encoding1
        
        # setting encoder and decoder:
        try:
            self.enc, self.dec = codecs.lookup(self.encoding1)[:2] 
        except LookupError:
            self.enc, self.dec = codecs.lookup(self.encoding2)[:2]
            self.codec = self.encoding2
        except LookupError:
            self.enc, self.dec = codecs.lookup('latin-1')[:2]
            self.codec = 'latin-1'
        except LookupError:
            self.enc, self.dec = codecs.lookup('utf-8')[:2]
            self.codec = 'utf-8'
        except LookupError:
            self.enc, self.dec = codecs.lookup(self.encoding3)[:2] # most likely using 'ascii'
            self.codec = self.encoding3
        
        print "Encoder: " + str(self.enc)
        print "Decoder: " + str(self.dec)
        
        self.s_data.filename = self.filename
        self.s_data.codec = self.codec
        
        
        # The data is read into lists.
        # colValues creates lists that contain values from one row
        # for each column. Matrix conatains all colValues lists.
        self.AssessorList = []
        self.SampleList = []
        self.ReplicateList = []
        self.AttributeList = []
        self.ListCollection = []
        self.LabelList = []
    
    
    def show_msg(self, msg, _title):
	dlg = wx.MessageDialog(None, msg, _title,
	  	       wx.OK | wx.ICON_INFORMATION)
	dlg.ShowModal()
	dlg.Destroy()        
    
    def showErrorDialog(self, text):
        dlg = wx.MessageDialog(self.parent, text,'Error Message',wx.OK | wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_OK:
            pass
            #print text
        dlg.Destroy()
        
        
        
    def showErrorDialog_YES_NO(self, text):
        dlg = wx.MessageDialog(self.parent, text,'Error Message',wx.YES_NO | wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES:
            self.drop = True
        else:
            self.drop = False
        dlg.Destroy()
        
        
        
    def showInputDialog(self, text, sugg):
        dlg = wx.TextEntryDialog(self.parent, text,'Change Value?')
        dlg.SetValue(sugg)

        if dlg.ShowModal() == wx.ID_OK:
            self.inputValueSat = True
            self.inputValue = dlg.GetValue()
        dlg.Destroy()
        
        
            
    def safe_uni_dec(self, obj):
        """ 
        returns the decoded unicode representation of obj 
        """
        try:
            #uni = self.dec(obj)[0]
            #print "unicode type string: " + self.enc(uni)[0] # may return: UnicodeEncodeError
            #return uni
            return self.dec(obj)[0]
        except UnicodeDecodeError: # cannot handle characters with code table
            #print 'UnicodeDecodeError: trying with "replace"..'
            return unicode(obj, self.codec, 'replace')
        except UnicodeDecodeError: # cannot handle characters with code table
            #print 'UnicodeDecodeError: trying with "replace" and with sys.stdin.encoding'
            self.codec = self.encoding2
            return unicode(obj, self.codec, 'replace')
        except UnicodeDecodeError:
            #print 'UnicodeDecodeError: cannot decode'
            return str(obj)
        except UnicodeEncodeError:
            return self.enc(obj)[0]        
        except: 
            return obj.encode('ascii', 'ignore')
            
            
    def safe_uni_enc(self, obj):
        """ 
        returns the decoded unicode representation of obj 
        """
        try:
            # trying to encode (transform from "natural" into "artificial") with known encoding 'sys.getfilesystemencoding()'
            uni = self.enc(obj)[0]
            # returning decoded (to "natural" unicode representation)
            return self.dec(uni)[0]
        except UnicodeEncodeError: # cannot handle characters with code table
            #print 'UnicodeEncodeError: trying with "replace"..'
            uni = obj.encode(self.codec, 'replace')
            return unicode(uni, self.codec, 'replace')
        except UnicodeEncodeError: # cannot handle characters with code table
            #print 'UnicodeEncodeError: trying with "replace" and with sys.stdin.encoding'
            self.codec = self.encoding2
            uni = obj.encode(self.codec, 'replace')
            return unicode(uni, self.codec, 'replace')
        except UnicodeEncodeError:
            #print 'UnicodeEncodeError: cannot encode'
            return str(obj)
        except UnicodeDecodeError:
            return self.safe_uni_dec(obj)
    
    
    
    def split_path(self, abs_path):
        """
        Returns tuple with: (directory-path, filename, file_extension)
        """
        if os.name == 'nt': # windows (same on a 'ce' system?)
            match = re.search(r"(.*)\\(.*)\.(.*)", abs_path)
        else: # hopefully some unix system (not sure about how it looks on mac)
            match = re.search(r"(.*)/(.*)\.(.*)", abs_path)
        return match.groups() 
        # three items in a tuple: ('directory-path', 'filename', 'file-extension')    
    
    
    
    def openTextFile(self, name):
        """
        Opens and reads a text file. 
        Each line is read in as an element in the self.text list.
        
        name = full file path (unicode type)
        """
        
        # File is opened using name that is given by
        # the file-open dialog in the main file
        try:
            print "Opening file: " + name.encode(self.codec, 'replace')
            
            # self.name is allready a unicode type of wxString produced via the wxFileDialog 
            # we can only trust that it always works
            dataFile = open(name, 'r')
            
            # All the data is read into memory
            self.text = dataFile.readlines()
            dataFile.close()
            return True
        except:
            self.error = "Error reading file! Check for invalid characters in file path:\n" + name.encode(self.codec, 'replace')
            return False
        
        
        
#---Get-methods:---#FFFFFF#FF8040--------------------------------------------
    def MatrixData(self):
        """
        Creates and returns the loaded data in an array.
        col_start: column in listCollection where score values begin 
        """
        # Get dimensions/size of loaded data
        numRows = len(self.ListCollection)
        numCols = len(self.ListCollection[0])
        
        # Create new array with the size of the loaded data (from file)
        # containing zeros. 
        
        diff = 3 # amount of columns less in Matrix compared to listCollection
                 # 3 because of the three first non-score columns
        self.Matrix = zeros((numRows, numCols-diff), float)
        
        # Fill the array with the loaded data from Matrix
        for rows in range(0, numRows):
            for cols in range(diff, numCols):
                self.Matrix[rows][cols-diff] = float(self.ListCollection[rows][cols])
        
        return self.Matrix

            
    
    def get_MAX_MIN_Values(self):
        """
        Returns a list of maximum and minimum values for x and y scale.
        [x_min, x_max, y_min, y_max]
        """
        self.min_max_values = [-1,1,-1,1] # values will be overwritten
        self.min_max_values[2] = float(self.s_data.SparseMatrix[(self.AssessorList[0],self.SampleList[0],self.ReplicateList[0])][0])
        self.min_max_values[3] = float(self.s_data.SparseMatrix[(self.AssessorList[0],self.SampleList[0],self.ReplicateList[0])][0])
        
        for ass in self.AssessorList:
            for samp in self.SampleList:
                for rep in self.ReplicateList:
                    values = self.s_data.SparseMatrix[(ass, samp, rep)]
                    for value in values:
                        if self.min_max_values[2] > float(value):
                            self.min_max_values[2] = float(value) #new y_min value
                        if self.min_max_values[3] < float(value):
                            self.min_max_values[3] = float(value) #new y_max value
        self.min_max_values[0] = 0 #x_min
        self.min_max_values[1] = len(self.AttributeList) + 1 #x_max
        return self.min_max_values
        
    
    
    
    def get_matrix_column(self, matrix, columnNumber):
        """
        Returns column as a list.
        """
        column = []
        numRows = len(matrix)
        for i in range(0, numRows):
            column.append(matrix[i][columnNumber])
        return column
    
        
    
#---Error checking methods:---#FFFFFF#FF8040--------------------------------------------
    
    def isNumeric(self, str_value, prog):
	if prog.match(str_value):
	    return True
	else:
	    return False

    def isFloat(self, value):
        """
        Returns true if value can be parsed into double/integer type
        """
        if isinstance(value, (int, float)): return True
        else:
            try:
                float(value)
                return True
            except:
                return False
        
        
    
    def isEmpty(self, value):
        """
        Returns true if value is None or equals: ''
        """
        if value == None or value == '':
            return True
        else:
            return False
        
        
    def isAcceptable(self, value):
        """
        Tests if the variable is acceptable as score-/numbering-/name-value.
        Returns true if value is acceptable, false if not.
        """
        if self.isEmpty(value):
            return False
        
        # testing some single characters:
        if value == '\t' or value == '\n' or value == ' ':
            return False
        return True
    
    
    
    def get_real_UsedRange_text(self, lines, delimiter='\t'):
        """
        Works on list.
        """
        print 'so far so good'
        numRows = len(lines)
        print numRows
        
        newNumRows = 0
        print 'sec 2'        
        # testing vertical used range
        for i in range(0, numRows):
            firstValue = lines[i].split(delimiter)[0]
            if self.isAcceptable(firstValue):
                newNumRows += 1
            else:
                break
        print 'sec 3'        
        #print newNumCols, newNumRows
        
        if newNumRows < numRows:
            # creating new datasheet containing the real used-range
            new_lines = []
            print 'sec 4'
            for i in range(0, newNumRows):
                new_lines.append(lines[i])
                
            return new_lines
        else:
            print 'sec 5'
            return lines    
            print 'sec 6'
        print 'Done'
        
        
    def get_real_UsedRange_matrix(self, datasheet):
        """
        Works on list of lists.
        Inspects the [M*N] datasheet.
        Tests: [(0,0),(1,0),(2,0), ... ,(N-1,0)]  and  [(0,0),(0,1),(0,2), ... , (0,M-1)]
        
        Returns a [(M-m) * (N-n)] datasheet.
        """
        print 'hi'
        numCols = len(datasheet[0])
        numRows = len(datasheet)
        print numCols, numRows
        
        newNumCols = 0
        newNumRows = 0
        
        # testing horizontal used range
        for row in datasheet[0]:
            if self.isAcceptable(row):
                newNumCols += 1
            else:
                break
                
        # testing vertical used range
        for i in range(0, numRows):
            if self.isAcceptable(datasheet[i][0]):
                newNumRows += 1
            else:
                break
                
        print newNumCols, newNumRows
        
        if newNumRows < numRows or newNumCols < numCols:
            # creating new datasheet containing the real used-range
            new_datasheet = []
            for i in range(0, newNumRows):
                new_datasheet.append(datasheet[i][0:newNumCols])
                
            return new_datasheet
        else:
            return datasheet

    
    def values_array(self, datasheet, positions):
        """
        returns 2d numpy array with numpy.nan for missing values (if any)
        """
        
        m_data = zeros((len(datasheet), len(datasheet[0])), float)
        
        for pos in positions:
            m_data[pos[0], pos[1]] = nan
        
	for i in range(len(datasheet)):
            for j in range(3, len(datasheet[0])):
                if m_data[i, j] == 0:
                    m_data[i, j] = float(datasheet[i][j])
        
        return m_data


    def only_mv_in_att_vector(self, vec):
        for x in vec:
            #print x
            if str(x) != '-1.#IND': 
               return False
        return True


    def too_many_mv_in_matrix(self, mx):
        (rows, cols) = shape(mx)
        for col_ind in range(cols):
            if self.only_mv_in_att_vector(mx[:,col_ind]): 
                return True
            #print mx[:,col_ind]
        return False 
    
    
    def missing_values_analysis(self, datasheet, ass_index = 0, samp_index = 1, rep_index = 2):
        """
        Searches for NaN values where there should be a number, meaning missing value.
        Gathers the positions (i, j) in list that is returned
        """
        #real_in = r'\d+'
        #real_dn = r'(\d+\.\d*|\d*\.\d+)'
        #real_sn = r'(\d\.?\d*[Ee][+\-]?\d+)'
        #real = '-?(' + real_sn + '|' + real_dn + '|' + real_in + ')'

        #prog = re.compile(real)
        positions = []
        row_missing = []

        for i in range(len(datasheet)):
            complete_row_missing = True
            for j in range(3, len(datasheet[0])):
                #if not self.isNumeric(datasheet[i][j], prog):
                if not self.isFloat(datasheet[i][j]):
                    positions.append([i, j])
                    datasheet[i][j] = "NaN"
                else:
                    complete_row_missing = False
            if complete_row_missing:
                row_missing.append([i, datasheet[i][ass_index], datasheet[i][samp_index], datasheet[i][rep_index]])

        return positions, row_missing
        


    def missing_values_analysis_assessors(self):
        """
        Missing values/unacceptable values are imputed
        
        
        @return: (dict, dict)
        """
	cols = len(self.AttributeList)
	rows = len(self.SampleList) * len(self.ReplicateList)
	
	mvt_dict = {}
	mv_ass_info = {}
	
	
	for ass in self.AssessorList:
	    
	    ass_mat = zeros((rows, cols), float)

	    row_ind = 0; num_missing = 0  
	    for samp in self.SampleList:
	        for rep in self.ReplicateList:
	            key = (ass, samp, rep)
	            att_vec = self.s_data.SparseMatrix[key]
	            ass_row = zeros((cols), float)
	            
	            nan_list = []
	            for i in range(len(att_vec)):
	                if att_vec[i] == "NaN":
	                    ass_row[i] = nan
	                    nan_list.append(i)
	                else:
	                    #print att_vec[i]
	                    ass_row[i] = float(att_vec[i])
	            
	            if len(nan_list) > 0:
	                mvt_dict[key] = nan_list
	                num_missing += len(nan_list)
	            
	            ass_mat[row_ind] = ass_row 
	            
	            row_ind += 1
	    
	    if self.too_many_mv_in_matrix(ass_mat): return None, None
	    
	    
	    # mv_ass_info[ass] = mvt.MVA(ass_mat)
	    mv_ass_info[ass] = float(num_missing) / float(rows * cols)
	    if mv_ass_info[ass] > 0:
	        self.s_data.has_mv = True
	    ass_mat = mvt.IMP(ass_mat) # impute new values for NaN values 
            
            
            row_ind = 0
	    for samp in self.SampleList:
	        for rep in self.ReplicateList:
	            key = (ass, samp, rep)
	            self.s_data.SparseMatrix[key] = ass_mat[row_ind]
	            
	            row_ind += 1
	            
	            

                
        return mvt_dict, mv_ass_info
     

    def unbalanced_data_analysis(self, datasheet, ass_index = 0, samp_index = 1, rep_index = 2):
        """
        Searches that all assessors exists for all samples, and vice versa.
        A samples goes as missing if a single replicate is missing.
        
        Returns two lists: missing_assessors, missing_samples
        
        1. get list of assessors and list of samples
        2. get existing samples for each assessor
        3. find assessomissing samplesrs with 
        """
        
        assessors = [] # list of all assessors
        samples = [] # list of all samples
        replicates = [] # list of all replicates
        
        # get list of assessors and list of samples:
        for row in datasheet:
            ass = row[ass_index]        
            samp = row[samp_index]
            rep = row[rep_index]
            if ass not in assessors: assessors.append(ass)
            if samp not in samples: samples.append(samp)
            if rep not in replicates: replicates.append(rep)
        
        # get existing samples for each assessor:
        existing_samples = {}
        existing_replicates = {}
        for ass in assessors: 
            existing_samples[ass] = []
            for samp in samples:
                existing_replicates[(ass, samp)] = []            
        for row in datasheet:
            ass = row[ass_index]        
	    samp = row[samp_index]
	    rep = row[rep_index]
            if samp not in existing_samples[ass]: existing_samples[ass].append(samp)
            existing_replicates[(ass, samp)].append(rep)
        #print existing_samples
        
        
        missing_assessors = [] # list of assessors that are missing one or more samples
        missing_samples = [] # list of samples that are missing one or more assessors
        missing_replicates = {} # dictionary with key: (assessor, sample) for the missing replicate
        
        # find assessors with missing samples and (assessor, sample) couples with missing replicate:
        for ass in assessors:
            if not len(existing_samples[ass]) == len(samples):
                if ass not in missing_assessors: missing_assessors.append(ass)
                # get missing samples:
                for samp in samples:
                    if samp not in existing_samples[ass] and samp not in missing_samples:
                        missing_samples.append(samp)
            for samp in samples:
                if not len(existing_replicates[(ass, samp)]) == len(replicates):
                    for rep in replicates:
                        if rep != existing_replicates[(ass, samp)]:
                            missing_replicates[(ass, samp)] = rep
        
        # if missing replicate: corresponding assessor or sample will be removed
        for key in missing_replicates.iterkeys():
            if key[0] not in missing_assessors:
                missing_assessors.append(key[0])
            if key[1] not in missing_samples:
                missing_samples.append(key[1])
        
        #print "unbalanced data analysis results:"
        #print missing_assessors, missing_samples, missing_replicates
        missing_assessors.sort(); missing_samples.sort()
        return missing_assessors, missing_samples, missing_replicates



    def balanceData_remove_assessors(self, datasheet, missing_assessors, ass_index = 0):
        """
        returns balanced data
        """
        # if missing replicate: corresponding assessor will be removed
        #missing_ass = missing_assessors[:]
        #for key in missing_replicates.iterkeys():
        #    if key[0] not in missing_ass:
        #        missing_ass.append(key[0])
            
        new_datasheet = []
        for row in datasheet:
            ass = row[ass_index]
            if ass not in missing_assessors:
                new_datasheet.append(row) # else: row not to be added
        return new_datasheet            


            
    def balanceData_remove_samples(self, datasheet, missing_samples, samp_index = 1):
        """
        returns balanced data
        """
        
        # if missing replicate: corresponding assessor will be removed
        #missing_samp = missing_samples[:]
        #for key in missing_replicates.iterkeys():
        #    if key[1] not in missing_samp:
        #        missing_samp.append(key[1])

        new_datasheet = []
        for row in datasheet:
            samp = row[samp_index]
            if samp not in missing_samples:
                new_datasheet.append(row) # else: row not to be added
        return new_datasheet

    

    def is_standard_file(self, firstRow): 
        """
        Returns true if file is acceptable.
        
        A very incomplete check, but now controls if first row is acceptable.
        One check could of course be file id in the first bytes for example.
        More can be added later.   
        """
        # acceptable length?
        if len(firstRow) < 3:
            self.error = "Not standard file! Cannot load file:\n" + self.name.encode(self.codec, 'replace')
            self.showErrorDialog(self.error)
            return False
        
        # only numbers? iterates firstRow[0] to firstRow[-2], because the last (firstRow[-1]) will contain "\n"
        all_are_numbers = True
        for i in range(0, len(firstRow)):
            try:
                float(firstRow[i])
            except:
                all_are_numbers = False
                break
            
        if all_are_numbers:
            self.error = "Unusal standard file or Not standard file! All " + str(len(firstRow)) + " header values are numbers, check file:"
            self.error += "\n" + self.name.encode(self.codec, 'replace')
            self.error += "\nDo you wish to stop the loading process?"
            dlg = wx.MessageDialog(self.parent, self.error,'Error Message',wx.YES_NO | wx.ICON_ERROR)
            if dlg.ShowModal() == wx.ID_YES:
                dlg.Destroy()
                return False
            dlg.Destroy()
            
        return True
                            
        


    def only_filled_lists(self, lists):
        """
        Returns false if any of the standard lists are empty.
        
        lists[0] - self.AssessorList
        lists[1] - self.SampleList
        lists[2] - self.ReplicateList
        lists[3] - self.AttributeList  
        """
        if len(lists[0]) == 0:
            return False
        if len(lists[1]) == 0:
            return False
        if len(lists[2]) == 0:
            return False
        if len(lists[3]) == 0:
            return False
        return True # each list length > 0
    
    
    
    def find_equal_names(self, list, pos, skipList):
        """
        Returns a list of positons of where there are equal elements between 
        elements in "list" and "list[pos]" ("pos" will not be added to list)
        """
        comp = list[pos]
        list_of_equals = []
        for i in range(pos, len(list)):
            if comp == list[i]:
                if i != pos:
                    if list[i] not in skipList:    
                        list_of_equals.append(i)
            i += 1
        #print "List of equals: "
        #print list_of_equals
        return list_of_equals
    
    
    def equal_columns(self, column1, column2):
        """
        Returns true if columns are equal. Expects equal length of column1 and column2. 
        """
        numCols = len(column1)    
        for row in range(0, numCols):
            if column1[row] != column2[row]: 
                return False
        return True
        
        

    def find_equal_columns(self, matrix, attributes):
        """
        Uses other error-check methods.
        Show dialogs windows for different situations.
        
            
        attributes = self.AttributeList
        matrix = self.ListCollection (Note: first columns should contain non-score values)
        
        1. Iterate Attributes list
        2. Search for equal names in attribute list.
        3. If equal names found, compare two by two columns.
        4. If columns are equal, automatic deletion of column (can question user for deletion) 
        5. If columns are not equal inform about equal attribute names.
        
        """
        #print attributes
        #print matrix
        
        i = 0
        can_skip = [] # list of elements that can be skipped
        for attr in attributes: # iterating attribute list
            list_of_equals = self.find_equal_names(attributes, i, can_skip)
            if len(list_of_equals) > 0:
                j = 0
                for value in list_of_equals: # value contains the index position of the Attribute equal to Attribute in attributes[i]
                    if self.equal_columns(self.get_matrix_column(matrix, i+3), self.get_matrix_column(matrix, value+3)): # must add with 3 because of the three first non-score columns
                        # two equal columns found!
                        self.error = "Column number " + str(i+4) + " and number " + str(int(value)+4) + " are equal!"
                        self.error += "\nDo you wish to drop column number " + str(value+4) + " in this data analysis?"
                        self.showErrorDialog_YES_NO(self.error)
                        if self.drop:
                            self.del_column(value+3) # del from self.ListCollection and self.SparseMatrixSparseMatrix
                            self.del_from_sparseMatrix(value)
                            adjust = False
                            # adjusting list of equals, because matrix = self.ListCollection
                            for k in range(0, len(list_of_equals)):
                                if adjust:
                                    list_of_equals[k] = list_of_equals[k] - 1
                                if value == list_of_equals[k]:
                                    adjust = True
                    if not self.drop:
                        self.error = "Attributes with equal names: Both are named \""+ attr +"\"\nDo you want to change attribute name for score-column " + str(int(value)+4) + " in this data analysis?"
                        self.error += "\n(Note: No change might produce faulty score-values for this column in plots!)"
                        self.showInputDialog(self.error, attr + str(j+2))
                        if self.inputValueSat:
                            self.AttributeList[value] = self.inputValue
                            #attributes[value] = self.inputValue
                            self.inputValueSat = False
                        j += 1
                    else:
                        del self.AttributeList[value]
                    self.drop = False # delete column? reset
                can_skip.append(attr) # add name to skip list
            i += 1
            #list_of_equals = []
            #print attributes
            
            
            
    def matrix_has_unacceptable(self, matrix):
        """
        Returns true if matrix has a None value.
        If True: Critical error. Sets self.error with position of None.
        """
        rowNum = 0 # first row has been removed. that is why 2 is added to rowNum in message.
        for i in range(0, len(matrix)):
            if self.row_has_unacceptable(matrix[i], rowNum):
                return True
            #pos = self.row_has_null(row)
            #if (pos > -1):
                #self.error = "Value at row:" + str(rowNum+2) + " column:" + str(pos+1) + " is empty!"
                #return True
            rowNum += 1
        return False
            
            
            
    def row_has_unacceptable(self, row, rowNum):
        """
        Returns position of None value if row has a None value. Or returns -1.
        
        """
##        for i in range (0, len(row)):
##            if row[i] == None:
##                return i
##        return -1
        max = len(row)
        deleted = False
        for i in range (0, max):
            # No values can be Empty
            if deleted:
                i -= 1
                deleted = False
            if self.isEmpty(row[i]):
                if i < 3:
                    return True
                #self.error = "Value at row:" + str(rowNum+2) + " column:" + str(i+1) + " is empty!"
                #self.error += "\nDo you wish to continue and drop column in this data analysis?"
                #self.showErrorDialog_YES_NO(self.error)
                else:#if self.drop:
                    print "Deleting column! Empty value at row-number:" + str(rowNum+1) + " column-number:" + str(i+1)
                    self.del_column(i) # position [i-3] points to correct position in SparseMatrix
                    self.del_from_sparseMatrix(i-3)
                    del self.AttributeList[i-3]
                    max -= 1
                    deleted = True
                self.drop = False
            else:
                if i >= 3:
                    # No score values can be other than float
                    if not self.isFloat(row[i]):
                        #self.error = "Score-value at row:" + str(rowNum+2) + " column:" + str(i+1) + " cannot be converted to float!"
                        #self.error += "\nDo you wish to continue and drop column in this data analysis?"
                        #self.showErrorDialog_YES_NO(self.error)
                        if True:#self.drop:
                            print "Deleting column! Not digit score-value at row-number:" + str(rowNum+1) + " column-number:" + str(i+1)
                            self.del_column(i) # position [i-3] points to correct position in SparseMatrix
                            self.del_from_sparseMatrix(i-3)
                            del self.AttributeList[i-3]
                            max -= 1
                            deleted = True
                        else:
                            return True
                        self.drop = False
            
        return False
        


    def null_column(self, column):
        """
        Returns a list of the positions of the None values.
        """
        list_zeros = [] # positons of None values
        for i in range (0, len(column)):
            if colum[i] == None:
                list_zeros.append(i)
        return list_zeros
    
    
    
    def column_has_null(self, column):
        """
        Returns true if column has a None value.
        """
        for i in range (0, len(column)):
            if colum[i] == None:
                return True
        return False
    
    
    
    def del_column(self, colNum):
        """
        Deletes a column in self.ListCollection given by colNum. 
        """
        # deleting column
        for list in self.ListCollection:
            del list[colNum]
        
        
        
    def del_from_sparseMatrix(self, colNum):
        """
        Removes values from self.SparseMatrixsparseMatrix
        """
        # deleting values
        for ass in self.AssessorList:
            for samp in self.SampleList:
                for rep in self.ReplicateList:
                    key = (ass, samp, rep)
                    del self.s_data.SparseMatrix[key][colNum]
                    
                    
                    
    def convert_to_ndarray(self):
        """
        Converts all lists in self.s_data.SparseMatrix to numpy arrays
        """
        for ass in self.AssessorList:
            for samp in self.SampleList:
                for rep in self.ReplicateList:
                    key = (ass, samp, rep)
                    try:
                        self.s_data.SparseMatrix[key] = array(self.s_data.SparseMatrix[key])
                    except KeyError:
                        err_msg = "Error with row identifier. Probably incorret value for assessor, sample or replicate.\n"
                        err_msg += "Missing key: (" + ass + ", " + samp + ", " + rep + ")"
                        self.showErrorDialog(err_msg)
                        return False
                    except:
                        err_msg = "Error setting row data. For key: (" + ass + ", " + samp + ", " + rep + ")"
                        self.showErrorDialog(err_msg)                         
                        return False
        return True
                        
    
    
    def load_data(self, datasheet, firstRow, encode_text=False):
        """
        File loading for general files
        """


        # missing values analysis:
        missing_values_positions, rows_missing = self.missing_values_analysis(datasheet)
        print rows_missing
        self.summaryFrame.grid.set_color_on_pos(missing_values_positions)

        #m_data = self.values_array(datasheet, missing_values_positions)


        if len(missing_values_positions) > 0:
               if len(rows_missing) > 0:
                   self.show_msg("Data set has " + str(len(missing_values_positions)) + " missing values.\nThere are rows that consist of missing values only.\nDataset will be considered unbalanced.", "Warning!")
               else:
                   self.show_msg("Data set has " + str(len(missing_values_positions)) + " missing values.\nNew values will be imputed for the missing values.", "Warning!")
               #m_data = mvt.IMP(m_data) # impute new values for NaN values 


        if self.summaryFrame.ShowModal() == 1:

            # column indexing:
            ass_index = self.summaryFrame.ass_index
            samp_index = self.summaryFrame.samp_index
            rep_index = self.summaryFrame.rep_index
            out_columns = self.summaryFrame.out_columns
            #print value_index                          
        else:
            self.summaryFrame.Destroy()
            self.fileRead = False
            return False


        self.summaryFrame.switch_to_progress()
        self.summaryFrame.Show()                 
        self.summaryFrame.append_text("\nChecking for unbalanced data...\n")
        missing_ass, missing_samp, missing_rep = self.unbalanced_data_analysis(datasheet, ass_index, samp_index, rep_index)               
        for row_missing in rows_missing:
            if row_missing[1] not in missing_ass: missing_ass.append(row_missing[1])
            if row_missing[2] not in missing_samp: missing_samp.append(row_missing[2])

        if len(missing_ass) > 0: # unbalanced data
            self.summaryFrame.append_text("Data set unbalanced!\n")
            str_ass = "("; str_samp = "("

            if encode_text:
                for ass in missing_ass: str_ass += self.norm_str_enc(ass) + ", "
                for samp in missing_samp: str_samp += self.norm_str_enc(samp) + ", "	    
            else:
                for ass in missing_ass: str_ass += self.safe_uni_dec(ass) + ", "
                for samp in missing_samp: str_samp += self.safe_uni_dec(samp) + ", "

            str_ass = str_ass[:-2] + ")"; str_samp = str_samp[:-2] + ")"   


            self.unbalanced_data = Unbalanced_Data(self.parent, missing_ass, missing_samp, str_ass, str_samp)
            if self.unbalanced_data.ShowModal() == 1:                   
                if self.unbalanced_data.radio1_selection:
                    datasheet = self.balanceData_remove_assessors(datasheet, missing_ass, ass_index)
                    info_str = "Unbalanced data set:\n"
                    info_str += "=================\n\n"
                    info_str += "Removed assessors: " + str_ass + "\n\n\n\n"
                    self.summaryFrame.append_text_summary(info_str)
                    self.summaryFrame.str_ind = len(info_str)
                elif self.unbalanced_data.radio2_selection:
                    datasheet = self.balanceData_remove_samples(datasheet, missing_samp, samp_index)
                    info_str = "Unbalanced data set:\n"
                    info_str += "=================\n\n"
                    info_str += "Removed assessors: " + str_samp + "\n\n\n\n"
                    self.summaryFrame.append_text_summary(info_str)
                    self.summaryFrame.str_ind = len(info_str)
                    
        else: # balanced data
            self.summaryFrame.append_text("Data set is balanced.\n")


        if encode_text:
            for items in range(len(firstRow)):
                firstRow[items] = self.safe_uni_enc(firstRow[items])	
        else:
            for items in range(len(firstRow)):
                firstRow[items] = self.safe_uni_dec(firstRow[items])



        # Copy attributes into a seperate list. The first 3 strings
        # are 'assessor', 'sample' and 'replicate' and are therefore
        # left out
        assessorExpression = firstRow[ass_index]
        sampleExpression = firstRow[samp_index]
        replicateExpression = firstRow[rep_index]


        self.LabelList = firstRow[:]
        self.AttributeList = []
        for i in range(len(firstRow)):
            if i not in out_columns and i != ass_index and i != samp_index and i != rep_index:
                self.AttributeList.append(firstRow[i])
        if self.AttributeList[-1][-1:] == '\n':
            self.AttributeList[-1] = self.AttributeList[-1][:-1]


        self.summaryFrame.set_gauge(40) # approx/guess 20% finished



        # Process the rest of the data (numerical data) in text

        for row_ind in range(len(datasheet)):

            row = datasheet[row_ind]

            # In case of len(row) <= 3, there is error in input data 
            if len(row) > 3:

                    if encode_text:
                        if type(row[ass_index]) == int:
                            newAssessor = assessorExpression + ' ' + str(row[ass_index])
                        elif type(row[ass_index]) == float:
                            newAssessor = assessorExpression + ' ' + str(int(row[ass_index]))
                        else:
                            newAssessor = self.safe_uni_enc(row[ass_index])

                        if type(row[samp_index]) == int:
                            newSample = sampleExpression + ' ' + str(row[samp_index])
                        elif type(row[samp_index]) == float:
                            newSample = sampleExpression + ' ' + str(int(row[samp_index]))
                        else:
                            newSample = self.safe_uni_enc(row[samp_index])

                        if type(row[rep_index]) == int:
                            newReplicate = replicateExpression + ' ' + str(row[rep_index])
                        elif type(row[rep_index]) == float:
                            newReplicate = replicateExpression + ' ' + str(int(row[rep_index]))
                        else:
                            newReplicate = self.safe_uni_enc(row[rep_index])

                    else:
                        if self.isFloat(row[ass_index]):
                            newAssessor = assessorExpression + ' ' + str(row[ass_index])
                        else:
                            newAssessor = self.safe_uni_dec(row[ass_index])

                        if self.isFloat(row[samp_index]):
                            newSample = sampleExpression + ' ' + str(row[samp_index])
                        else:
                            newSample = self.safe_uni_dec(row[samp_index])

                        if self.isFloat(row[rep_index]):
                            newReplicate = replicateExpression + ' ' + str(row[rep_index])
                        else:
                            newReplicate = self.safe_uni_dec(row[rep_index])



                    if newAssessor not in self.AssessorList:
                        self.AssessorList.append(newAssessor)
                    if newSample not in self.SampleList:
                        self.SampleList.append(newSample)
                    if newReplicate not in self.ReplicateList:
                        self.ReplicateList.append(newReplicate)




                    #for i in range(len(row)):
                    #    row[i] = re.sub(',', '.', row[i])


                    row_collection = []
                    for i in range(len(row)):
                        if i not in out_columns: row_collection.append(row[i])
                    self.ListCollection.append(row_collection)


                    #row_collection = []
                    #for i in range(len(m_data[row_ind])):
                    #    if i not in out_columns:
                    #	row_collection.append(m_data[row_ind, i])
                    #self.ListCollection.append(row_collection)

                    floatList = []
                    for i in range(len(row)):
                        if i not in out_columns and i != ass_index and i != samp_index and i != rep_index: floatList.append(row[i])
                    #try:
                    #    floatList = map(float, floatList)
                    #except (ValueError, TypeError):
                    #    self.showErrorDialog("Possibly missing data! Cannot proceed loading.")
                    #    self.fileRead = False; return


                    if self.s_data.SparseMatrix.has_key((newAssessor,newSample,newReplicate)): 
                        self.duplicate_keys.append((newAssessor,newSample,newReplicate))
                    self.s_data.SparseMatrix[(newAssessor,newSample,newReplicate)] = floatList
                    
            else:
                self.summaryFrame.append_text("\nError: Too few column values on line\n")

            colValues = []



        if len(self.duplicate_keys) > 0:         
            str_list = ""
            for k in self.duplicate_keys: str_list += k[0] + ", " + k[1] + ", " + k[2] + "\n"

            self.showErrorDialog("Cannot proceed loading. The following assessor-sample-replicate\n" \
                               + "combinations are used for more than one score row:\n" + str_list + "\nPlease check your data set.")
            self.summaryFrame.Destroy()
            self.fileRead = False
            return False             
        
        
        # error checking:
        #if self.matrix_has_unacceptable(self.ListCollection):
            # Unaccpetable value, stopping load
            #self.fileRead = False
            #return False                



	    self.find_equal_columns(self.ListCollection, self.AttributeList)

        
        
        # Imputes missing values and converts attribute vectors to numpy arrays
        mv_dict, mv_inf = self.missing_values_analysis_assessors()
        
        if mv_dict == None:
            self.showErrorDialog("Cannot proceed loading: \nAn attribute column consists of only missing values.")
            self.summaryFrame.Destroy()
            self.fileRead = False
            return False            

        # file loading did not fail
        # update sensory data
        self.s_data.AssessorList = self.AssessorList
        self.s_data.SampleList = self.SampleList
        self.s_data.ReplicateList = self.ReplicateList
        self.s_data.AttributeList = self.AttributeList
        self.s_data.ListCollection = self.ListCollection
        self.s_data.LabelList = self.LabelList
        self.s_data.mv_pos = mv_dict
        self.s_data.mv_inf = mv_inf

        #if not self.convert_to_ndarray():
        #    self.fileRead = False
        #    return False

        #if len(missing_values_positions) > 0:
        #    rows, cols = m_data.shape
        #    percent_missing = 100.0 * (len(missing_values_positions)/float(rows*cols))
        #    formatted_str = "%.2f" % (percent_missing)
        #    self.mv_msg = formatted_str + "% missing values (new values have been imputed)\n=================\n"
        #else: self.mv_msg = "No missing values\n=================\n"
        self.mv_msg = ""


        # update gui
        self.summaryFrame.Update()
        self.summaryFrame.set_gauge(100) # reading of file finished 100%
        self.fileRead = True

        return True
        
        
        
    def norm_str_enc(self, obj):
        if type(obj) == int:
            new = str(obj)
        elif type(obj) == float:
            new = str(int(obj))
        else:
            new = self.safe_uni_enc(obj)
        return new       
        
        
    def norm_str_dec(self, obj):
        if type(obj) == int:
            new = str(obj)
        elif type(obj) == float:
            new = str(int(obj))
        else:
            new = self.safe_uni_dec(obj)
        return new       
        
        

class PlainText(DataFile):
    def __init__(self, parent, name, summaryFrame, delimiter):
        """
        The class 'PlainText' reads the sensory data into an Numeric array
        from a "plain" text file. All values should be tab-separated (\t).
        This class will function as an extended DataFile class.
        
        First row: strings describing what columns contain.
        First column: indicator - assessor numbers.
        Second column: indicator - sample numbers.
        Third column: indicator - replicate numbers.
        All following columns: assessor score values.
        
        @version: 1.3
        @since: 07.03.2005
        
        @status:    
                    - reads attributes into attribute list (first row in text file)
                    - handles Unicode for attribute list (norwegian characters are possible now)
                    - reads score values into an array/matrix
                    - creates a sparse matrix where data is accessible through key words
        
        @todo: nothing I can think of right now
        
        @author: Oliver Tomic, Henning Risvik
        @organization: Matforsk - Norwegian Food Research Institute
        
        @type name:     string
        @param name:    Absolute file-path of the data file to be read.
        
        @type parent:     object
        @param parent:    self object from PanelCheck_GUI module.
        
        Short overview:
        ------------------------------------------------------------
        1. Initializing, inheriting from DataFile class.
        2. Tries to open file for reading. Reads file as a list of strings.
        3. Tries to order first row (name-tags, complete self.AttributeList), if fail: stop loading.
        4. Iterates the rest of the lines.
        5. Splits a line into values, for assessor, sample, replicate and scores.
        6. Fills lists with the different elements, self.AssessorList, self.SampleList, self.ReplicateList (all for "name-tags").
        7. self.ListCollection is filled with all values, the three first columns will contain non-score values (name-tags) the rest do.
        8. self.SparseMatrix is filled with score values.
        9. self.ListCollection is checked for None values, if found: 
                User can remove column with None value(s) or stop process.
        10. self.AttributeList is checked for equal values, if found: 
                Check for double column, if found: 
                    User can remove column, if user chooses not to remove:
                        User can change name of attribute.
                No double column:
                    User can change name of attribute
        11. Sets self.fileRead to True, if load completed, or False, if load failed.
        ------------------------------------------------------------
        """
        
        DataFile.__init__(self, parent, name)
        self.name = name
        self.summaryFrame = summaryFrame
        self.parent = parent
        
        
        # File is opened using name that is given by
        # the file-open dialog in the main file
        if self.openTextFile(self.name):
            
  
            try:
                print 'yes'
                self.text = self.get_real_UsedRange_text(self.text, delimiter) #self.text is an Array
                print 'okay'

            # Catch the first line from the file and extract
            # the attributes.
            # The .decode-part is necessary such that the norwegian/other foreign
            # characters can be read
            except:
                self.error = "Not standard file! Cannot load file:\n " + self.name.encode(self.codec, 'replace')
                self.showErrorDialog(self.error)
                self.fileRead = False
                return # not standard file: stopping process
            
            firstRow = self.text[0].split(delimiter)
            
            if self.is_standard_file(firstRow):
                datasheet = []
		for line in self.text:
		    datasheet.append(line.split(delimiter))            
                self.summaryFrame.set_grid(datasheet)
                
            

                del datasheet[0] # remove header row
   
		for row in datasheet:
		    for i in range(3, len(row)):
		        row[i] = re.sub(',', '.', row[i])                
                
                if not self.load_data(datasheet, firstRow):
                   return 
                
                
            else:
                #self.error = "Not standard file! Cannot load file:\n" + name.encode(self.codec, 'replace')
                #self.showErrorDialog(self.error)
                self.fileRead = False
                return
        else: # cannot open file
            self.showErrorDialog(self.error)
            self.fileRead = False
            
    
        
class Excel(DataFile):
    def __init__(self, parent, name, summaryFrame):
        """
        This class reads the sensory data into an Numeric array from a win32 
        Excel (*.xls) file. This class will function as an extended DataFile class.
        
        First row: strings describing what columns contain.
        First column (A): indicator - assessors.
        Second column (B): indicator - samples.
        Third column (C): indicator - replicates.
        All following columns (D, ...): assessor score values.
        
        
        @version: 1.0
        @since: 07.08.2005
        
        @author: Henning Risvik
        @organization: Matforsk - Norwegian Food Research Institute
        
        @type name:     string
        @param name:    Absolute file-path of the data file to be read.
        """
        DataFile.__init__(self, parent, name)
        self.name = name
        self.summaryFrame = summaryFrame
        self.parent = parent
        
        self.summaryFrame.append_text("\nUsing codec: " + self.codec + "\n")
        # Following dictionaries/lists initialized:
        # self.AssessorList = []
        # self.SampleList = []
        # self.ReplicateList = []
        # self.ListCollection = []
        # self.AttributeList = []
        # self.SparseMatrix = {}
        
        self.summaryFrame.set_gauge(0) # starting 0%
        self.summaryFrame.Update()
        
        '''
        try:
            #from win32com.client import Dispatch
            excelApp = Dispatch("Excel.Application")
            #excelApp.Visible = -1
            self.summaryFrame.append_text("\nUsing Excel Application...\n")
            workBook = excelApp.Workbooks.Open(self.name)
            sheet = workBook.ActiveSheet

            datasheet_tup = sheet.UsedRange.Value #Tuple of Tuple: 2d matrix containing values
            datasheet_tup = self.get_real_UsedRange_matrix(datasheet_tup) #datasheet is a 2dArray
        '''
        try:
            book = xlrd.open_workbook(name)
            first_sheet = book.sheet_by_index(0)

            firstRow = []

            if first_sheet.nrows > 0:
                datasheet = []
                for i in range(0, first_sheet.nrows):
                    datasheet.append(first_sheet.row_values(i))       
                # extracting first row:
                firstRow = datasheet[0]

                if self.is_standard_file(firstRow):
                    print datasheet
                    self.summaryFrame.set_grid(datasheet)
                    del datasheet[0] # remove header row

                    if not self.load_data(datasheet, firstRow, encode_text=True):              
                       return 
            else:
                self.fileRead = False

            # Closing Excel and Excel-file
            self.summaryFrame.Update()
            #print self.SparseMatrix
        
        except:
            self.summaryFrame.append_text("\nCannot open file because Microsoft Excel is not installed.\n")
            dlg = wx.MessageDialog(parent, 'Cannot open file. Check that the data has correct structure and that Microsoft Excel is installed.','Information', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
    '''
 
    # print number of sheets
        print book.nsheets
 
    # print sheet names
        print book.sheet_names()
 
    # get the first worksheet
        
 
    # read a row
        print first_sheet.row_values(0)
 
    # read a cell
        cell = first_sheet.cell(0,0)
        print cell
        print cell.value
 
    # read a row slice
        print first_sheet.row_slice(rowx=0,
                                start_colx=0,
                                end_colx=2)

        datasheet = first_sheet 
    '''           

    def str_datasheet(self, datasheet):
        # convert to str
        numCols = len(datasheet[0])
        numRows = len(datasheet) 
        
        
        

    
    def norm_str(self, obj):
        if type(obj) == int:
            new = str(obj)
        elif type(obj) == float:
            new = str(int(obj))
        else:
            new = self.safe_uni_enc(obj)
        return new
    
    
    def get_real_UsedRange_old(self, datasheet):
        """
        Inspects the [M*N] datasheet.
        Tests: [(0,0),(1,0),(2,0), ... ,(N-1,0)]  and  [(0,0),(0,1),(0,2), ... , (0,M-1)]
        
        Returns a [(M-m) * (N-n)] datasheet.
        """
        numCols = len(datasheet[0])
        numRows = len(datasheet)
        #print numCols, numRows
        
        newNumCols = 0
        newNumRows = 0
        
        # testing horizontal used range
        for cell in datasheet[0]:
            if cell != None:
                newNumCols += 1
                
        # testing vertical used range
        for i in range(0, numRows):
            if datasheet[i][0] != None:
                newNumRows += 1
                
        #print newNumCols, newNumRows
        
        if newNumRows < numRows and newNumCols < numCols:
            # creating new datasheet containing the real used-range
            new_datasheet = []
            for i in range(0, newNumRows):
                new_datasheet.append(datasheet[i][0:newNumCols])
            return new_datasheet
        else:
            return datasheet    
 	
    
##class LoadDialog(wx.Dialog):
##    def __init__(self, prnt, filename, codec):
##        # generated method, don't edit
##        wx.Dialog.__init__(self, id=wx.NewId(), name='', parent=prnt,
##              pos=wx.DefaultPosition, size=wx.DefaultSize,
##              style=wx.DEFAULT_DIALOG_STYLE | wx.ALWAYS_SHOW_SB, title='Loading File...')
##        self.SetClientSize(wx.Size(390, 112))
##
##        self.gauge = wx.Gauge(id=wx.NewId(), name='gauge',
##              parent=self, pos=wx.DefaultPosition, size=wx.DefaultSize,
##              style=wx.GA_HORIZONTAL)
##
##        self.text = wx.StaticText(id=wx.NewId(), label="Opening file...\n" + filename.encode(codec, 'replace'),
##         name='text', parent=self, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0)
##            
##        #sizer initialization
##        sizer = wx.BoxSizer(wx.VERTICAL)
##        
##        #adding gui items
##        sizer.Add(self.text, 1, wx.LEFT|wx.TOP|wx.GROW)
##        sizer.Add(self.gauge, 1, wx.LEFT|wx.TOP|wx.GROW)
##        
##        #adjusting sizer
##        self.SetSizer(sizer)
##        sizer.SetSizeHints(self)
##        self.Layout()
##        self.Show()


class Unbalanced_Data(wx.Dialog):
    def __init__(self, prnt, missing_assessors, missing_samples, str_ass, str_samp):
        wx.Dialog.__init__(self, id=wx.NewId(), name=u'Unbalanced Data:', parent=prnt,
	                  pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        # missing values:
        self.radio1_selection = 1
        self.radio2_selection = 0
        self.missing_assessors = missing_assessors
        self.missing_samples = missing_samples
        
        #self.panel = wx.Panel(self, id=wx.NewId())

        box_balance = wx.BoxSizer(wx.VERTICAL)
        self.box_title = wx.StaticText(self, -1, "Select group to be removed for balancing the data:", size=(400,-1))
        self.radio1 = wx.RadioButton(self, -1, "Remove Assessors: ", style = wx.RB_GROUP, size=(400,-1))
        self.radio2 = wx.RadioButton(self, -1, "Remove Samples: ", size=(400,-1))
        box_balance.Add(self.box_title, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.ALL, 2)
        box_balance.Add(self.radio1, 1, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.ALL, 2)
        box_balance.Add(self.radio2, 1, wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.ALL, 2)
        #self.panel.SetSizer(box_balance)  
        
        if len(self.missing_assessors):
            self.SetTitle("Unbalanced Data:")
            if len(missing_assessors) > len(missing_samples):
                self.radio1.SetValue(False); self.radio2.SetValue(True)
            else:
                self.radio1.SetValue(True); self.radio2.SetValue(False)
            self.radio1.SetLabel("Remove Assessors: " + str_ass)
            self.radio2.SetLabel("Remove Samples: " + str_samp)
        else:
            self.radio1.Show(False)
            self.radio2.Show(False)
        ok = wx.NewId()
        self.buttonOK = wx.Button(id=ok, label=u'OK', parent=self)
        self.buttonOK.Bind(wx.EVT_BUTTON, self.OnButtonOK, id=ok)
        box_balance.Add(self.buttonOK, 0, wx.ALIGN_CENTER|wx.ALIGN_BOTTOM, 2)
        self.SetSizer(box_balance)
        self.Layout()
        self.SetClientSize(wx.Size(300, 100))
        self.Show()
        
    def OnButtonOK(self, event):
        self.radio1_selection = self.radio1.GetValue()
        self.radio2_selection = self.radio2.GetValue()
        self.EndModal(1)
        
    def ascii_enc(self, obj):
        """ 
        returns the decoded unicode representation of obj 
        """
        return obj.encode('ascii', 'ignore') # remove bad characters