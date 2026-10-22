	CODE16
|sub_0800748C|
	PUSH     {r3, lr}
	MOV      r1, #0
	LDR      r0, [pc, #0x2c]
	BL       |sub_08012588|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080074AA|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
