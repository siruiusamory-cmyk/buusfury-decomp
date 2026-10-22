	CODE16
|loc_08013E64|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	LDR      r5, [sp, #0x2c]
	LDR      r6, [sp, #0x30]
	LDR      r7, [sp, #0x34]
	ADD      r4, r0, #0
	BNE      |sub_08013E82|
	MOV      r0, #0x3c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08013E82|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
