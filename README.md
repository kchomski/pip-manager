# pip-manager [![Build Status](https://travis-ci.org/kchomski/pip-manager.svg?branch=master)](https://travis-ci.org/kchomski/pip-manager)

**pip-manager** is a command line tool to make Python packages management easy.


## Table of Contents
1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Contributing](#contributing)
5. [Support](#support)
6. [License](#license)
7. [Acknowledgements](#acknowledgements)

## 1. Requirements
**pip-manager** works on both Python 2 and Python 3 (tested on `python2.7` and `python3.5+`) and is Linux and Windows compatible (tested on Linux Mint 18.2 and Windows 7). 

#### Dependencies:
**pip-manager** is written purely in Python and has `pip` as an only dependency.  

#### IMPORTANT note for Windows users:
On Windows you have to install ported `curses` library ([link](http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses)) as native Python `curses` does not work there.

## 2. Installation
**pip-manager** can be easily installed using `pip`:
```
pip install -U pip-manager
```
If you want to install pip-manager system-wide just use `sudo`:
```
sudo pip install -U pip-manager
```

## 3. Usage
To run **pip-manager** just type `pip-manager` in your terminal window and hit `Enter`.  
If you made system-wide installation, run pip-manager with:
```
sudo -H pip-manager
```

You will see something very similar to this:
```
pip-manager v1.0.0 (python 2.7.12)
┌─────────────────────────────────────────────────────────────────────────────┐
│Checking the newest version for cssselect                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```
After a (hopefully) short while pip-manager will be ready to use:  
```
pip-manager v1.0.0 (python 2.7.12)
[ ] cssselect                          1.0.1        1.0.1
[ ] cycler                             0.10.0       0.10.0
[ ] decorator                          4.0.11       4.0.11
[ ] django                             1.11.3       1.11.3
[ ] docutils                           0.13.1       0.13.1
[ ] entrypoints                        0.2.3        0.2.3
[ ] enum34                             1.1.6        1.1.6
[ ] fancycompleter                     0.7          0.7
[ ] flask                              0.10         0.12.2
[ ] functools32                        3.2.3.post2  3.2.3.post2
[ ] futures                            3.1.1        3.1.1
[ ] html5lib                           0.999999999  0.999999999
[ ] hupper                             1.0          1.0
[ ] hyperlink                          17.2.1       17.2.1
Page: 1/5
Options:
Up/Down - prev/next package
Left/Right - prev/next page
PgUp/PgDn - jump up/down by 5
Home/End - jump to top/bottom
Space - (un)select package
A - toggle all
Enter - upgrade selected
Delete - uninstall selected
Q - exit
```
As you can see options are displayed all the time and are pretty self-explanatory, so using `pip-manager` should be really simple and straightforward.

Second column shows current version installed and third column shows the newest stable version available.  
It is not visible here, but if there is newer version available, it will be printed with **bold** font.  
If newest version is already installed it will be printed greyed out.

#### IMPORTANT: Protected distributions
To protect yourself from accidentally removing needed distributions, you can add them to `[protected]` section in `config.ini` file (located in `pip-manager` installation directory).  
This way you can select all packages by pressing `A`, uninstall them with `Delete` and everything except protected packages will be uninstalled.  
By default `pip`, `setuptools`, `wheel` and `pip-manager` are listed in the aforementioned file. To uninstall protected distributions you have to either uninstall them manually (`pip uninstall some_dist`) or remove them from `config.ini` file.

 
## 4. Contributing
Contributions are always welcome - just:  
1. Fork the project.  
2. Commit your changes on a feature/fix branch.  
3. Push.  
4. Submit a pull request.  
5. Have your changes merged :)  

## 5. Support
If you need assistance, want to report a bug or request a feature, please raise an issue [here](https://github.com/kchomski/pip-manager/issues).

## 6. License
**pip-manager** is released under the terms of the MIT License. Please refer to the `LICENSE.txt` file for more details.

## 7. Acknowledgements
Great thanks to `pip` creators and contributors for making life easier for the rest of us. 
