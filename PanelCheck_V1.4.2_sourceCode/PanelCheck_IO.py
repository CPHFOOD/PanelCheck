import cPickle as bin
import copy, os.path
"""

Handles generic binary data-streams in PanelCheck (not the files with the sensory data, see LoadData.py).
Using the cPickle module.


================================================================

The pickle module provides the following functions to make the pickling process more convenient: 


dump( obj, file[, protocol]) 

Write a pickled representation of obj to the open file object file. This is equivalent to Pickler(file, protocol).dump(obj). 
If the protocol parameter is omitted, protocol 0 is used. If protocol is specified as a negative value or HIGHEST_PROTOCOL, the highest protocol version will be used. 

Changed in version 2.3: Introduced the protocol parameter. 

file must have a write() method that accepts a single string argument. It can thus be a file object opened for writing, a StringIO object, or any other custom object that meets this interface. 


load( file) 

Read a string from the open file object file and interpret it as a pickle data stream, reconstructing and returning the original object hierarchy. This is equivalent to Unpickler(file).load(). 
file must have two methods, a read() method that takes an integer argument, and a readline() method that requires no arguments. Both methods should return a string. Thus file can be a file object opened for reading, a StringIO object, or any other custom object that meets this interface. 

This function automatically determines whether the data stream was written in binary mode or not. 

================================================================


Henning Risvik (31.12.2007)

"""




class SessionData:
    """
    holds: 
      - string list of recently opened files
      - last used senosory data
      - view selections
      
    future: selections for each plot, maybe calculated data
    """
    
    
    def __init__(self):
        self.recent_files = [] # on the form: [[abspath1, delimiter1], [abspath2, delimiter2], ... , [abspathN, delimiterN]]
        self.sensory_data = None # SensoryData object (sensory data of self.recent_files[-1])
        self.view = {}
        self.view["grid"] = False
        self.view["legend"] = True
        self.view["selection"] = True
        self.image_save_path = ""
        self.export_active_plots = []
     
        
    def store_session_file(self, filename="session.dat"):
        """
        
        Save session data
        
        Note: overwrites file given by filename
        
        pickle.HIGHEST_PROTOCOL will be used
        
        """
        try:
            f = open(filename, "wb")      
            bin.dump(self, f, bin.HIGHEST_PROTOCOL)
            f.close()
        except:
            print "Could not write file."
        
        
    def update(self, **kwargs):
        
        limit = 15
    
        if "new_recent" in kwargs:
            temp = []
            for recent in self.recent_files:
                if recent[0] != kwargs["new_recent"][0]:
                    temp.append(recent)
            temp.append(kwargs["new_recent"])
            #print kwargs["new_recent"]
            if len(temp) > limit:
                del temp[0]
            self.recent_files = temp

        
        if "sensory_data" in kwargs:
            self.sensory_data = kwargs["sensory_data"]
        
        if "view" in kwargs:
            self.update_view(kwargs["view"])
            
        if "image_save_path" in kwargs:
            self.image_save_path = kwargs["image_save_path"]
        
        if "export_active_plots" in kwargs:
            self.export_active_plots = kwargs["export_active_plots"]
            
    
    
    def update_view(self, v):
        self.view["grid"] = v["grid"]
        self.view["legend"] = v["legend"]
        self.view["selection"] = v["selection"]
        

    def check_recent_files(self):
        temp = []
        for recent_file in self.recent_files:
            if os.path.isfile(recent_file[0]):
                temp.append(recent_file)
        self.recent_files = temp
                

        
def load_session_data(filename="session.dat"):
    """
    
    Loads SessionData object
    
    """
    try:
        f = open(filename, "rb")    
        session = bin.load(f) # class/object is reconstructed and returned
        session.check_recent_files()
        f.close()
        return session
    except:
        print "Could not load session file."
        return None
        