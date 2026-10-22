	CODE16
|sub_0802D08C|
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802D0A8|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	MOV      r1, #0
	STR      r1, [r0, #8]
|loc_0802D0A8|
	POP      {r4, pc}
	LSL      r0, r0, #0
	STMIA    r6!, {r4, r5, r6}
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0
	STRH     r1, [r4, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r4, #8]
	STRB     r1, [r4, #0x11]
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r0, [pc, #0x10c]
	MOV      r2, #0
	MOV      r1, #0x24
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x11b72
	CMP      r0, #0xc
	BLT      |loc_0802D0DA|
	MOV      r0, #0x18
	STRH     r0, [r4, #0x12]
|loc_0802D0DA|
	POP      {r4, pc}
	PUSH     {r4, r5, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x1c
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x18
	BCC      |sub_0802D102|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
