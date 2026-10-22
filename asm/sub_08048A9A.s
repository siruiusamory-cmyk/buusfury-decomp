	CODE16
|sub_08048A9A|
	LSL      r0, r0, #0xc
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048AA4|
	DCW      0x31f8
	DCW      0x0300,0xbd78
|loc_08048AAA|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048AB4|
|unk_08048AB4|
	INCBIN	baserom.gba_0x48ab4_0x48ab6.extracted
