# LMT Widget Tool (LWT)

The LMT Widget Tool is as tool designed to facilitate the extraction and analysis of behavioral data from .sqlite databases from the Live Mouse Tracker (LMT).
It helps users with no programming experience to easily visualize, analyze and extract relevant analysis.

You will find more information about LMT on its [website](https://livemousetracker.org/) and [publication](https://www.nature.com/articles/s41551-019-0396-1.epdf?shared_access_token=8wpLBUUytAaGAtXL96vwIdRgN0jAjWel9jnR3ZoTv0MWp3GqbF86Gf14i30j-gtSG2ayVLmU-s57ZbhM2WJjw18inKlRYt31Cg_hLJbPCqlKdjWBImyT1OrH5tewfPqUthmWceoct6RVAL_Vt8H-Og%3D%3D).

In our tool, we used the [LMT-Analysis](https://github.com/fdechaumont/lmt-analysis) repo v1.0.5, from [Fabrice de Chaumont](https://github.com/fdechaumont) with only few changes for our tool to work.

If you have any questions or comments, feel free to contact us, Damien (damien.huzard@igf.cnrs.fr) or Paul (paul.carrascosa@igf.cnrs.fr).

## The Video Tutorial:
[![Watch the video](https://youtu.be/JdHjRV_WiZ0?si=aDXVUr696PyLIxlh)]

## 1. Download (and unzipping)

First of all, you will need to download the folder which contains all of the files to run the tool:<br><br>
![alt_download](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Download.jpg?raw=true)<br><br>
Place the ZIP file in the folder of your choice, unzip it (for example with [7-Zip](https://www.7-zip.org/download.html)).<br>

## 2. Installation steps (for Windows users):
### 2.1. Python

To make the tool work, you will need Python version 3.10.11. Download the [3.10.11 Python version here](https://www.python.org/downloads/release/python-31011/). Go down until the 'Files' section and install `Windows installer (64-bit)` (64-bit is recommended but if your computer is on a 32-bit OS you should download the 32-bit version).<br><br>
![alt_python](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Python.jpg?raw=true)<br><br>
Then, execute the .exe file you just downloaded.

## **! WARNING !**<br>
During the installation, make sure to check the box "Add python.exe to PATH" and click on "Install now" until Python is installed:<br><br>
![alt_path](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Path.jpg?raw=true)<br><br>

### 2.2. LWTools

Once you have installed Python, open your command prompt to install the tool. (To open the command prompt, press the keys Windows + R, then type "cmd" and press Enter.) In your command prompt, put the following command :

```bash
pip install LWTools
```
this command will automatically install the latest version of our LWTools library from the [pypi website](https://pypi.org/project/LWTools/).

## 3. Launch Jupyter Lab

Each time you want to use the tool, you will have to launch Jupyter Lab first. 

To launch Jupyter Lab, open a command prompt and write (or copy-paste):
```bash
jupyter lab
```
This will open a Jupyter Lab tab in your favorite web browser. (! Warning ! if you close the command prompt it will also close the Jupyter Lab session).

## 4. Launching the LWTools notebook

Once Jupyter Lab is launched, go to the folder you downloaded from Github during the step <b> 1. Download (and unzipping) </b> and open the <b> scripts </b> folder (e.g. '...\LMT_Widget_Tool-LWT-main\scripts').

## **! WARNING !**

Before using the tool, make sure to restart the kernel to clear it :<br><br>
![alt_restart_kernel](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Restart_kernel.jpg?raw=true)<br><br>
Sometimes you will need to restart the kernel when it seems that the tool crashed, but don’t do it when it’s running !

Then, you can enjoy the tool, by opening the <b>LMT_Widget_Tool.ipynb</b> and running it within Jupyter Lab! (If so far, you never used a jupyter lab before, we recommend trying [that tutorial](https://jupyter.org/try-jupyter/lab/?path=notebooks%2FIntro.ipynb)).
<br><br>

## Order for analysis<br>

First, you will have to execute the first cell code to install the packages for the tool. Click on the cell you want to execute and press the keys Ctrl + Enter <br><br>

### Rebuild databases and convert into csv files

![alt_rebuil_plus_export](https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT/blob/main/media/images/Rebuild_plus_export.jpg?raw=true)<br><br>
The part 1 will rebuild the databases by deleting the data and rebuild them using the detections and export these data into csv files. It is recommanded to do timebins of 5 or 10 minutes for each bin<br><br>

### **! WARNING !** for 1.1<br><br>
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

## Future developments

We are also planning to improve and extend to possibilities of this tool, you can also send us your suggestions and feedbacks! <br>
Here are few ideas of future developments:<br>
  - More statistical analyses
  - defining ROI from your LMT cages (defining zones of interest, like food-zone, house, ...)
  - Graphs of distance
  - exporting all graphs and stats at once

## Another Cool LMT Tool

If you do not know it yet, please have a look to Nicolas Torquet's own [LMT_toolkit_analysis](https://github.com/ntorquet/lmt_toolkit_analysis)! It is really a powerful way to extract and visualize data from your .sqlite directly. <br>
It might be still a bit harder to install and run than our tool, but it is a beautiful and inspiring initiative! Try it and let him/us know!

## License

LMT_Widget_Tool is released under the GNU GPL v3.0 licence. See the [LICENSE](LICENSE) file.

Copyright (C) 2023 IGF - CNRS - INSERM - Université de Montpellier

LMT_Widget_Tool uses the LMT-analysis code provided on [GitHub](https://github.com/fdechaumont/lmt-analysis). This code is also under the GNU GPL v3.0 licence.
[GNU GPL ?](https://choosealicense.com/licenses/mit/)
