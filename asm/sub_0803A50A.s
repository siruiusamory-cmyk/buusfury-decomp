	CODE16
|sub_0803A50A|
	MOV      r0, #0
	SUB      r0, r5, r0
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803A520|
	LDR      r1, [pc, #8]
	STR      r1, [r0]
|loc_0803A520|
	POP      {r3, pc}
	LSL      r0, r0, #0
	ADD      r2, #0xc8
	LSL      r0, r0, #0xc
	ADD      r3, sp, #0x50
	LSR      r4, r0, #0x20
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDRH     r1, [r1, #0x12]
	ADD      r1, #1
	LSL      r1, r1, #0x10
	LSR      r1, r1, #0x10
	STRH     r1, [r0, #0x12]
	LSR      r1, r1, #3
	CMP      r1, #4
	BNE      |sub_0803A552|
	BL       |inc_0x0158_0x143f2| + 0xed20
	POP      {r3, pc}
