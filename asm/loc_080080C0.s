	CODE16
|loc_080080C0|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r4, r0, #0
	BNE      |Irq_WriteEnable1|
	LDR      r0, [pc, #0x3c4]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |Irq_WriteEnable1|
	ADD      r0, r4, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
