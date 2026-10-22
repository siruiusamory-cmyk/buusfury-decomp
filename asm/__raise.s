	CODE16
|__raise|
	PUSH     {r4, r5, r6, lr}
	LDR      r6, [pc, #0x38]
	ADD      r5, r1, #0
	ADD      r1, r0, #0
	ADD      r4, r0, #0
	ADD      r6, pc
	ADD      r0, r6, #0
	BL       |loc_08048006|
|loc_08048006|
	ADD      r2, r0, #0
	CMP      r0, r6
	BNE      |sub_0804801A|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |__default_signal_handler|
	POP      {r4, r5, r6}
	POP      {r3}
	BX       r3
