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
---

## 1. Installing GPI Lab
1. Download v1 beta from - http://gpilab.com/downloads/
2. Typical installation on Mac (no guarantee for Windows)
---
## 2. Installing Pulseq for GPI Lab
1. Clone [repo](https://github.com/sravan953/pulseq-gpi)
2. Open GPI Lab
3. Click on `Config` > `Generate User Library`
4. Place the downloaded folder inside this auto-generated user library folder:
  Mac - `/Users/<user-name>/gpi/<user-name>/`
5. Place gre_GPI.net file in:
  Mac - `/Applications/GPI.app/Contents/Resources/miniconda/share/doc/gpi/Examples/`

> PRO TIP: With your Finder open, press `⌘ + Shift + G` and paste the path to jump to that location
---
## 3. Getting started
1. Open GPI Lab
2. Click on `Help` > `Examples`
3. Drag and drop the `gre_GPI.net` file onto the blank canvas
4. Configure the pulse sequence values by right clicking on the `ConfigSeq` and `AddBlock` nodes (refer Appendix for configuration values)
5. From left to right, click `Compute` events in each Node
6. Right click on the Matplotlib Node to view graphs
