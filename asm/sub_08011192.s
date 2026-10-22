	CODE16
|sub_08011192|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r1, r0, #0
	ADD      r0, #0xff
	ADD      r0, #0xb1
	BL       |loc_0800A95A|
	ADD      r0, r4, #0
	BL       |loc_0800EF08|
	POP      {r4, pc}
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0xc]
	SUB      sp, #4
	BL       |sub_08000158|
	ADD      r6, r0, #0
	ADD      r7, r4, #0
	ADD      r5, r4, #0
	ADD      r5, #8
	ADD      r7, #0x10
	MOV      r0, #0xff
	ADD      r0, #0xbd
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080111D0|
	ADD      r0, r4, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
