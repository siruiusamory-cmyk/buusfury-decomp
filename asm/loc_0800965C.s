	CODE16
|loc_0800965C|
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x298]
	ADD      r1, r0, #0
	LDR      r0, [r4]
	BL       |loc_080092BC|
	LDR      r0, [r4, #4]
	BL       |loc_08009CC2|
	POP      {r4, pc}
