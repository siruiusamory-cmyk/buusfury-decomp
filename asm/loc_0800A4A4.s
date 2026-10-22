	CODE16
|loc_0800A4A4|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0800A4BC|
	MOV      r0, #0x58
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800A4BC|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
