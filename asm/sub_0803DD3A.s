|sub_0803DD3A|
	EXPORT |sub_0803DD3A|
	PUSH     {r4, r5, r6, lr}
	SUB      sp, #0x108
	ADD      r5, r0, #0
	ADD      r0, sp, #0x124
	ADD      r6, r1, #0
	STR      r0, [sp, #0x104]
	ADD      r4, sp, #4
	ADD      r0, r4, #0
	LDR      r1, [sp, #0x120]
	ADD      r2, sp, #0x104
	BL       |sub_0803DB7C|
	ADD      r2, r4, #0
	ADD      r1, r6, #0
	ADD      r0, r5, #0
	BL       |loc_0803DCC4|
	ADD      sp, #0x108
	POP      {r4, r5, r6}
	POP      {r3}
	ADD      sp, #0x10
	BX       r3
