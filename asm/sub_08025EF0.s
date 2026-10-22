	CODE16
|sub_08025EF0|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x28c]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0x1c]
	CMP      r0, #0
	BEQ      |loc_08025F06|
	MOV      r1, #1
	BL       |inc_0x03d784_0x041118| + 0x1e08
|loc_08025F06|
	LDR      r0, [pc, #0x28c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08025F14|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08025F14|
	POP      {r3, r4, r5, pc}
|loc_08025F16|
	PUSH     {r4, lr}
	LDR      r2, [r0, #0x14]
	ADD      r4, r0, #0
	ADD      r2, #0x38
	MOV      r1, #0x68
	MOV      r0, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r1, [pc, #0x260]
	STR      r0, [r4, #0x1c]
	LDR      r1, [r1, #0xc]
	STR      r1, [r0, #0xc]
	LDR      r1, [r4, #0x1c]
	MOV      r0, #2
	STRB     r0, [r1, #3]
	LDR      r0, [r4, #0x1c]
	MOV      r1, #0
	STR      r1, [r0, #4]
	MOV      r1, #0xe
	STR      r1, [r0, #8]
	LDR      r1, [r4, #0x1c]
	MOV      r0, #0x10
	STRB     r0, [r1, #1]
	LDR      r0, [r4, #0x1c]
	MOV      r1, #0
	LDR      r2, [r0, #0x30]
	LDR      r0, [r0, #0x24]
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r4, #0x20]
	LDR      r1, [pc, #0x23c]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #2
	LDR      r2, [r1, r0]
	LDR      r0, [r4, #0x1c]
	MOV      r1, #0x68
	BL       |inc_0x03d784_0x041118| + 0x5e2
	POP      {r4, pc}
|sub_08025F64|
|unk_08025F64|
		BX       lr
