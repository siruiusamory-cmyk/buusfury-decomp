	CODE16
|loc_0800CEF4|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r2, #0
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_0800CF08|
	MOV      r0, #0x34
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800CF40|
|loc_0800CF08|
	LDR      r1, [pc, #0x290]
	MOV      r6, #0
	STR      r1, [r0]
	LDR      r1, [pc, #0x290]
	STR      r6, [r0, #0xc]
	STR      r1, [r0]
	STR      r4, [r0, #0x20]
	STR      r0, [r0, #0x10]
	ADD      r7, r0, #0
	ADD      r7, #0x24
	LDMIA    r4!, {r1, r2, r3}
	STMIA    r7!, {r1, r2, r3}
	LDMIA    r4!, {r3}
	SUB      r4, #0x10
	STMIA    r7!, {r3}
	LDR      r1, [r0, #0x20]
	LDRB     r2, [r1, #0x16]
	STRB     r2, [r0, #8]
	LDR      r2, [r4, #0xc]
	STR      r2, [r0, #4]
	LDRB     r1, [r1, #0x17]
	MOV      r2, #1
	CMP      r1, #0
	BNE      |loc_0800CF3A|
	MOV      r2, #0
|loc_0800CF3A|
	STR      r2, [r0, #0x1c]
	STRH     r5, [r0, #0x14]
	STR      r6, [r0, #0x18]
|loc_0800CF40|
	POP      {r3, r4, r5, r6, r7, pc}
	LDR      r1, [r0, #0x1c]
	CMP      r1, #0
	BNE      |loc_0800CF4C|
	MOV      r0, #0
	BX       lr
|loc_0800CF4C|
	LDR      r1, [pc, #0x254]
	LDR      r2, [r0, #0x24]
	LDR      r1, [r1, #4]
	ADD      r1, #0x18
	LDR      r3, [r1, #8]
	CMP      r2, r3
	BGE      |sub_0800CF76|
	LDR      r2, [r1]
	LDR      r3, [r0, #0x2c]
	CMP      r2, r3
	BGE      |sub_0800CF76|
	LDR      r2, [r0, #0x28]
	LDR      r3, [r1, #0xc]
	CMP      r2, r3
	BGE      |sub_0800CF76|
	LDR      r1, [r1, #4]
	LDR      r0, [r0, #0x30]
	CMP      r1, r0
	BGE      |sub_0800CF76|
	MOV      r0, #1
	BX       lr
