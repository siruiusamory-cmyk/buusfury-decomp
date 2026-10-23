	CODE16
|sub_080077EC|
	PUSH     {lr}
	SUB      sp, #0x24
	LDR      r1, [r0, #4]
	ADD      r0, sp, #0x14
	BL       |Object_WriteBounds1|
	LDR      r0, [pc, #0x58]
	LDR      r1, [r0]
	LDR      r2, [r1]
	LDR      r1, [r1, #4]
	STR      r2, [sp, #0xc]
	STR      r1, [sp, #0x10]
	LDR      r1, [sp, #0x14]
	LDR      r2, [sp, #0x1c]
	ADD      r1, r1, r2
	LSR      r2, r1, #0x1f
	ADD      r1, r2, r1
	ASR      r1, r1, #1
	SUB      r1, #0x78
	LSL      r1, r1, #0xa
	STR      r1, [sp, #4]
	LDR      r1, [sp, #0x18]
	LDR      r2, [sp, #0x20]
	ADD      r1, r1, r2
	LSR      r2, r1, #0x1f
	ADD      r1, r2, r1
	ASR      r1, r1, #1
	SUB      r1, #0x54
	LSL      r1, r1, #0xa
	STR      r1, [sp, #8]
	LDR      r1, [sp, #4]
	LDR      r2, [sp, #0xc]
	SUB      r1, r1, r2
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	ASR      r1, r1, #6
	ADD      r1, r1, r2
	STR      r1, [sp, #0xc]
	LDR      r1, [sp, #8]
	LDR      r2, [sp, #0x10]
	SUB      r1, r1, r2
	LSL      r3, r1, #3
	ADD      r1, r3, r1
	ASR      r1, r1, #7
	ADD      r1, r1, r2
	STR      r1, [sp, #0x10]
	LDR      r0, [r0]
	ADD      r1, sp, #0xc
	BL       |loc_08009744|
	ADD      sp, #0x24
	POP      {pc}
|sub_08007854|
|unk_08007854|
	INCBIN	baserom.gba_0x7854_0x7856.extracted
|sub_08007856|
	DCW      0x0807
