	CODE16
|sub_08029E5C|
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029E70|
	LDR      r1, [pc, #0xc]
	STR      r1, [r0]
	STR      r4, [r0, #0xc]
|loc_08029E70|
	POP      {r4, pc}
	LSL      r0, r0, #0
	LSL      r4, r5, #9
	LSR      r5, r6, #1
	STMIA    r6!, {r6}
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029E9C|
	LDR      r1, [pc, #0x24]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_08029E9C|
	POP      {r3, r4, r5, pc}
	MOV      r3, #0xff
	ADD      r3, #0xe5
	PUSH     {r4, lr}
	LDR      r3, [r3, r1]
	LDR      r4, [r0, #0xc]
	CMP      r3, r4
	BNE      |sub_08029EB6|
	LDR      r0, [r0, #0x10]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r4, pc}
