	CODE16
|sub_0800F668|
	STR      r3, [r5]
	LDR      r1, [r4, #0x18]
	MOV      r6, #0
	CMP      r1, #0
	BEQ      |loc_0800F67E|
	STR      r6, [sp, #4]
	STR      r6, [sp, #0x48]
	MOV      r2, #0
	ADD      r0, sp, #4
	BL       |loc_08004038|
|loc_0800F67E|
	LDR      r0, [r4, #0x1c]
	LDR      r1, [r0]
	BL       |inc_0x046118_0x049114| + 0x98a
	STR      r6, [r5]
	ADD      sp, #0xdc
	POP      {r4, r5, r6, r7, pc}
