# HoltOS: out-of-tree build of snd-pci-ps (Linux 7.2.4 source,
# sound/soc/amd/ps/pci-ps.c and ps-common.c) with the GZ302 microphone quirk,
# and snd-ps-pdm-dma (ps-pdm-dma.c) with the microphone clock test settings.
# DKMS calls the kernel build system with M= pointing here.
obj-m := snd-pci-ps.o snd-ps-pdm-dma.o
snd-pci-ps-y := pci-ps.o ps-common.o
snd-ps-pdm-dma-y := ps-pdm-dma.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(CURDIR) modules

clean:
	$(MAKE) -C $(KDIR) M=$(CURDIR) clean
