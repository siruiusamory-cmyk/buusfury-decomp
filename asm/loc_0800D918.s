	CODE16
|loc_0800D918|
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x14]
	SUB      sp, #0x44
	LDMIA    r0!, {r1, r2}
	MOV      r0, sp
	MOV      r5, sp
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r1, [sp, #0x24]
	LDR      r0, [r4, #0x14]
	LDR      r0, [r0, #0xc]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	MOV      r0, #0
	STR      r0, [sp, #0x34]
	STR      r0, [sp, #0x38]
	LDR      r0, [r4, #0x14]
	ADD      r2, sp, #0x34
	LDR      r1, [r0]
	LDR      r0, [r0, #4]
	STR      r1, [sp, #0x3c]
	STR      r0, [sp, #0x40]
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0x368]
	LSL      r0, r0, #5
	ADD      r1, r0, r1
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x3c
	MOV      r1, #0
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1e08
	ADD      sp, #0x44
	POP      {r4, r5, pc}
