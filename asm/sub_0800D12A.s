	CODE16
|sub_0800D12A|
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [r0, #0x34]
	ADD      r5, r0, #0
	LDRH     r0, [r4, #0x16]
	LDR      r1, [pc, #0x7c]
	CMP      r0, r1
	BNE      |loc_0800D14E|
	LDR      r0, [r4, #0x34]
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x64]
	LDR      r0, [r0]
	BL       |loc_0801124C|
	STRH     r0, [r4, #0x16]
	ADD      r0, r4, #0
	BL       |sub_0800D026|
|loc_0800D14E|
	LDR      r1, [r5, #0x20]
	LDRH     r0, [r4, #0x16]
	LDRH     r1, [r1, #0x14]
	ADD      r0, r0, r1
	STRH     r0, [r5, #0x16]
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0800D172|
	MOV      r0, #0x38
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800D172|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
