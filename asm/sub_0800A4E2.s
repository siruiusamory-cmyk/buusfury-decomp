	CODE16
|sub_0800A4E2|
	LSR      r4, r0, #0x20
	LSL      r7, r7, #0x1f
	LSL      r0, r0, #0
	ASR      r0, r6, #0x1b
	LSR      r7, r0, #0x20
	BHI      |loc_0800A580|
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x48]
	LDR      r2, [r0, #0x38]
	CMP      r1, r2
	BGT      |loc_0800A512|
	LDR      r1, [r0, #0x4c]
	LDR      r2, [r0, #0x3c]
	CMP      r1, r2
	BGT      |loc_0800A512|
	LDR      r1, [r0, #0x50]
	LDR      r2, [r0, #0x40]
	CMP      r1, r2
	BLT      |loc_0800A512|
	LDR      r1, [r0, #0x54]
	LDR      r2, [r0, #0x44]
	CMP      r1, r2
	BGE      |sub_0800A516|
|loc_0800A512|
	MOV      r0, #0
	POP      {r3, pc}
