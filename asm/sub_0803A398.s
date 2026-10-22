	CODE16
|sub_0803A398|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDRH     r0, [r1, #0x12]
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x10
	BNE      |loc_0803A3DA|
|loc_0803A3AC|
	ADD      r0, r5, #0
	BL       |loc_0803A2FE|
	MOV      r1, #3
	STR      r0, [r5, #4]
	STRB     r1, [r0, #0x10]
	LDR      r6, [r5, #4]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803A3C8|
	LDR      r1, [pc, #0xc0]
	STR      r1, [r0]
|loc_0803A3C8|
	ADD      r7, r0, #0
	MOV      r1, #0x12
	ADD      r0, r6, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r7, #0
	ADD      r0, r6, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
|loc_0803A3DA|
	LDR      r0, [r5, #4]
	CMP      r0, #0
	BEQ      |loc_0803A3FE|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_0803A3FE|
	LDR      r0, [pc, #0x98]
	LDR      r1, [r5, #4]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	MOV      r0, #0
	STR      r0, [r5, #4]
|loc_0803A3FE|
	LDRH     r0, [r4, #0x12]
	LSL      r0, r0, #0x15
	LSR      r0, r0, #0x18
	STRB     r0, [r4, #0x11]
	LDR      r1, [r4, #0x50]
	LDR      r1, [r1]
	CMP      r1, r0
	BNE      |loc_0803A41C|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0803A41C|
	POP      {r3, r4, r5, r6, r7, pc}
|sub_0803A41E|
|unk_0803A41E|
		ADD r1, #0xff
		ADD r1, #0xc1
		PUSH {r4, r5, r6, lr}
		LDR r1, [r1, #0x30]
		MOV r6, #1
		ADD r1, #0xff
		ADD r1, #0xc1
		LDR r1, [r1, #0x38]
		ADD r1, #0xff
		ADD r1, #0xc1
		LDR r4, [r1, #0x38]
		LDR r1, [r0, #4]
		CMP r1, #0
		BNE      |loc_0803A45C|
		STR r6, [r0, #4]
		MOV r0, #8
		DCW     0xF003
		DCW     0xF8BB
		CMP r0, #0
		BEQ      |loc_0803A44A|
		LDR r1, [pc, #0x48]
		STR r1, [r0]
|loc_0803A44A|
		ADD r5, r0, #0
		MOV r1, #0x12
		ADD r0, r4, #0
		BL       |Record_SelectIndexed|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_0800ED18|
|loc_0803A45C|
		LDR r0, [r4, #0x58]
		ADD r0, #0x48
		LDR r0, [r0, #0x54]
		LDR r1, [r4, #0x50]
		CMP r0, r1
		BNE      |sub_0803A46C|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x52ae
