	CODE16
|sub_08048B7A|
	LSR      r4, r0, #0x20
	ADD      r2, #0x34
	LSL      r0, r0, #0xc
|loc_08048B80|
	BLS      |loc_08048BEC|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BLT      |loc_08048B30|
	LSR      r4, r0, #0x20
|loc_08048B98|
	ADD      r2, #0x3c
	LSL      r0, r0, #0xc
	LDMIA    r3!, {r4, r5, r6}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048BA8|
	DCW      0x3244
	DCW      0x0300,0xbd68
|loc_08048BAE|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048BBE|
|unk_08048BBE|
	INCBIN	baserom.gba_0x48bbe_0x48bc2.extracted
