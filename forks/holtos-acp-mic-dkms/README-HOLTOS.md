# holtos-acp-mic-dkms

Built-in microphones on the ASUS ROG Flow Z13 (GZ302EA, GZ302EAC) for HoltOS.

## The problem

The Z13's three built-in microphones are digital (PDM) microphones on the AMD
audio coprocessor 7 (PCI 1022:15e2, rev 0x70). The firmware's ACPI table
SSDT9 (OEM table id OEMACP) sets `acp-audio-config-flag` to 0x10
(`FLAG_AMD_LEGACY_ONLY_DMIC`), so the kernel picks the legacy ACP driver for
digital microphones only. Two other firmware details then hide them:

- `\_SB.PCI0.GPPA.ACP_._WOV` returns `WOVS`, which is 0 and never changed, and
  the kernel turns the PDM path off when `_WOV` returns 0;
- the PDM device `ACP_.PDMC` (`_ADR 0x02`) has no `_DSD` with
  `acp-audio-device-type`, which the kernel also requires.

The kernel then logs `acp_asoc_acp70.0: warning: No matching ASoC machine
driver found`, and the only input left is the Realtek ALC294's digital mic
pins (0x12, 0x13), which record only noise (tested on the Z13, 2026-09-15).

## The fix

`src/acp-legacy-common.c` is Linux v7.2.4's `sound/soc/amd/acp/acp-legacy-common.c`
(git.kernel.org stable, tag v7.2.4) with one HoltOS change in
`check_acp_config()`: on machines matching `holtos_acp_force_dmic_table`
(DMI sys_vendor "ASUS", board_name "GZ302EA"), a PDM device at the PDM address
counts as present without the property, and `_WOV` is ignored. It also logs
the ACP pin config value and the result, prefixed "HoltOS GZ302 microphone
quirk". `acp_machine_select()` then registers `acp-pdm-mach` as it does for
any `FLAG_AMD_LEGACY_ONLY_DMIC` machine. The upstream ThinkPad P14s Gen 6 AMD
fix (`acp_ignore_wov_table` in `ps/pci-ps.c`) uses the same approach.

The other files are unchanged v7.2.4 copies (`amd.h`, `acp_common.h`,
`chip_offset_byte.h`, `mach-config.h`), except the include path of
`mach-config.h` in `acp-legacy-common.c`. `Makefile.upstream` is the kernel's
own Makefile, kept for reference.

## Limits

- DKMS builds it only for 7.2 kernels (`BUILD_EXCLUSIVE_KERNEL="^7\.2\."`),
  because the copied headers describe 7.2's driver structures. On any other
  kernel the stock module loads and the microphones are hidden again: update
  these sources from that kernel's tag, or drop the package once upstream has
  a GZ302 quirk.
- It only works if the chip's pin config register reports a PDM layout
  (`is_pdm_config`); the log line shows the value.
- Undo: `pacman -R holtos-acp-mic-dkms`, then reboot.

The quirk should be sent upstream (linux-sound, ASoC AMD maintainers) so this
package can be removed.
