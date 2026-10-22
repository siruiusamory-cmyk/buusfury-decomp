	CODE16
|loc_0800C300|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0800C318|
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800C318|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
