	CODE16
|sub_08003CAC|
	ASR      r2, r2, #1
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	POP      {r4}
	BX       lr
	PUSH     {r3, lr}
	LDR      r3, [r1]
	LDRB     r2, [r3]
	ADD      r3, #1
	STR      r3, [r1]
	LSL      r1, r2, #2
	LDR      r2, [pc, #0x274]
	LDR      r1, [r2, r1]
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r3, [r1]
	LDRB     r2, [r3]
	ADD      r3, #1
	STR      r3, [r1]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LSL      r1, r2, #2
	LDR      r2, [pc, #0x258]
	LDR      r0, [r0, #4]
	LDR      r1, [r2, r1]
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
|sub_08003CF6|
|unk_08003CF6|
	INCBIN	baserom.gba_0x3cf6_0x3d10.extracted
