	CODE16
|sub_0803B6D4|
	LDR      r2, [sp, #0x24]
	STR      r2, [r1]
	LDR      r1, [sp, #0x28]
	STR      r1, [r0]
	LDR      r1, [sp, #0x54]
	MOV      r0, #1
	STR      r0, [r1, #0x14]
	ORR      r5, r6
	ADD      r0, r5, #0
	ADD      sp, #0x64
	POP      {r4, r5, r6, r7, pc}
