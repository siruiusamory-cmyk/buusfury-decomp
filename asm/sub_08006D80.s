	CODE16
|sub_08006D80|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0]
	ADD      r5, r1, #0
	BL       |loc_08010D9A|
	CMP      r5, #0
	BEQ      |loc_08006D96|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08006D96|
	POP      {r3, r4, r5, pc}
