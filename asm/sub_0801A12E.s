	CODE16
|sub_0801A12E|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	LDRB     r1, [r0, #0x15]
	LSL      r1, r1, #1
	ADD      r0, r1, r0
	ADD      r0, #0x2e
	LDRB     r5, [r0]
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801A154|
	LDR      r1, [pc, #0x1d8]
	STR      r1, [r0]
	STR      r5, [r0, #0x14]
	MOV      r1, #0
	STR      r1, [r0, #0xc]
	STR      r1, [r0, #0x10]
	STR      r1, [r0, #0x18]
|loc_0801A154|
	ADD      r5, r0, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
	LDR      r1, [pc, #0x1b8]
	LDR      r1, [r1]
	CMP      r1, #0
	BEQ      |loc_0801A174|
	MOV      r0, #0
	BX       lr
|loc_0801A174|
	LDR      r1, [pc, #0x198]
	LDR      r1, [r1, #0x14]
	LDR      r1, [r1, #0xc]
	CMP      r1, #0
	BNE      |loc_0801A182|
	MOV      r0, #0
	BX       lr
|loc_0801A182|
	LDRB     r0, [r0, #0x14]
	LDR      r1, [pc, #0x1a0]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	LDRB     r0, [r0]
	LSL      r0, r0, #0x1e
	LSR      r0, r0, #0x1f
	BEQ      |sub_0801A19A|
	MOV      r0, #0
	BX       lr
