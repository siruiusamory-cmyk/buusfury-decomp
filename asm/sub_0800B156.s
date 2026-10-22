	CODE16
|sub_0800B156|
	LDR      r1, [r0, #0x50]
	ADD      r1, #1
	STR      r1, [r0, #0x50]
	CMP      r1, #8
	BLT      |loc_0800B184|
	LDR      r1, [r0, #0x24]
	MOV      r2, #1
	CMP      r1, #0
	BNE      |loc_0800B16A|
	STR      r2, [r0, #0x28]
|loc_0800B16A|
	LDR      r1, [r0, #0x14]
	LDRH     r3, [r1]
	CMP      r3, #0x5e
	BNE      |loc_0800B178|
	ADD      r1, #2
	STR      r1, [r0, #0x14]
	STR      r2, [r0, #0x28]
|loc_0800B178|
	LDR      r1, [r0, #0x14]
	STR      r1, [r0, #0x18]
	STR      r1, [r0, #0x10]
	LDR      r1, [pc, #0x194]
	ADD      r0, #0x80
	STR      r1, [r0, #0x34]
|loc_0800B184|
	MOV      r0, #0
	BX       lr
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #0x14
	ADD      r6, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r7, [sp, #0x3c]
	BNE      |sub_0800B1A6|
	MOV      r0, #0xb8
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800B1A6|
	ADD      r0, r4, #0
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
