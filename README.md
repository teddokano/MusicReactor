# What is this?
The MusicReactor is a demo application for I²C LED driver ([PCA9955B](https://www.nxp.com/products/power-management/lighting-driver-and-controller-ics/led-drivers/16-channel-fm-plus-ic-bus-57-ma-20-v-constant-current-led-driver:PCA9955BTW)) 
and I²C stepper motor controller ([PCA9629A](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/ic-bus-controller-and-bridge-ics/fm-plus-ic-bus-advanced-stepper-motor-controller:PCA9629APW)) using [MicroPython](https://micropython.org).  
The [MIMXRT1010-EVK](https://www.nxp.com/design/development-boards/i-mx-evaluation-and-development-boards/i-mx-rt1010-evaluation-kit:MIMXRT1010-EVK) is chosen as MocroPython running platform  

A brief demo [video is avairable on YouTube](https://youtu.be/X5pqsewMzrw).   
[![Demo video](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/demo_view.png)](https://youtu.be/X5pqsewMzrw)

As shown in the video, the LEDs and the stepper motors act flashing and switching rotation synchronized to the music beat.  

# Configuration
The demo is configured as next picture.  
![demo_diagram.jpeg](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/demo_diagram.jpeg)  
_Demo system diagram_  

![boards.png](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/boards.png)  
_Boards in the video_  

## Music source
A music signal is fed from source (PC or smart phone) via 3.5mm plug. 

## Interface board (Arduino shield)
The signal goes into an "interface board" which is made as an Arduino shield board.  
The interface board has two 3.5mm jack those are connected in parallel. Ether one of them can be input and other can be output for amplifier integrated speaker.  
The interface board convert the music signal to envelope waveform for ease of handling amplitude information in MCU. The waveform is fed to "A0" pin of MCU board. 

## MCU board
MIMXRT1010-EVK is chosed for this demo but any MicroPython enabled MCU can be used. I chose RT1010 MCU since its lightest MicroPython supported MCU from NXP.  
IMXRT1010-EVK detects peak of "A0" pin input. It samples the "A0" analog input in every 10ms (100Hz). The sampled data is compared with previous sample if it has certain defference.  
If the level is avobe threshold, the MCU detects it as peak then LED flashing and switching motor direction are done through I²C interface.  

## I²C devices
The LED driver is main device of this demo. It flashes LEDs synchronized to music beat.   
The Stepper motor controllers are option. If no stepper motor controller presented in the demo, the demo program just ignores its absence.  

### LED driver
16 channel LED driver: PCA9955B is used. The access of the LED driver from MCU is done with target address of 0xEC (0x76 in 7 bit presentation). 
This address is called as "sub address 1" in PCA9955B and enabled in default state after reset.  
All LED access are done with this address. So the multiple PCA9955B can be connected to this demo to perform same on every LED drivers.  
This demo is intended to use demonstration boards of [OM13483](https://www.nxp.jp/docs/en/user-guide/UM10729.pdf). Color(RGB) LED and white LED assignment is made for this OM13483. 
If user want to use PCA9955B-ARD, LED assignment may need to be changed and set EN pin input on the board. 

The demo program operates "Gradation Control" function on PCA9955B. 
All LED outputs are controlled with this function. The color LEDs are controlled automatically inside of the LED driver. 
Each red, green and blue channels are controlled by same waveform continuously but different phases. It makes color gradations. 
White LED is also controlled with the gradation control but it triggered by audio peak in single-shot. 

To enhance light effect, all channel brightness are controlled by PWM on addition to gradation control.  
The gradation control controls the brightness in output current. User can add brightness modulation by PWM control. 

### Stepper motor controller
Stepper motor is just an option on this demo.  
The demo programignores absence of stepper motor controller.  

PCA9629A is the stepper motor controller and "Five PCA9629 Stepper Motors Controller Board" is used.  
There are 5 motors but all motor controllers are controlled by same target address:0xE0 (0x70 in 7 bit presentation). 
The 0xE0 is the ALLCALL address in PCA9629A. 
Using this address, all stepper motor controllers in same way.  
The 0xE0 is the ALLCALL address in PCA9955B too. To avoid the conflict, the ALLCALL adress in PCA9955B is masked. 
Since all motor controller is operated with one target address, any number of controller can run on this demo. 
No need to be 5 motors always. 

After the system reset, the motors go home position to align direction of the arm on spindle. 
After that, the rotation is started.  
The motor rotation direction switched by peak detection. All motor actions are synchronized by command from MCU. 

# Setup
## Hardware
This demo requires "MIMXRT1010-EVK", "OM13483" (or "PCA9955B-ARD").  
The stepper motor controllers are option.  

### Interface board (Arduino shield type analog interface board)
On addition to that, user need to prepare an interface board by him/her-self.  
The interface board can be built either simple or flexible circuit. 

#### Interface board with simple circuit
The simple circuit board can be made very easy. It can be implemented with few passive components.  
It just forms connect 3.5mm audio jacks in parallel, simple diode detecotr circuit. 
The music signal on 3.5mm jack transformed to audio amplitude waveform and fed into MCU AD-conveter input pin.  

This circuit is recommended for first try because it's very simple. 
However, this type is sensitive for input signal level. 
This demo is expecting to have consumer audio line level. If it is less than expected, the demo will not react to the music. 
User need to adjust output volume on music source device. 

![simple_interface.jpg](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/simple_interface.jpg)  
_Interface board: simple circuit version_

#### Interface board with flexible circuit
Another option could be more analog processing on the interface board. 
This sample is called "flexible interface". This interface handle smaller input signal level.  
This circuit is having 100Hz LPF and op-amp based rectifier with gain. 
If the signal level is too big, a VR in input can be used for attenuation. 

![flexible_interface.jpg](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/flexible_interface.jpg)  
_Interface board: flexible circuit version_

## Software
Software setup need to be done in two steps. #1:Install MicroPython, #2:Install library and application code

### Step 1: Install MicroPython
Since the MicroPython is an interpreter, its executable need to be installed into the MCU first. 
The executable binary file can be downloaded from [download site](https://micropython.org/download/MIMXRT1010_EVK/).  
The file can be downloaded fron [this link](https://micropython.org/resources/firmware/MIMXRT1010_EVK-20230426-v1.20.0.bin)

The downloaded file need to be copied into the MCU.  
Set the J1 jumper pin in middle position (shorting 5-6 pins) and connect USB cable to J41. When the USB cable is connected to PC, it will appear as USB storage device named "RT1010-EVK". 
Copy downloaded "MIMXRT1010_EVK-20230426-v1.20.0.bin" file into the "RT1010-EVK" by drag&drop. When the copy completed, the USB strage will be re-mounted (appear after disappear).

![bin0](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/bin0.JPG)  
![bin2](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/bin2.JPG)
![bin1](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/bin1.JPG)  
_MIMXRT1010-EVK setting for Step 1: Install MicroPython_

<img src="https://github.com/teddokano/MusicReactor/blob/main/references/pictures/bin_copy.gif" width="352"><br />
_Copying MicroPython executable file into MCU by drag&drop_

### Step 2:Install library and application code
After MicroPython instration, change jumper configuration and USB connection. Set J1 jumber to short 3-4 pins and connect USB cable to J9.  
On PC, use Thonny application to copy the Python code into the MCU.  
For details of Thonny operation, please watch [this video](https://youtu.be/KHRxZc4m0Vc) (turn-ON YouTube subtitle feature for English). 

Everything in src directory in this repository into MCU under `flash/` folder. 
![py0](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/py0.JPG)  
![py1](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/py1.JPG)
![py2](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/py2.JPG)  
_MIMXRT1010-EVK setting for Step 2:Install library and application code_

![code copy](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/py_copy.gif)  
_Copying demo code and library into MCU by using Thonny_

### Everything is ready!
With completing these steps, the demo is ready!  
The demo will be running after reset or turning-ON the system :)

# Tips
### Select good music for demo :)  
This demo is just detecting music signal amplitude. Some very old music or recent music which is heavily amplitude complessed one may not give good result. 
It will be good idea to monitor the waveform from music source or MCU "A0" input pin which has amplitude information by oscilloscope when selecting demo source. 

### Adjusting input level
When using flexible circuit version interface board, music source output level may not need to adjust carefully. 
Even the signal is clipped on the interface corcuit, the demo may work correctly. However, if you take signal from speaker output from power-amplifire, it may need to be adjusted.  
The flexible version circuit has an LED to indicate "overload". Overload means the signal leel is close to satulation. If this LED is continuously kept ON, the signal may need to be attenuated. 

# Reference
- This demo had been built with ['mikan' class libraries](https://github.com/teddokano/mikan)
- I²C LED driver ([PCA9955B](https://www.nxp.com/products/power-management/lighting-driver-and-controller-ics/led-drivers/16-channel-fm-plus-ic-bus-57-ma-20-v-constant-current-led-driver:PCA9955BTW)) 
- I²C stepper motor controller ([PCA9629A](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/ic-bus-controller-and-bridge-ics/fm-plus-ic-bus-advanced-stepper-motor-controller:PCA9629APW))
- [MIMXRT1010-EVK](https://www.nxp.com/design/development-boards/i-mx-evaluation-and-development-boards/i-mx-rt1010-evaluation-kit:MIMXRT1010-EVK)
- [MicroPython](https://micropython.org).  

