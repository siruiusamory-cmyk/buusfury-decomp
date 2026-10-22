	CODE16
|loc_08048868|
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BVC      |loc_080487D4|
	LSR      r4, r0, #0x20
	ADD      r0, #0xb0
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r3, r4, r5, r6, r7}
	LSR      r4, r0, #0x20
