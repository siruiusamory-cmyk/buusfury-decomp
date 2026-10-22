	CODE16
|sub_080123A2|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	LDR      r1, [r0, #0x60]
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |sub_080123C0|
	LDR      r0, [pc, #0x30]
	LDR      r1, [r4, #4]
	LDR      r0, [r0, #4]
	BL       |loc_08011944|
	MOV      r0, #1
	POP      {r4, pc}
