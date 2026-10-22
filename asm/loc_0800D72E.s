	CODE16
|loc_0800D72E|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	LDR      r5, [pc, #0x144]
	ADD      r1, r0, #0
	LDR      r4, [r0, #0x48]
	LDR      r0, [r5]
	BL       |loc_08011944|
	CMP      r4, #0
	BLT      |loc_0800D754|
	MOV      r0, #0x34
	LDR      r1, [pc, #0x138]
	MUL      r0, r4
	ADD      r0, r0, r1
	ADD      r2, r6, #0
	ADD      r1, r4, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0x1d72
	POP      {r4, r5, r6, pc}
