	CODE16
|sub_08048A3A|
	LSL      r0, r0, #0xc
	LDR      r5, [sp, #0x2e0]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x10]
	LDR      r0, [pc, #0x14]
	STR      r0, [r1]
	LDR      r0, [pc, #0x14]
	ADD      r1, #8
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048A54|
|unk_08048A54|
	INCBIN	baserom.gba_0x48a54_0x48a56.extracted
