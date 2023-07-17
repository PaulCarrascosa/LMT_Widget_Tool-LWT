# LMT Widget Tool (LWT)

LMT Widget Tool is as tool for the Live Mouse Tracker (LMT) data analysis for users without programming experience.

You will find more information about LMT on its [website](https://livemousetracker.org/) and [publication](https://www.nature.com/articles/s41551-019-0396-1.epdf?shared_access_token=8wpLBUUytAaGAtXL96vwIdRgN0jAjWel9jnR3ZoTv0MWp3GqbF86Gf14i30j-gtSG2ayVLmU-s57ZbhM2WJjw18inKlRYt31Cg_hLJbPCqlKdjWBImyT1OrH5tewfPqUthmWceoct6RVAL_Vt8H-Og%3D%3D).

In our tool, we use the LMT-Analysis v1.0.5 with few changes in files for our tool to work.

## Download

First of all, you will need to download the folder which contains all of the files to run the tool.

## Installation
### Python

To make the tool work, you will need a specific version of Python. Download the 3.10 Python version [here](https://www.python.org/downloads/release/python-31011/). Go down until the 'Files' section and install 'Windows installer (32-bit)' or 'Windows installer (64-bit)' (depending of your system) and execute the downloaded file. 

During the installation, make sure to check the box "Add python.exe to PATH" and follow the process until Python is installed.

### Jupyter Lab

Once you have installed Python, open your command prompt. Here, put the following command :

```bash
pip install jupyterlab==3.5.0
```

## Launch Jupyter Lab

Each time you want to launch Jupyter Lab, you will have to open you command prompt and use the following command :

```bash
jupyter lab
```

## Launch the tool

After the installation, open the folder .../scripts in Jupter Lab and open the file :

```bash
LMT_Widget_Tool.ipynb
```
First, you will have to execute the first cell code to install the packages for the tool. Once all the packages are installed, close JupyterLab and close the Kernel by pressing the keys "Ctrl + C" inside of your prompt. Then restart JupyterLab in your prompt using :

```bash
jupyter lab
```

Here you can enjoy the analysis !

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[GNU GPL ?](https://choosealicense.com/licenses/mit/)
