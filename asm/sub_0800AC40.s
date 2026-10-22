	CODE16
|sub_0800AC40|
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x10]
	SUB      r1, #1
	STR      r1, [r0, #0x10]
	BNE      |sub_0800AC56|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x12c]
	LDR      r0, [r0]
	BL       |loc_08011944|
	POP      {r3, pc}
