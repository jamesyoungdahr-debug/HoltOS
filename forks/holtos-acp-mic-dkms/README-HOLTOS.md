# holtos-acp-mic-dkms

**Withdrawn 2026-09-15.** The 2.1 clock test on the Z13 recorded a flat line
(3-18 distinct values, pinned at -32768) for every combination:
`holtos_clk_ctrl` 0-7 and `holtos_clkdiv` 0-64. The chip's own values before
the driver runs were CLK_CTRL 0x1, CLKDIV 0xc0, MISC_CTRL 0x0, and the driver
set CLK_CTRL 0x7 and MISC_CTRL 0x18 as upstream does. The microphones get a
running clock but send no data: something Windows enables (microphone power
or pin routing through AMD's driver or DSP firmware) is missing on Linux. The
package was removed from both HoltOS package repositories, the dev hardware
rule and the stable model-extras switch were turned off, and the sources stay
here for when AMD or the kernel supports these microphones. Remove it with
`pacman -R holtos-acp-mic-dkms` and restart.

Built-in microphones on the ASUS ROG Flow Z13 (GZ302EA, GZ302EAC) for HoltOS.

## The problem

The Z13's three built-in microphones are digital (PDM) microphones on the AMD
audio coprocessor 7 (PCI 1022:15e2, rev 0x70). The firmware's ACPI table
SSDT9 (OEM table id OEMACP) sets `acp-audio-config-flag` to 0x10
(`FLAG_AMD_LEGACY_ONLY_DMIC`) and `acp-audio-zsc-enable` to 1. Two more
firmware details hide the microphones from Linux:

- `\_SB.PCI0.GPPA.ACP_._WOV` (wake on voice) returns `WOVS`, which is 0 and
  never changed; the kernel treats 0 as "no digital microphone";
- the PDM device `ACP_.PDMC` (`_ADR 0x02`) is empty: no `_DSD` with
  `acp-audio-device-type`, which the kernel also requires.

Without a fix the only input is the Realtek ALC294's digital mic pins (0x12,
0x13), which record only hiss (both tested on the Z13, 2026-09-15).

## Version 1 (legacy driver): did not work

Version 1 rebuilt `snd-acp-legacy-common` so `snd_acp_pci` ignored `_WOV`.
On the Z13 the quirk applied (pin config 0xa, pdm config 1, pdm device 1),
the `acp-pdm-mach` card appeared and the capture stream ran with interrupts,
but the recording was not audio: every sample non-zero, peaks at full scale,
played back as silence. The same result is reported upstream for the Acer
Nitro AN16S-61 (ACP 7.0, Realtek ALC245, linux-sound 2026-08, no fix yet).

The likely cause: on ACP 7 the legacy PDM path reads the capture ring buffer
at `ACP7x_DMIC_MEM_WINDOW_START` (0x4C00000), while `snd_pci_ps` uses
`PDM_MEM_WINDOW_START` (0x4000000) for every revision. The ASUS ACP 7.0
laptops with working microphones upstream (TUF A14 FA401EA, Zenbook S16
UM5606GA, in `acp70_acpi_flag_override_table`) run on `snd_pci_ps`.

## Version 2 (this package): snd_pci_ps

`src/pci-ps.c` and `src/ps-common.c` are Linux v7.2.4's
`sound/soc/amd/ps/pci-ps.c` and `ps-common.c` (git.kernel.org stable, tag
v7.2.4), `src/acp63.h` and `src/mach-config.h` unchanged copies, with HoltOS
changes in `pci-ps.c` only, on machines matching `holtos_ps_force_dmic_table`
(DMI sys_vendor "ASUS", board_name "GZ302EA"):

- the probe continues although `snd_amd_acp_find_config()` returns a flag;
- `get_acp63_device_config()` accepts the PDM device without the property
  and ignores `_WOV`, then logs "HoltOS GZ302 microphone quirk (snd_pci_ps)";
- the include path of `mach-config.h`.

`snd_pci_ps` reads pin config 0xa (`ACP_CONFIG_10`) as a PDM layout and, with
no SoundWire devices, registers the `acp_ps_mach` machine with the in-tree
`snd-ps-pdm-dma` and `snd-soc-ps-mach` modules.

`holtos-acp-mic.conf` (installed to /usr/lib/modprobe.d) blacklists
`snd_acp_pci`, which would otherwise claim the chip first because of the
firmware flag. The package is installed only on the GZ302 through the
hardware rules. `Makefile.upstream` is the kernel's ps/Makefile, kept for
reference.

## Version 2 on the Z13, and the 2.1 clock test

Version 2 works at the driver level on the Z13 (snd_pci_ps takes the chip,
"pdm config 1, pdm device 1", card `acp63`, the digital microphone is the
default input) but the recording is still flat: every sample -32768 (one
distinct value), with or without the microphone mute key. The PDM data line
carries no microphone signal, as in the Acer Nitro AN16S-61 report. Arch's
sof-firmware 2025.12.2 has no ACP 7.0 DSP firmware, and 7.2.4 knows a single
PDM block, so the remaining lead is the clock: `ACP_PDM_CLKDIV` (0x2C6C) is
never written by either driver.

Version 2.1 also rebuilds `snd-ps-pdm-dma` (v7.2.4 `ps-pdm-dma.c`) with two
test parameters read at every capture start, `holtos_clk_ctrl` (value for
`ACP_WOV_CLK_CTRL`, -1 = the driver's 7) and `holtos_clkdiv` (value for
`ACP_PDM_CLKDIV`, -1 = not written), and logs the register values before and
after ("HoltOS test"). With both at -1 nothing changes. `holtos-mic-test`
(installed to /usr/bin) runs a list of combinations, records 3 seconds each
through PipeWire and prints how many distinct sample values arrived. Values
are undocumented: this is trial and error. A restart resets the chip.

## Limits

- DKMS builds it only for 7.2 kernels (`BUILD_EXCLUSIVE_KERNEL="^7\.2\."`),
  because the copied headers describe 7.2's driver structures. On any other
  kernel the stock module loads and the microphones are hidden again: update
  these sources from that kernel's tag, or drop the package once upstream has
  a GZ302 quirk.
- `pdm_gain` (0-3, default 3) is a module parameter of the in-tree
  `snd-ps-pdm-dma` if the microphones turn out too quiet or too loud.
- Undo: `pacman -R holtos-acp-mic-dkms`, then reboot.

Once it works, the quirk should be sent upstream (linux-sound, ASoC AMD
maintainers) as a GZ302 entry in `acp70_acpi_flag_override_table` plus the
`_WOV` and property handling, so this package can be removed.
