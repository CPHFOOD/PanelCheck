#!/bin/sh

sudo mkdir /Applications/PanelCheck                                          
sudo mv -fv "$(pwd)"/PanelCheck_V1.4.2_sourceCode/* /Applications/PanelCheck                           

OUTPUT=$(which pip)
if echo "$OUTPUT" | grep -q "pip"; then
    echo "Pip is already installed, type password to continue"
else 
	echo "Pip not installed, installing pip"
	sudo rm -f /usr/bin/easy_install*
	sudo rm -f /usr/local/bin/easy_install*
	curl -O https://svn.apache.org/repos/asf/oodt/tools/oodtsite.publisher/trunk/distribute_setup.py
	sudo python distribute_setup.py
	sudo rm distribute_setup.py
	sudo easy_install pip
fi


sudo pip2 install -U wxPython
sudo pip2 install matplotlib numpy scipy pandas xlrd rpy2 
sudo chmod u+x /Applications/PanelCheck/run_panelcheck.sh
ln -s /Applications/PanelCheck/run_panelcheck.sh $HOME/Desktop/

