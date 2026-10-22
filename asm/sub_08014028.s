	CODE16
|sub_08014028|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #0xc
	LDR      r5, [sp, #0x3c]
	LDR      r6, [sp, #0x40]
	LDR      r7, [sp, #0x44]
	ADD      r4, r0, #0
	BNE      |sub_08014046|
	MOV      r0, #0x3c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08014046|
	ADD      r0, r4, #0
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
