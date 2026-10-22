; PATH-100-005 / R-RAW-001: the census run 0x087122f8..0x0871e258 as LABELED RAW DATA.

	EXPORT	|unk_087122F8|
|unk_087122F8|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x7122f8_0x7129a5.extracted
	EXPORT	|unk_087129A5|
|unk_087129A5|
; cited by 0x082AA45A

	INCBIN	baserom.gba_0x7129a5_0x712fdc.extracted
	EXPORT	|unk_08712FDC|
|unk_08712FDC|
; cited by 0x08035A6E

	INCBIN	baserom.gba_0x712fdc_0x71370c.extracted
	EXPORT	|unk_0871370C|
|unk_0871370C|
; cited by 0x08027CFA INDEXED base + register (r0, r0, r1) INDEXED base + register (r1, r0, r1) INDEXED base + register (r0, r6, r0)

	INCBIN	baserom.gba_0x71370c_0x7137cc.extracted
	EXPORT	|unk_087137CC|
|unk_087137CC|
; cited by 0x08027D42

	INCBIN	baserom.gba_0x7137cc_0x7137d8.extracted
	EXPORT	|unk_087137D8|
|unk_087137D8|
; cited by 0x0800BB5C INDEXED ldr [r2 + reg] INDEXED base + register (r1, r1, r2) INDEXED ldr [r3 + reg] INDEXED base + register (r2, r2, r3)

	INCBIN	baserom.gba_0x7137d8_0x713ad8.extracted
	EXPORT	|unk_08713AD8|
|unk_08713AD8|
; cited by 0x0800BBD2 INDEXED ldrb [r1 + reg] INDEXED ldr [r2 + reg] INDEXED base + register (r1, r1, r2)

	INCBIN	baserom.gba_0x713ad8_0x713fd8.extracted
	EXPORT	|unk_08713FD8|
|unk_08713FD8|
; cited by 0x0800BB9E INDEXED ldrb [r1 + reg] INDEXED ldr [r3 + reg] INDEXED base + register (r2, r2, r3) INDEXED ldr [r2 + reg]

	INCBIN	baserom.gba_0x713fd8_0x714077.extracted
	EXPORT	|unk_08714077|
|unk_08714077|
; cited by 0x08110142

	INCBIN	baserom.gba_0x714077_0x7144d8.extracted
	EXPORT	|unk_087144D8|
|unk_087144D8|
; cited by 0x0800B57E INDEXED base + register (r1, r1, r2)

	INCBIN	baserom.gba_0x7144d8_0x7180e9.extracted
	EXPORT	|unk_087180E9|
|unk_087180E9|
; cited by 0x0864EE00 ldm r3 +0x0

	INCBIN	baserom.gba_0x7180e9_0x718249.extracted
	EXPORT	|unk_08718249|
|unk_08718249|
; cited by 0x0860CB7C

	INCBIN	baserom.gba_0x718249_0x7196d8.extracted
	EXPORT	|unk_087196D8|
|unk_087196D8|
; cited by 0x0805114E ldr r0 +0x0

	INCBIN	baserom.gba_0x7196d8_0x7196dc.extracted
	EXPORT	|unk_087196DC|
|unk_087196DC|
; cited by 0x0801957C ldr r0 +0x0

	INCBIN	baserom.gba_0x7196dc_0x7196e0.extracted
	EXPORT	|unk_087196E0|
|unk_087196E0|
; cited by 0x0805254A ldr r0 +0x0

	INCBIN	baserom.gba_0x7196e0_0x7198e4.extracted
	EXPORT	|unk_087198E4|
|unk_087198E4|
; cited by 0x080196E8 INDEXED ldr [r7 + reg] INDEXED base + register (r2, r2, r7) INDEXED base + register (r0, r0, r1)

	INCBIN  build\endrom\endrom_007198E4_00719C34.bin
	EXPORT	|unk_08719C34|
|unk_08719C34|
; cited by 0x080519A6 ldr r0 +0x4

	DCD	|unk_03003898|
	DCD	|unk_03001C4C|
	DCD	|unk_030019A4|
	EXPORT	|unk_08719C40|
|unk_08719C40|
; cited by 0x08019800 INDEXED ldr [r2 + reg] INDEXED base + register (r0, r0, r2) ldr r0 +0x0 INDEXED base + register (r1, r0, r1), 0x08019826 ldr r0 +0x0 INDEXED base + register (r1, r0, r1) INDEXED base + register (r0, r6, r0), 0x0801985A ldr r4 +0x4, 0x0801988A ldr r6 +0x4 (+3 more sites)

	INCBIN	baserom.gba_0x719c40_0x719c60.extracted
	EXPORT	|unk_08719C60|
|unk_08719C60|
; cited by 0x08051E74 ldr r0 +0x0

	INCBIN	baserom.gba_0x719c60_0x71b050.extracted
	EXPORT	|unk_0871B050|
|unk_0871B050|
; cited by 0x0828294C

	INCBIN	baserom.gba_0x71b050_0x71b1a6.extracted
	EXPORT	|unk_0871B1A6|
|unk_0871B1A6|
; cited by 0x084E5DF0

	INCBIN	baserom.gba_0x71b1a6_0x71da68.extracted
	EXPORT	|unk_0871DA68|
|unk_0871DA68|
; cited by 0x08033056

	INCBIN	baserom.gba_0x71da68_0x71da88.extracted
	EXPORT	|unk_0871DA88|
|unk_0871DA88|
; cited by 0x0803C11E

	INCBIN	baserom.gba_0x71da88_0x71da98.extracted
	EXPORT	|unk_0871DA98|
|unk_0871DA98|
; cited by 0x0801A60A ldr r1 +0x14

	INCBIN	baserom.gba_0x71da98_0x71daf8.extracted
	EXPORT	|unk_0871DAF8|
|unk_0871DAF8|
; cited by 0x080135A4

	INCBIN	baserom.gba_0x71daf8_0x71dd38.extracted
	EXPORT	|unk_0871DD38|
|unk_0871DD38|
; cited by 0x0805242A ldr r0 +0x4

	DCD	|unk_03003898|
	DCD	|unk_03001C4C|
	DCD	|unk_03001068|
	DCD	|unk_030019A4|
	DCD	|unk_03002A64|
	EXPORT	|unk_0871DD4C|
|unk_0871DD4C|
; cited by 0x0801A678 INDEXED base + register (r5, r0, r1) ldr r0 +0x4, 0x0801A6AC ldr r0 +0x4, 0x0801A708 INDEXED base + register (r2, r0, r1), 0x0801A7D8 INDEXED base + register (r2, r0, r1) INDEXED base + register (r3, r0, r1) ldr r0 +0x4 (+3 more sites)

	INCBIN	baserom.gba_0x71dd4c_0x71ddc8.extracted
	EXPORT	|unk_0871DDC8|
|unk_0871DDC8|
; cited by 0x0801A904 INDEXED base + register (r5, r0, r1) ldr r0 +0x4, 0x0801A938 ldr r0 +0x4, 0x0801A9A0 INDEXED base + register (r2, r0, r1) ldr r0 +0x4, 0x0801A9C0 ldr r0 +0x4 INDEXED base + register (r2, r0, r1) (+5 more sites)

	INCBIN	baserom.gba_0x71ddc8_0x71de74.extracted
	EXPORT	|unk_0871DE74|
|unk_0871DE74|
; cited by 0x0801AD56 INDEXED base + register (r2, r0, r1) ldr r0 +0x4, 0x0801ADBC INDEXED base + register (r5, r0, r1) INDEXED base + register (r2, r0, r1) ldr r0 +0x4

	INCBIN	baserom.gba_0x71de74_0x71dec4.extracted
	EXPORT	|unk_0871DEC4|
|unk_0871DEC4|
; cited by 0x0801AE6E INDEXED base + register (r2, r0, r1) INDEXED ldr [r1 + reg], 0x0801AE9A INDEXED ldr [r1 + reg]

	INCBIN	baserom.gba_0x71dec4_0x71df70.extracted
	EXPORT	|unk_0871DF70|
|unk_0871DF70|
; cited by 0x0801B30E INDEXED base + register (r2, r0, r1) ldr r0 +0x4 INDEXED ldr [r2 + reg], 0x0801B364 INDEXED ldr [r2 + reg] INDEXED base + register (r1, r0, r1) ldr r0 +0x4, 0x0801B388 INDEXED base + register (r1, r0, r1) ldr r0 +0x4 INDEXED ldr [r1 + reg], 0x0801B392 INDEXED base + register (r1, r0, r1) ldr r0 +0x4 INDEXED ldr [r1 + reg] INDEXED base + register (r1, r2, r1) (+1 more sites)

	INCBIN	baserom.gba_0x71df70_0x71df9c.extracted
	EXPORT	|unk_0871DF9C|
|unk_0871DF9C|
; cited by 0x0801B564 INDEXED base + register (r2, r0, r1) ldr r6 +0x0 INDEXED base + register (r0, r0, r2) ldr r6 +0x4, 0x0801B5AA INDEXED ldr [r1 + reg], 0x0801B64A INDEXED base + register (r5, r0, r2) INDEXED base + register (r0, r0, r2) ldr r4 +0x4 ldr r4 +0x0, 0x0801B74A INDEXED base + register (r2, r0, r1) ldr r0 +0x4 INDEXED ldr [r1 + reg] (+1 more sites)

	INCBIN	baserom.gba_0x71df9c_0x71e024.extracted
	EXPORT	|unk_0871E024|
|unk_0871E024|
; cited by 0x0801B946 INDEXED base + register (r0, r0, r1), 0x0801BA32 INDEXED base + register (r2, r0, r1) ldr r0 +0x4

	INCBIN	baserom.gba_0x71e024_0x71e0a4.extracted
	EXPORT	|unk_0871E0A4|
|unk_0871E0A4|
; cited by 0x0801BB64 INDEXED ldr [r2 + reg], 0x0801BD1C INDEXED base + register (r7, r0, r1) ldr r0 +0x4 INDEXED base + register (r1, r0, r1)

	INCBIN	baserom.gba_0x71e0a4_0x71e0f8.extracted
	EXPORT	|unk_0871E0F8|
|unk_0871E0F8|
; cited by 0x0801BDE8 INDEXED base + register (r5, r0, r1) INDEXED base + register (r2, r0, r1) ldr r0 +0x4, 0x0801BE7C INDEXED base + register (r2, r0, r1) INDEXED ldr [r1 + reg], 0x0801BEAA INDEXED ldr [r1 + reg], 0x0801BF52 INDEXED base + register (r5, r0, r1) INDEXED base + register (r2, r0, r1) ldr r0 +0x4 (+2 more sites)

	INCBIN	baserom.gba_0x71e0f8_0x71e1b0.extracted
	EXPORT	|unk_0871E1B0|
|unk_0871E1B0|
; cited by 0x0801C0CE INDEXED base + register (r6, r0, r1) INDEXED base + register (r2, r0, r1)

	INCBIN	baserom.gba_0x71e1b0_0x71e1e0.extracted
	EXPORT	|unk_0871E1E0|
|unk_0871E1E0|
; cited by 0x0801C67A INDEXED base + register (r2, r0, r1) ldr r0 +0x4

	INCBIN	baserom.gba_0x71e1e0_0x71e200.extracted
	EXPORT	|unk_0871E200|
|unk_0871E200|
; cited by 0x0805118A ldr r0 +0x4

	INCBIN	baserom.gba_0x71e200_0x71e228.extracted
	EXPORT	|unk_0871E228|
|unk_0871E228|
; cited by 0x080511DE ldr r0 +0x4

	DCD	|unk_03003898|
	DCD	|unk_03001C4C|
	DCD	|unk_030019A4|
	EXPORT	|unk_0871E234|
|unk_0871E234|
; cited by 0x0801C92A INDEXED base + register (r0, r0, r1) INDEXED ldr [r3 + reg] INDEXED base + register (r0, r0, r3) ldr r0 +0x0, 0x0801C95C ldr r0 +0x0 INDEXED base + register (r0, r0, r5) ldr r4 +0x4, 0x0801C984 ldr r4 +0x4, 0x0801C9DE ldr r0 +0x4 (+2 more sites)

	INCBIN	baserom.gba_0x71e234_0x71e254.extracted
	EXPORT	|unk_0871E254|
|unk_0871E254|
; cited by 0x0801CF16 INDEXED base + register (r1, r1, r2) ldr r0 +0x0 INDEXED base + register (r0, r0, r5)


	INCBIN	baserom.gba_0x71e254_0x71e258.extracted
