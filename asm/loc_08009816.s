	CODE16
|loc_08009816|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	LDR      r2, [r2]
	LDR      r0, [r6, #4]
	SUB      sp, #0x24
	STR      r0, [sp, #0x18]
	ADD      r0, r2, #0
	STR      r2, [sp, #0x14]
	LDR      r2, [r3]
	ADD      r5, r3, #0
	ADD      r0, r0, r2
	LDR      r2, [sp, #0x18]
	LDR      r3, [r5, #4]
	STR      r0, [sp, #0xc]
	ADD      r2, r2, r3
	STR      r0, [sp, #0x1c]
	ADD      r7, r1, #0
	ADD      r7, #0x80
	STR      r2, [sp, #0x10]
	STR      r2, [sp, #0x20]
	LDR      r1, [r7, #0x28]
	ADD      r0, sp, #0x14
	ADD      r4, sp, #0x14
	BL       |loc_08009324|
	CMP      r0, #0
	BEQ      |sub_08009856|
	LDMIA    r4!, {r1, r2, r3, r4}
	LDR      r0, [sp, #0x24]
	STMIA    r0!, {r1, r2, r3, r4}
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
