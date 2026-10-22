	CODE16
|loc_0803DCC4|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	ADD      r6, r1, #0
	ADD      r4, r2, #0
	ADD      r1, r2, #0
	LDR      r0, [r0, #0xc]
	SUB      sp, #0x104
	BL       |sub_0803FFE8|
	CMP      r0, r6
	BGT      |sub_0803DCE6|
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |loc_0803DADA|
	ADD      sp, #0x104
	POP      {r4, r5, r6, r7, pc}
