# What is this?
The MusicReactor is a demo application for I²C LED driver ([PCA9955B](https://www.nxp.com/products/power-management/lighting-driver-and-controller-ics/led-drivers/16-channel-fm-plus-ic-bus-57-ma-20-v-constant-current-led-driver:PCA9955BTW)) 
and I²C stepper motor controller ([PCA9629A](https://www.nxp.com/products/interfaces/ic-spi-i3c-interface-devices/ic-bus-controller-and-bridge-ics/fm-plus-ic-bus-advanced-stepper-motor-controller:PCA9629APW)) using [MicroPython](https://micropython.org).  
The [MIMXRT1010-EVK](https://www.nxp.com/design/development-boards/i-mx-evaluation-and-development-boards/i-mx-rt1010-evaluation-kit:MIMXRT1010-EVK) is chosen as MocroPython running platform  

A brief demo [video is avairable on YouTube](https://youtu.be/X5pqsewMzrw).   
[![Demo video](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/demo_view.png)](https://youtu.be/X5pqsewMzrw)

As shown in the video, the LEDs and the stepper motors act flashing and switching rotation synchronized to the misic beat.  

# Configuration
The demo is configured as next picture.  
![demo_diagram.jpeg](https://github.com/teddokano/MusicReactor/blob/main/references/pictures/demo_diagram.jpeg)
## Music source
A misic signal is fed from source (PC or smart phone) via 3.5mm plug. 

## Interface board (Arduino shield)
The signal goes into an "interface board" which is made as an Arduino shield board.  
The interface board has two 3.5mm jack those are connected in parallel. Ether one of them can be input and other can be output for amplifier integrated speaker.  
The interface board convert the misic signal to envelope waveform for ease of handling amplitude information in MCU. The waveform is fed to "A0" pin of MCU board. 

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


