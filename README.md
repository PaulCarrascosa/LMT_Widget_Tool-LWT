# LMT Widget Tool (LWT)

LMT Widget Tool is as tool for the Live Mouse Tracker (LMT) data analysis for users without programming experience.

You will find more information about LMT on its [website](https://livemousetracker.org/) and [publication](https://www.nature.com/articles/s41551-019-0396-1.epdf?shared_access_token=8wpLBUUytAaGAtXL96vwIdRgN0jAjWel9jnR3ZoTv0MWp3GqbF86Gf14i30j-gtSG2ayVLmU-s57ZbhM2WJjw18inKlRYt31Cg_hLJbPCqlKdjWBImyT1OrH5tewfPqUthmWceoct6RVAL_Vt8H-Og%3D%3D).

In our tool, we use the LMT-Analysis v1.0.5 with few changes in files for our tool to work.

## 1. Download

First of all, you will need to download the folder which contains all of the files to run the tool:<br><br>
![alt_download](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Download.jpg?raw=true)<br><br>
First of all, move the zipped folder on your desktop. Once it's done, make sure to unzip the zipped folder you just download (download [7-Zip](https://www.7-zip.org/download.html) for free to unzip zipped folders if you don't have it already on your computer).<br>
To unzip, you have to do a right-click on the folder, then click on "7-Zip" and "Extract here". If you are using a Windows 11 version, do a right-click on the zipped folder, then click on "Show more options", then "7-Zip" and "Extract here". 

## 2. Installation
### 2.1. Python

To make the tool work, you will need a specific version of Python. Download the 3.10 Python version [here](https://www.python.org/downloads/release/python-31011/). Go down until the 'Files' section and install 'Windows installer (64-bit)' (64-bit is recommended but if your computer is on a 32-bit OS you should download the 32-bit version).<br><br>
![alt_python](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Python.jpg?raw=true)<br><br>
Then, execute the .exe file you just downloaded.

## :warning: WARNING<br>
During the installation, make sure to check the box "Add python.exe to PATH" and click on "Install now" until Python is installed:<br><br>
![alt_path](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Path.jpg?raw=true)<br><br>

### 2.2. LWTools

Once you have installed Python, open your command prompt to install the tool. To open the command prompt, press the keys Windows + R, then type "cmd" and press Enter. In your command prompt, put the following command :

```bash
pip install LWTools
```

## 3. Launch Jupyter Lab

Each time you want to launch the tool, you will need to launch Jupyter Lab first. To launch Jupyter Lab, you will have to open you command prompt (if it is not already open) and use the following command :

```bash
jupyter lab
```

## 4. Launch the tool

Once Jupyter Lab is launched, find the folder you downloaded from Github during the first step and open the folder '...\LMT_Widget_Tool-LWT-main\scripts' in Jupter Lab and open the file :

```bash
LMT_Widget_Tool.ipynb
```

## :warning: WARNING

Before using the tool, make sure to restart the kernel to clear it :<br><br>
![alt_restart_kernel](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Restart_kernel.jpg?raw=true)<br><br>
Sometimes you will need to restart the kernel when it seems that the tool crashed, but don’t do it when it’s running !

Here you can enjoy the tool !

## Order for analysis<br><br>

First, you will have to execute the first cell code to install the packages for the tool. Click on the cell you want to execute and press the keys Ctrl + Enter <br><br>

### Rebuild databases and convert into csv files

![alt_rebuil_plus_export](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Rebuild_plus_export.jpg?raw=true)<br><br>
The part 1 will rebuild the databases by deleting the data and rebuild them using the detections and export these data into csv files. It is recommanded to do timebins of 5 or 10 minutes for each bin<br><br>

### :warning: Warning for 1.1<br><br>
![alt_only_export](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Only_export.jpg?raw=true)<br><br>
The part 1.1 is optional. It is usefull only if you want to convert your data into csv using different timebins. So be careful with this code cell, use it only if you want to change the timebins of your data.<br><br>

![alt_merge](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Merge.jpg?raw=true)<br><br>
The part 2 will merge the csv files created into one csv file which will be used by the tool for the analysis.<br><br>

![alt_tool](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Tool.jpg?raw=true)<br><br>
The part 3 will start the tool, you will need to use the merged file that you will have with the third part.<br><br>

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

LMT_Widget_Tool is released under the GNU GPL v3.0 licence. See the [LICENSE](LICENSE) file.

Copyright (C) 2023 IGF - CNRS - INSERM - Université de Montpellier

LMT_Widget_Tool uses the LMT-analysis code provided on [GitHub](https://github.com/fdechaumont/lmt-analysis). This code is also under the GNU GPL v3.0 licence.
[GNU GPL ?](https://choosealicense.com/licenses/mit/)
