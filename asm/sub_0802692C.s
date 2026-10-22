	CODE16
|sub_0802692C|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08026948|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08026948|
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	ADD      r1, pc, #0x80
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_08026966|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802697C|
|loc_08026966|
	LDR      r1, [pc, #0x1c8]
	LDR      r3, [pc, #0x1c8]
	STR      r1, [r0]
	LDR      r1, [r4]
	MUL      r1, r3
	ASR      r1, r1, #8
	STR      r1, [r0, #4]
	LDR      r1, [r4, #4]
	MUL      r1, r3
	ASR      r1, r1, #8
	STR      r1, [r0, #8]
|loc_0802697C|
	POP      {r4, pc}
	PUSH     {r3, lr}
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	ADD      r0, r1, #0
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	STRB     r2, [r0, #0x11]
	MOV      r1, #0x12
	BL       |inc_0x0158_0x143f2| + 0xeb82
	POP      {r3, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x18
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x18
	BCC      |sub_080269BC|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
