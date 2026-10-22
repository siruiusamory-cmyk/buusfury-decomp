	CODE16
|sub_08048906|
	LSL      r0, r0, #0xc
	LDMIA    r3!, {r3, r4, r5}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BLT      |loc_08048900|
	LSR      r4, r0, #0x20
	ADD      r0, #0xe0
	LSL      r0, r0, #0xc
	LDMIA    r3!, {r5, r7}
	LSR      r4, r0, #0x20
