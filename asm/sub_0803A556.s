	CODE16
|sub_0803A556|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r1, #0
	LDR      r1, [r0, #4]
	MOV      r5, #1
	CMP      r1, #0
	LDR      r6, [pc, #0x34]
	BNE      |loc_0803A576|
	MOV      r1, #0x13
	STR      r5, [r0, #4]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r6, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
|loc_0803A576|
	LDR      r1, [r4, #0x14]
	ADD      r0, r5, #0
	CMP      r1, r6
	BEQ      |loc_0803A580|
	MOV      r0, #0
|loc_0803A580|
	SUB      r0, r5, r0
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803A594|
	LDR      r1, [pc, #8]
	STR      r1, [r0]
|loc_0803A594|
	POP      {r3, pc}
	LSL      r0, r0, #0
	ADD      r2, #0xcc
	LSL      r0, r0, #0xc
	STMIA    r2!, {r2, r3, r5}
	LSR      r4, r0, #0x20
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r4, lr}
	LDRH     r0, [r1, #0x12]
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	LDR      r1, [r1, #0x50]
	LSR      r0, r0, #3
	LDR      r1, [r1]
	CMP      r1, r0
	BNE      |sub_0803A5D6|
	MOV      r1, #0x14
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x5c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
