	CODE16
|sub_080072FA|
	LSL      r0, r0, #0
	LDR      r3, [sp, #0x310]
	LSR      r4, r0, #0x20
	LSL      r4, r7, #0x1e
	LSR      r7, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0800731C|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800731C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
