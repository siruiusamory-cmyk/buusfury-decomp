	CODE16
|sub_0800DFF2|
	MOV      r0, #0
	STRB     r0, [r1, #0x11]
|loc_0800DFF6|
	BX       lr
	LSL      r2, r2, #0x15
	LSR      r2, r2, #0x18
	STRB     r2, [r1, #0x11]
	CMP      r2, r0
	BLT      |loc_0800DFF6|
	MOV      r0, #0
	STRB     r0, [r1, #0x11]
	STRH     r0, [r1, #0x12]
	BX       lr
	PUSH     {r3, lr}
	LDRH     r2, [r1, #0x12]
	ADD      r2, #1
	LSL      r2, r2, #0x10
	LSR      r2, r2, #0x10
	STRH     r2, [r1, #0x12]
	CMP      r2, #0xa0
	BCC      |loc_0800E030|
	CMP      r2, #0xb0
	BCC      |sub_0800E02A|
	LDR      r2, [r0]
	LDR      r3, [r2, #0x24]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
