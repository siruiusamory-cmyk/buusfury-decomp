	CODE16
|sub_08004D38|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0xbc]
	ADD      r4, r0, #0
	ADD      sp, r3
	BNE      |sub_08004D56|
	MOV      r0, #0xff
	ADD      r0, #0x81
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08004D56|
	ADD      r0, r4, #0
	LDR      r3, [pc, #0xa8]
	ADD      sp, r3
	POP      {r4, r5, r6, r7, pc}
