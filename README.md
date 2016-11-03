# Pulseq-GPI
---
Python language based implementation of [Pulseq](http://pulseq.github.io) in [GPI Lab](http://gpilab.com). Tested on macOS Sierra 10.12.1.

## TABLE OF CONTENTS
1. Installing GPI Lab
2. Installing Pulseq for GPI Lab
3. Getting started
4. Issues & TODOs
5. Appendix
6. Contributing

## 1. Installing GPI Lab
1. Download v1 beta from - http://gpilab.com/downloads/
2. Typical installation on Mac (no guarantee for Windows)

## 2. Installing Pulseq for GPI Lab
1. Clone [repo](https://github.com/sravan953/pulseq-gpi)
2. Open GPI Lab
3. Click on `Config` > `Generate User Library`
![](https://github.com/sravan953/pulseq-gpi/blob/master/screenshots/gen_user_lib.png)

4. Place the downloaded folder inside this auto-generated user library folder:
  Mac - `/Users/<user-name>/gpi/<user-name>/`
5. Place gre_GPI.net file in:
  Mac - `/Applications/GPI.app/Contents/Resources/miniconda/share/doc/gpi/Examples/`
![](https://github.com/sravan953/pulseq-gpi/blob/master/screenshots/gpi_network_in_examples.png)

> PRO TIP: With your Finder open, press `⌘ + Shift + G` and paste the path to jump to that location

## 3. Getting started
1. Open GPI Lab
2. Click on `Help` > `Examples`
![](https://github.com/sravan953/pulseq-gpi/blob/master/screenshots/gpi_help_examples.png)

3. Drag and drop the `gre_GPI.net` file onto the blank canvas
4. Configure the pulse sequence values by right clicking on the `ConfigSeq` and `AddBlock` nodes (refer Appendix for configuration values)
![](https://github.com/sravan953/pulseq-gpi/blob/master/screenshots/config_params.png)

5. From left to right, click `Compute` events in each Node
6. Right click on the Matplotlib Node to view graphs

## 4. Issues & TODO
1. Issue: Only cartesian coordinate system supported
2. Issue: Node parameters get reset when loading network from a save file
3. TODO: Implement read from seq file functionality
4. TODO: Customize Matplotlib node to support subplots

## 5. Appendix
> (Nodes are configured from left to right)

> (Parameters not mentioned have to be set to 0)

First AddBlock Node - Rf, Gz

Event 1 - Rf

Parameter | Value
:---:|:---:
duration (s) | 2e-3
timeBwProduct (s) | 4
apodization | 0.5
sliceThickness (m) | 5e-3

---

Second AddBlock Node - GxPre, GyPre, GzReph

Event 1 - G

Parameter | Value
:---:|:---:
channel | x
duration (s) | 2e-3
area | -145.681818

Event 2 - GyPre

Event 3 - G

Parameter | Value
:---:|:---:
channel | z
duration (s) | 2e-3
area | -403

---

Third AddBlock Node - Delay 1

Event 1 - Delay

Parameter | Value
:---:|:---:
delay (s) | 0.002775

---

Fourth AddBlock Node - Gx, ADC

Event 1 - Gx

Parameter | Value
:---:|:---:
readoutTime (s) | 6.4e-3

Event 2 - ADC

Parameter | Value
:---:|:---:
numSamples | 64
duration (s) | 0.0064
delay (s) | 1e-5

---

Fifth AddBlock Node - Delay 2

Event 1 - Delay

Parameter | Value
:---:|:---:
delay (s) | 0.004775

## 6. Contributing
Fork & PR!

## NOTES
- Click Off under each Event, and then proceed to configuring the appropriate events in each Node
- `ConfigSeq` should mandatorily be the first GPI Node in any pulse sequence
- `GenSeq` node should mandatorily be the last GPI Node in any pulse sequence
- If the canvas is yellow coloured, right click and uncheck ‘Pause’
- GPI Lab docs - http://docs.gpilab.com/en/develop/intro.html
