	CODE16
|sub_0803D478|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803D494|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0803D494|
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	SUB      sp, #0x100
	LSR      r4, r0, #0x20
|loc_0803D4A0|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	LDRH     r0, [r0, #0x10]
	MVN      r1, r0
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x2ab8
	LDRH     r1, [r4, #2]
	MOV      r0, #0xf
	BIC      r0, r1
	BNE      |loc_0803D4C8|
	LDRB     r0, [r4, #1]
	CMP      r0, #0
	BEQ      |loc_0803D4C8|
	LDRH     r0, [r4, #4]
	LSL      r0, r0, #0x1c
	BEQ      |loc_0803D4C8|
	BL       |inc_0x03d784_0x041118| + 0x2288
|loc_0803D4C8|
	POP      {r4, pc}
|loc_0803D4CA|
	DCW      0x0000
	DCW      0x0120,0x0400
