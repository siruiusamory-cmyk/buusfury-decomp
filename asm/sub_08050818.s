	CODE16
|sub_08050818|
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	BLE      |loc_08050890|
	LSR      r1, r6, #1
|unk_08050820|
	INCBIN	baserom.gba_0x50820_0x50822.extracted
|dat_08050822|
	DCW      0x0804
	DCW      0x0000
	DCW      0x0601
	DCW      0xca80
	DCW      0x0804