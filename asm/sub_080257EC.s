	CODE16
|sub_080257EC|
	LDR      r1, [r0]
	LDR      r2, [r0, #8]
	MOV      r7, lr
	CMP      r1, r2
	BNE      |loc_080257FE|
	LDR      r2, [r0, #4]
	LDR      r3, [r0, #0xc]
	CMP      r2, r3
	BEQ      |loc_08025842|
|loc_080257FE|
	LDR      r2, [r7]
	STR      r2, [sp, #0xe4]
	LDR      r3, [r7, #8]
	CMP      r2, r3
	BNE      |sub_0802581C|
	LDR      r2, [r7, #4]
	LDR      r3, [r7, #0xc]
	CMP      r2, r3
	BNE      |sub_0802581C|
	LDMIA    r0!, {r1, r2, r3}
	STMIA    r7!, {r1, r2, r3}
	LDMIA    r0!, {r3}
	SUB      r0, #0x10
	STMIA    r7!, {r3}
	B        |loc_08025842|
