	CODE16
|sub_08018BE2|
	LSR      r7, r5, #1
	STRH     r0, [r4, #4]
	LSR      r3, r5, #1
	LDMIA    r4!, {r0, r2, r3, r6, r7}
	MVN      r4, r1
	ADD      r1, pc, #0xE0
	LSR      r4, r0, #0x20
	LDR      r1, [r0, #4]
	CMP      r1, #0
	BNE      |loc_08018BFA|
	MOV      r0, #1
	BX       lr
|loc_08018BFA|
	SUB      r1, #1
	STR      r1, [r0, #4]
	BNE      |sub_08018C04|
	MOV      r0, #1
	BX       lr
