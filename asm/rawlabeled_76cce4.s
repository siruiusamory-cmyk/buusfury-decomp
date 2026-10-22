; PATH-100-004 / R-RAW-001: the census run 0x0876cce4..0x0877ae68 as LABELED RAW DATA.

	EXPORT	|unk_0876CCE4|
|unk_0876CCE4|
; no citation: the run's first byte, a label boundary only

	INCBIN	baserom.gba_0x76cce4_0x76dff8.extracted
	EXPORT	|unk_0876DFF8|
|unk_0876DFF8|
; cited by 0x08037F24 INDEXED base + register (r1, r1, r2) INDEXED base + register (r0, r0, r1) INDEXED base + register (r7, r0, r1)

	INCBIN	baserom.gba_0x76dff8_0x76e0b8.extracted
	EXPORT	|unk_0876E0B8|
|unk_0876E0B8|
; cited by 0x080383F0 ldr r7 +0x4 INDEXED base + register (r1, r1, r3) INDEXED base + register (r0, r0, r1), 0x080384AA ldr r0 +0x4, 0x080384F4 ldr r6 +0x4, 0x08038592 ldr r6 +0x8 ldr r6 +0x4 (+4 more sites)

	DCD	|unk_03003898|
	DCD	|unk_03001C4C|
	DCD	|unk_030019A4|
	EXPORT	|unk_0876E0C4|
|unk_0876E0C4|
; cited by 0x08038714

	INCBIN	baserom.gba_0x76e0c4_0x76e0dc.extracted
	EXPORT	|unk_0876E0DC|
|unk_0876E0DC|
; cited by 0x08052C4A ldr r0 +0x0

	INCBIN	baserom.gba_0x76e0dc_0x76e264.extracted
	EXPORT	|unk_0876E264|
|unk_0876E264|
; cited by 0x08038458 INDEXED base + register (r1, r1, r3) INDEXED base + register (r0, r0, r1) INDEXED base + register (r0, r0, r5) ldr r0 +0x4

	INCBIN	build\endrom\endrom_0076E264_0076E2F4.bin
	EXPORT	|unk_0876E2F4|
|unk_0876E2F4|
	INCBIN	baserom.gba_0x76e2f4_0x7703ac.extracted
	EXPORT	|unk_087703AC|
|unk_087703AC|
; cited by 0x08126D20 ldrh r0 +0x18

	INCBIN	baserom.gba_0x7703ac_0x770cf4.extracted
	EXPORT	|unk_08770CF4|
|unk_08770CF4|
; cited by 0x08038AA4 ldr r1 +0x8

	INCBIN	baserom.gba_0x770cf4_0x770d0c.extracted
	EXPORT	|unk_08770D0C|
|unk_08770D0C|
; cited by 0x080388EE INDEXED base + register (r3, r3, r6) INDEXED base + register (r0, r0, r5) ldr r1 +0x8 ldr r3 +0x4

	INCBIN	baserom.gba_0x770d0c_0x7710fc.extracted
	EXPORT	|unk_087710FC|
|unk_087710FC|
; cited by 0x0801A924

	INCBIN	baserom.gba_0x7710fc_0x77110c.extracted
	EXPORT	|unk_0877110C|
|unk_0877110C|
; cited by 0x08038E1E ldr r4 +0x0, 0x08038E7A ldr r0 +0x0

	INCBIN	baserom.gba_0x77110c_0x77ad10.extracted
	EXPORT	|unk_0877AD10|
|unk_0877AD10|
; cited by 0x08038B30 INDEXED base + register (r0, r0, r1) ldr r0 +0x0

	INCBIN	baserom.gba_0x77ad10_0x77add0.extracted
	EXPORT	|unk_0877ADD0|
|unk_0877ADD0|
; cited by 0x080390C8 ldr r4 +0x4 ldr r4 +0x0 INDEXED base + register (r1, r0, r1) INDEXED base + register (r0, r4, r0)

	DCD	|unk_03003898|
	DCD	|unk_03001C4C|
	EXPORT	|unk_0877ADD8|
|unk_0877ADD8|
; cited by 0x080391C0 INDEXED ldr [r2 + reg], 0x080391D0 INDEXED ldr [r3 + reg]

	INCBIN	baserom.gba_0x77add8_0x77ae58.extracted
	EXPORT	|unk_0877AE58|
|unk_0877AE58|
; cited by 0x0803928E ldm r0 +0x0 ldr r0 +0x0, 0x08039296 ldr r0 +0x0, 0x080392E4 ldr r0 +0x0


	INCBIN	baserom.gba_0x77ae58_0x77ae68.extracted
