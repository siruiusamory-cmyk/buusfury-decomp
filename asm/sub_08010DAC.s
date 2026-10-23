	CODE16
|sub_08010DAC|
	PUSH     {r3, lr}
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |sub_08010DBA|
	BL       |loc_0801064C|
	POP      {r3, pc}
