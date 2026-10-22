	CODE16
|sub_08035FD2|
	CMP      r0, #2
	BNE      |loc_08035FDA|
	MOV      r3, #0
	STR      r3, [r2, #0xc]
|loc_08035FDA|
	LDR      r2, [r1, #0x50]
	LDR      r2, [r2]
	CMP      r2, r0
	BGT      |sub_08035FF2|
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
