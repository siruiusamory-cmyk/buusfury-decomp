	CODE16
|loc_08047F84|
	CMP      r0, #0
	BEQ      |sub_08047F94|
	ADD      r1, sp, #4
	LDMIA    r1!, {r0, r1}
	ADD      sp, #0x1c
	POP      {r4, r5}
	POP      {r3}
	BX       r3
