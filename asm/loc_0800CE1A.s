	CODE16
|loc_0800CE1A|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0800CE32|
	MOV      r0, #0x60
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800CE32|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
