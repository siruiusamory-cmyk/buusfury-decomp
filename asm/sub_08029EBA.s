	CODE16
|sub_08029EBA|
	LSL      r0, r0, #0
	LDMIA    r3!, {r4, r5, r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0x10]
	BX       lr
	ADD      r0, r1, #0
	ADD      r0, #0xff
	ADD      r0, #0xc1
	LDR      r1, [r0, #0x24]
	ADD      r1, #1
	STR      r1, [r0, #0x24]
	MOV      r0, #0
	BX       lr
|sub_08029ED4|
|unk_08029ED4|
	INCBIN	baserom.gba_0x29ed4_0x29ed6.extracted
