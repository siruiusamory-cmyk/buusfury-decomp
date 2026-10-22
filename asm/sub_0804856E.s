	CODE16
|sub_0804856E|
	LSL      r0, r0, #0xc
	LDR      r6, [sp, #0x270]
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	MOV      r1, #0
	STR      r1, [r0]
	STR      r1, [r0, #0xc]
	LDR      r1, [pc, #8]
	STR      r1, [r0, #8]
	BX       lr
	LSL      r0, r0, #0
	CMP      r3, #0xd8
	LSL      r0, r0, #0xc
	ADD      r4, r4, r5
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1, #8]
	ADD      r1, #0xff
	LDR      r0, [pc, #0xc]
	ADD      r1, #0x95
	STR      r0, [r1, #8]
	BX       lr
|sub_0804859C|
|unk_0804859C|
	INCBIN	baserom.gba_0x4859c_0x4859e.extracted
