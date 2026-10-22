	CODE16
|sub_08048D72|
	LSL      r0, r0, #0xc
	BVC      |sub_08048D60|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048D80|
	DCW      0x32d0
	DCW      0x0300,0xb81c
|loc_08048D86|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D90|
|unk_08048D90|
	INCBIN	baserom.gba_0x48d90_0x48d92.extracted
