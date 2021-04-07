# MixUS

## Software License GNU GPL
MixUS is an open source project that uses the GNU GPL v3 license. This license is used since PyQt5, the framework that the app is built on, is also GNU GPL v3.

1. Anyone can copy, modify and distribute this software.
2. You have to include the license and copyright notice with each and every distribution.
3. You can use this software privately.
4. You can use this software for commercial purposes.
5. If you dare build your business solely from this code, you risk open-sourcing the whole code base.
6. If you modify it, you have to indicate changes made to the code.
7. Any modifications of this code base MUST be distributed with the same license, GPLv3.
8. This software is provided without warranty.
9. The software author or license can not be held liable for any damages inflicted by the software.

More information about this license can be found [here](https://gist.github.com/kn9ts/cbe95340d29fc1aaeaa5dd5c059d2e60)

## Material License CC BY-SA
MixUS uses cads found in the [Open Build catalog](https://openbuildspartstore.com/). Thus, the material license for this project is the Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA). 
Under this license, you are free to:
- Share: copy and redistribute the material in any medium or format
- Adapt: remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:
- Attribution: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- ShareAlike: If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

More information about this license can be found [here](https://creativecommons.org/licenses/by-sa/4.0/?fbclid=IwAR1nMqahF2SNDniU5qahvUERI8FzeTw22oniBX6LPSnPQnIk0aLiyP96HRw)

## Mechanical Assembly
All the information for mechanical assembly can be found in [this wiki](https://github.com/BenjaminMoff/MixUS/wiki)
## Software

### Raspberry Pi Setup
If you chose to use a Raspberry Pi, you can run [this file](https://github.com/BenjaminMoff/MixUS/blob/main/configuration/PiConfig.sh) to automagically download Python, compile it, and get all the required packages.

If you are using the same 7" touch screen that we are (see the bom for the exact screen), you need to change the following in the Raspberry Pi's config.txt file:
- max_usb_curren=1
- hdmi_force_hotplug=1
- config_hdmi_boost=7
- hdmi_group=2
- hdmi_mode=87
- hdmi_drive=1
- display_rotate=0
- hdmi_cvt 1024 600 60 6 0 0 0

### Windows Setup
If you chose to use a Windows computer, you need to have a version of Python 3 installed. Then, you can run [this file](https://github.com/BenjaminMoff/MixUS/blob/main/configuration/Pythonconfig.bat) to automagically download the required packages.

The Windows version of the app cannot support the detection of the cup since it is done using a limit switch connected to a Raspberry Pi.

### Change the database
The app uses a database to remember all the drinks you like and the bottles you have. You can add more drinks to the database by running, in the terminal from MixUS/code/, this command: 
- Windows: py DrinkDatabaseUpdater.py
- Raspbian: python3 DrinkDatabaseUpdater.py

### Run MixUS
To run the application, you need to run the following command in the terminal from MixUS/code/:
- Windows: py Mixus.py
- Raspbian: python3 Mixus.py

### Documentation
The entire documentation for the code can be found [here](https://htmlpreview.github.io/?https://raw.githubusercontent.com/BenjaminMoff/MixUS/main/code/documentation/_build/html/index.html).
