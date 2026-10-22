	CODE16
|sub_0803333C|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r4, #0xc
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08033352|
	LDR      r1, [pc, #0x54]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08033352|
	POP      {r4, pc}
	ADD      r2, r1, #0
	ADD      r1, r0, #0
	MOV      r0, #0x85
	LSL      r0, r0, #2
	ADD      r1, #0xc
	ADD      r2, r2, r0
	PUSH     {lr}
	SUB      sp, #0x6c
	MOV      r0, #0
	STR      r0, [sp]
	STR      r0, [sp, #0x44]
	MOV      r0, sp
	BL       |inc_0x0158_0x143f2| + 0x3ee0
	LDR      r0, [sp]
	CMP      r0, #1
	BNE      |sub_08033380|
	LDR      r0, [sp, #4]
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	ADD      sp, #0x6c
	POP      {pc}
