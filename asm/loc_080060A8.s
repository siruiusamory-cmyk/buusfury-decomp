	CODE16
|loc_080060A8|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #0xc
	LDR      r5, [sp, #0x44]
	LDR      r6, [sp, #0x48]
	LDR      r7, [sp, #0x4c]
	ADD      r4, r0, #0
	BNE      |sub_080060C6|
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080060C6|
	ADD      r0, r4, #0
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
