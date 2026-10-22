	CODE16
|sub_0802A006|
	LSL      r0, r0, #0xc
	LDR      r5, [sp, #0x3c0]
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0xac]
	PUSH     {r4, lr}
	LDR      r3, [r2]
	CMP      r3, #0
	BEQ      |loc_0802A026|
	ADD      r3, #0xff
	ADD      r3, #0xa1
	LDMIA    r3!, {r4}
	STR      r4, [r0, #0x1c]
	LDR      r3, [r3]
	STR      r3, [r0, #0x20]
	BL       |inc_0x351c0_0x3d4d0| + 0x6940
|loc_0802A026|
	POP      {r4, pc}
	LDR      r2, [pc, #0x90]
	PUSH     {r4, r5, lr}
	LDR      r2, [r2]
	SUB      sp, #0x1c
	CMP      r2, #0
	BNE      |sub_0802A03A|
	MOV      r0, #0
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
