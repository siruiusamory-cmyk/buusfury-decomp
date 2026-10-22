	CODE16
|sub_0804FCE2|
	LSL      r0, r0, #0
	LDR      r0, [r1]
	LDR      r1, [pc, #0xc]
	LDR      r1, [r1, #0x10]
	ADD      r1, #0xff
	ADD      r1, #0x81
	STR      r0, [r1, #0x1c]
	BX       lr
	LSL      r0, r0, #0
	ADR      r6, |loc_0804FFC8|
	LSR      r2, r6, #1
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	LDR      r2, [r0]
	LDR      r3, [r2]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r0, #0
	BX       lr
	LDR      r0, [pc, #0xc]
	LDR      r0, [r0, #0x14]
	ADD      r0, #0xff
	ADD      r0, #0x81
	LDR      r0, [r0, #0x10]
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	ADR      r6, |loc_0804FFF4|
	LSR      r2, r6, #1
	BX       lr
	LSL      r0, r0, #0
	LDR      r0, [pc, #0x1c]
	PUSH     {r4, lr}
	LDR      r0, [r0]
	ADD      r4, r1, #0
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r2, r0, #0
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |sub_08049168|
	POP      {r4, pc}
|sub_0804FD48|
|unk_0804FD48|
	INCBIN	baserom.gba_0x4fd48_0x4fd4a.extracted
