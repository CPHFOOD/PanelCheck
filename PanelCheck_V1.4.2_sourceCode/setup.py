# setup.py
from setuptools import setup
import py2app
import uuid
import decimal
#from distutils.core import setup
#import py2app
from plistlib import Plist
import os

data =               [("R_scripts", [r"./R_scripts/sensmixedVer4.2.R", r"./R_scripts/sensmixedNoRepVer1.1.R"]),
                      ("",["fig.ico", "help.chm", "about.png", "logo.png", "about.html"]),
                      ("gfx", [r"./gfx/_pc_circle.gif",
                               r"./gfx/_pc_pointer_down.gif",
                               r"./gfx/_pc_pointer_up.gif", 
                               r"./gfx/_pc_pointer_right.gif", 
                               r"./gfx/_pc_pointer_left.gif", 
                               r"./gfx/_ctrl_print.gif", 
                               r"./gfx/_ctrl_print_setup.gif", 
                               r"./gfx/_ctrl_save.gif", 
                               r"./gfx/_ctrl_copy.gif", 
                               r"./gfx/_nav_home.gif", 
                               r"./gfx/_nav_zoom.gif", 
                               r"./gfx/_nav_pan.gif"]),
#                      ("",["MSVCP71.dll", "MSVCR71.dll"])
                      ]    

packages = [
             'pytz',
#            'numpy',
#            'six',
             'pandas', 
             'wx',
             'logging',
#            'matplotlib',
#            'rpy2',
#            'rpy2.robjects',
#            'scipy',
#            'xlrd',
#            'uuid',
#            'decimal'
          ]

excludes = [
    '_gtkagg',
    '_tkagg',
    'tcl',
    'Tkconstants',
    'Tkinter',
    'tcl',
    'pywin.debugger', 
    'pywin.debugger.dbgcon',
    'pywin.dialogs',
    'bsddb',
    'curses',
    'email',
 #   'logging',
    'readline',
    'setuptools',
    '_ssl'
    ]

#setup(  
#      app = ['PanelCheck.py'],
#      data_files = data,
#      options={'py2app': OPTIONS},
#      setup_requires = ['py2app'],
#      name = 'PanelCheck_V1.5.0', 
#      version = '1.5.0',
#      description = 'Data Analysis Tool',
#      author = 'Henning Risvik and Oliver Tomic',
#      url = 'http://www.panelcheck.com/',
#      )

name = 'PanelCheck'
version = '1.5.0'
Icon = './fig'+".ico"

 # Build the .app file
setup(
     app=[ name + '.py' ],
     options=dict(
         py2app=dict(
             iconfile=Icon,
             packages=packages,
             excludes=excludes,
             site_packages=True,
             argv_emulation= True,
             matplotlib_backends = '*',
             resources=data,
             optimize=True,
           #  versions=version,
             dylib_excludes=['Rblas.dylib','R.dylib','libR.dylib'],

             plist=dict(
                 CFBundleName               = name,
                 CFBundleShortVersionString = version,     # must be in X.X.X format
                 CFBundleGetInfoString      = name+" "+ version,
                 CFBundleExecutable         = name,
                 translatesAutoresizingMaskIntoConstraints='YES',
             ),
         ),
     ),
)

