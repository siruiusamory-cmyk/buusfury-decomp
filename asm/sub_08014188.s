	CODE16
|sub_08014188|
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x74
	ADD      r5, r0, #0
	BNE      |sub_080141A0|
	LDR      r0, [pc, #0x278]
	BL       |GBARam_Malloc|
	ADD      r5, r0, #0
	BNE      |sub_080141A0|
	ADD      r0, r5, #0
	ADD      sp, #0x74
	POP      {r4, r5, r6, r7, pc}
