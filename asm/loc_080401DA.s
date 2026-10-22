	CODE16
|loc_080401DA|
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x44]
	LDR      r0, [r4, #4]
	STR      r0, [r4, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [pc, #0x30]
	ADD      r0, #8
	STR      r0, [r4, #4]
	POP      {r4, pc}
