	CODE16
|loc_0800B8FC|
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x28]
	LDR      r2, [r0, #0x14]
	ADD      r1, r1, r2
	MOV      r2, #0xf
	MVN      r2, r2
	CMP      r1, r2
	STR      r1, [r0, #0x28]
	BGE      |sub_0800B91A|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x338]
	LDR      r0, [r0, #8]
	BL       |loc_08011944|
	POP      {r3, pc}
