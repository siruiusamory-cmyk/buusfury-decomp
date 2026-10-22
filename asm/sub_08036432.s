	CODE16
|sub_08036432|
	LSR      r4, r0, #0x20
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	ADR      r7, |loc_0803651C|
	LSR      r5, r6, #1
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08036454|
	MOV      r0, #0x9c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08036454|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
