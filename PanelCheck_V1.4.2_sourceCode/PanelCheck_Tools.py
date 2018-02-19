import wx, re, os, sys, codecs


from Progress_Info import Progress
from Summary import SummaryFrame
from Grid import *

from PanelCheck_IO import *


def split_path(abs_path):
        """
        Returns tuple with: (directory-path, filename, file_extension)
        """
        if os.name == 'nt': # windows (same on a 'ce' system?)
            match = re.search(r"(.*)/(.*)\.(.*)", abs_path)
        else: # hopefully some unix system (not sure about how it looks on mac)
            match = re.search(r"(.*)/(.*)\.(.*)", abs_path)
        return match.groups() 
        # three items in a tuple: ('directory-path', 'filename', 'file-extension')
        


def summaryConstructor(self, sampleList, assessorList, replicateList, 
                            attributeList):
    """
    Creates summary text of given lists.
    
    @type sampleList:     list
    @param sampleList:    Complete list of ALL samples
    
    @type assessorList:     list
    @param assessorList:    Complete list of ALL assessors
        
    @type replicateList:    list
    @param replicateList:   Complete list of ALL replicates
        
    @type attributeList:    list
    @param attributeList:   Complete list of ALL attributes
    """
    # TODO: Recognition of which plotting methods are possible based on number of replicates
        
    infoString = 'Number of assessors:   ' + str(len(assessorList)) + \
                        '\n=================\n\n'
        
    for assessor in assessorList:
        infoString = infoString + str(assessorList.index(assessor) + 1) + \
                        ': ' + assessor + '\n'
        
    infoString = infoString + '\n\n\n'
        
    infoString = infoString + 'Number of samples:   ' + str(len(sampleList)) + \
                        '\n================\n\n'
        
    for sample in sampleList:
            infoString = infoString + str(sampleList.index(sample) + 1) + \
                        ': ' + sample + '\n'
        
    infoString = infoString + '\n\n\n'
        
    infoString = infoString + 'Number of replicates:   ' + str(len(replicateList)) + \
                        '\n================\n\n'
        
    infoString = infoString + '\n\n\n'
        
    infoString = infoString + 'Number of attributes:   ' + str(len(attributeList)) + \
                    '\n================\n\n'
        
    for attribute in attributeList:
            infoString = infoString + str(attributeList.index(attribute) + 1) + \
                        ': ' + attribute + '\n'
        
    return infoString





def summaryConstructor2(self, sampleList, assessorList, replicateList, 
                            attributeList, mv_inf, summary):
    """
    Creates summary text of given lists. 
    
    @type sampleList:     list
    @param sampleList:    Complete list of ALL samples
    
    @type assessorList:     list
    @param assessorList:    Complete list of ALL assessors
        
    @type replicateList:    list
    @param replicateList:   Complete list of ALL replicates
        
    @type attributeList:    list
    @param attributeList:   Complete list of ALL attributes
    """
    # TODO: Recognition of which plotting methods are possible based on number of replicates
    
    
    infoString = 'Number of assessors:   ' + str(len(assessorList)) + '\n=================\n\n'
    str_ind = summary.str_ind + len(infoString)
    
    txt_ctrl = summary.textSummary3
    
    txt_ctrl.AppendText(infoString)
    txt_ctrl.SetInsertionPoint(0)
    
    for assessor in assessorList:
        missing = "(No missing values)"
        color = "BLUE"
        if mv_inf[assessor] > 0:
            missing = "(%.2f" % (mv_inf[assessor] * 100.0)
            missing += "% missing values)"
            color = "RED"
        infoString = str(assessorList.index(assessor) + 1) +  ': ' + assessor + '   '
        infoString = infoString + missing + '\n'
        str_ind += len(infoString)
        txt_ctrl.AppendText(infoString)
        txt_ctrl.SetStyle(str_ind-len(missing)-1, str_ind-1, wx.TextAttr(color))
        
    infoString = '\n\n\n'
        
    infoString = infoString + 'Number of samples:   ' + str(len(sampleList)) + \
                        '\n================\n\n'
        
    for sample in sampleList:
            infoString = infoString + str(sampleList.index(sample) + 1) + \
                        ': ' + sample + '\n'
        
    infoString = infoString + '\n\n\n'
        
    infoString = infoString + 'Number of replicates:   ' + str(len(replicateList)) + \
                        '\n================\n\n'
        
    infoString = infoString + '\n\n\n'
        
    infoString = infoString + 'Number of attributes:   ' + str(len(attributeList)) + \
                    '\n================\n\n'
        
    for attribute in attributeList:
            infoString = infoString + str(attributeList.index(attribute) + 1) + \
                        ': ' + attribute + '\n'
        
    txt_ctrl.AppendText(infoString)
    txt_ctrl.SetInsertionPoint(0)
    txt_ctrl.Refresh()
    txt_ctrl.Update()



# system encoding:
encoding1 = sys.getfilesystemencoding()# can be:   'mbcs' win32
encoding2 = sys.stdin.encoding         # can be:   'cp850' win32 extended latin-1 type
encoding3 = sys.getdefaultencoding()   # usually:  'ascii'

codec = encoding1

# setting encoder and decoder:
try:
    enc, dec = codecs.lookup(encoding1)[:2] 
except LookupError:
    enc, dec = codecs.lookup(encoding2)[:2]
    codec = self.encoding2
except LookupError:
    enc, dec = codecs.lookup('latin-1')[:2]
    codec = 'latin-1'
except LookupError:
    enc, dec = codecs.lookup('utf-8')[:2]
    codec = 'utf-8'
except LookupError:
    enc, dec = codecs.lookup(encoding3)[:2] # most likely using 'ascii'
    codec = encoding3

def safe_uni_dec(obj):
        """ 
        returns the decoded unicode representation of obj 
        """
        try:
            #uni = self.dec(obj)[0]
            #print "unicode type string: " + self.enc(uni)[0] # may return: UnicodeEncodeError
            #return uni
            return dec(obj)[0]
        except UnicodeDecodeError: # cannot handle characters with code table
            #print 'UnicodeDecodeError: trying with "replace"..'
            return unicode(obj, codec, 'replace')
        except UnicodeDecodeError: # cannot handle characters with code table
            #print 'UnicodeDecodeError: trying with "replace" and with sys.stdin.encoding'
            codec = encoding2
            return unicode(obj, codec, 'replace')
        except UnicodeDecodeError:
            #print 'UnicodeDecodeError: cannot decode'
            return str(obj)
        except UnicodeEncodeError:
            return enc(obj)[0]        
        except: 
            return obj.encode('ascii', 'ignore')
            
            
def safe_uni_enc(obj):
        """ 
        returns the decoded unicode representation of obj 
        """
        try:
            # trying to encode (transform from "natural" into "artificial") with known encoding 'sys.getfilesystemencoding()'
            uni = enc(obj)[0]
            # returning decoded (to "natural" unicode representation)
            return dec(uni)[0]
        except UnicodeEncodeError: # cannot handle characters with code table
            #print 'UnicodeEncodeError: trying with "replace"..'
            uni = obj.encode(codec, 'replace')
            return unicode(uni, codec, 'replace')
        except UnicodeEncodeError: # cannot handle characters with code table
            #print 'UnicodeEncodeError: trying with "replace" and with sys.stdin.encoding'
            codec = encoding2
            uni = obj.encode(codec, 'replace')
            return unicode(uni, codec, 'replace')
        except UnicodeEncodeError:
            #print 'UnicodeEncodeError: cannot encode'
            return str(obj)
        except UnicodeDecodeError:
            return safe_uni_dec(obj)


def save_dataset(abspath, dataset):
        """
        Saves a dataset as a standard PanelCheck file
        """

        try:
            f = open(abspath, 'w')

            f.write("Assessor\tSample\tReplicate\t")
            for att in dataset.AttributeList:
                if att == dataset.AttributeList[-1]: f.write(att.encode(codec))
                else: f.write(att.encode(codec) + "\t")
            f.write("\n")

            for ass in dataset.AssessorList:
                for samp in dataset.SampleList:
                    for rep in dataset.ReplicateList:
                        f.write(ass.encode(codec) + "\t" + samp.encode(codec) + "\t" + rep.encode(codec) + "\t")
                        for i in range(len(dataset.AttributeList)):
                            if i >= len(dataset.AttributeList)-1: f.write(str(dataset.SparseMatrix[(ass, samp, rep)][i]))
                            else: f.write(str(dataset.SparseMatrix[(ass, samp, rep)][i]) + "\t")
                        f.write("\n")
            f.close()

            return "Dataset saved as: " + abspath.encode(codec)

        except:
            import traceback
            print traceback.print_exc()
            return traceback.format_exc()


class DelimiterSelector(wx.Dialog):
    def __init__(self, prnt):
        wx.Dialog.__init__(self, id=wx.NewId(), name=u'Select delimiter:', parent=prnt, title="Select delimiter:",
	                  pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        pathname = os.path.dirname(sys.argv[0]) 
        self.progPath = os.path.abspath(pathname).decode(sys.getfilesystemencoding())
        figpath = self.progPath + u'/fig.ico'
        self.SetIcon(wx.Icon(figpath,wx.BITMAP_TYPE_ICO))
            
        s_sizer = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(self, id=wx.NewId())
        
        
	sizer_inner = wx.BoxSizer(wx.VERTICAL)
	text = wx.StaticText(panel, id=wx.NewId(), label=u'Select delimiter for current file:')
	self.d1 = wx.RadioButton(panel, label="Tab delimited")
	self.d2 = wx.RadioButton(panel, label="Comma delimited")
	self.d3 = wx.RadioButton(panel, label="Semicolon delimited")
	self.d4 = wx.RadioButton(panel, label="Other delimiter:")	    
	self.in_ext = wx.TextCtrl(panel, id=wx.NewId())

	sizer_inner.Add(text, 0, wx.ALL, 5)
	sizer_inner.Add(self.d1, 0, wx.ALL, 5)
	sizer_inner.Add(self.d2, 0, wx.ALL, 5)
	sizer_inner.Add(self.d3, 0, wx.ALL, 5)
	sizer_inner.Add(self.d4, 0, wx.ALL, 5)
	sizer_inner.Add(self.in_ext, 0, wx.ALL, 15)

	panel.SetSizer(sizer_inner)

	self.d1.SetValue(True)
	self.in_ext.SetValue("\t")

	self.SetSize((320,240))	
	            
        self.id_ok = wx.NewId()
        self.ok = wx.Button(self, id=self.id_ok, label=u'Apply')
        self.b_panel = wx.Panel(self, id = wx.NewId())
        self.b_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.b_sizer.Add(self.b_panel, 1, wx.EXPAND)
        self.b_sizer.Add(self.ok, 0, wx.ALIGN_RIGHT|wx.ALL)
        #self.Bind(wx.EVT_CLOSE, self.Close)
        self.Bind(wx.EVT_BUTTON, self.OnButtonOK, id=self.id_ok)	
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(s_sizer, 1, wx.GROW)
        sizer.Add(self.b_sizer, 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()  
        self.Refresh()        
        
        
    def OnButtonOK(self, event):
        
        if self.d1.GetValue():
            self.EndModal(0)
        elif self.d2.GetValue():
            self.EndModal(1)
        elif self.d3.GetValue():
            self.EndModal(2)
        elif self.d4.GetValue():
            self.delimiter = self.in_ext.GetValue()
            self.EndModal(3)            
        else:
            self.Close()      