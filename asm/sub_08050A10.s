	CODE16
|sub_08050A10|
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050A1E|
	BL       |GBARam_Free|
|loc_08050A1E|
	POP      {r3, pc}
