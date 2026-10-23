	CODE16
|sub_08039364|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0803937C|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0803937C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
