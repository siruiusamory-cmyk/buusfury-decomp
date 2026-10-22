	CODE16
|loc_08013914|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r3, #0x16
	LDRSH    r0, [r0, r3]
	CMP      r0, #0
	BNE      |sub_08013924|
	POP      {r3, r4, r5, r6, r7, pc}
