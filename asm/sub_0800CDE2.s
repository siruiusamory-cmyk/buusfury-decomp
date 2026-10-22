	CODE16
|sub_0800CDE2|
	LSL      r0, r0, #0
	SWI      0x4c
	LSR      r4, r0, #0x20
	BX       lr
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [r0, #0x5c]
	ADD      r5, r0, #0
	LDRH     r0, [r4, #0x16]
	LDR      r1, [pc, #0xf0]
	CMP      r0, r1
	BNE      |loc_0800CE0E|
	LDR      r0, [r4, #0x5c]
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0xe8]
	LDR      r0, [r0]
	BL       |loc_0801124C|
	STRH     r0, [r4, #0x16]
	ADD      r0, r4, #0
	BL       |sub_0800CD00|
|loc_0800CE0E|
	LDR      r1, [r5, #0x20]
	LDRH     r0, [r4, #0x16]
	LDRH     r1, [r1, #0x14]
	ADD      r0, r0, r1
	STRH     r0, [r5, #0x16]
	POP      {r3, r4, r5, pc}
