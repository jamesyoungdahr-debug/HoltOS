# HoltOS: out-of-tree build of snd-acp-legacy-common (Linux 7.2.4 source,
# sound/soc/amd/acp/acp-legacy-common.c) with the GZ302 microphone quirk.
# DKMS calls the kernel build system with M= pointing here.
obj-m := snd-acp-legacy-common.o
snd-acp-legacy-common-y := acp-legacy-common.o

KDIR ?= /lib/modules/$(shell uname -r)/build

all:
	$(MAKE) -C $(KDIR) M=$(CURDIR) modules

clean:
	$(MAKE) -C $(KDIR) M=$(CURDIR) clean
