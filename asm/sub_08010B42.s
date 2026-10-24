	CODE16
|sub_08010B42|
	LSL      r0, r0, #0
	MOV      r7, #0xa0
	LSR      r7, r0, #0x20
	BVC      |loc_08010C04|
	LSR      r4, r0, #0x20
	STMIA    r7!, {r3, r5, r6}
	LSR      r4, r0, #0x20
	CMP      r3, #0xfc
	LSL      r0, r0, #0xc
	CMP      r3, #0xfd
	LSL      r0, r0, #0xc
	ASR      r0, r2, #0x20
	LSL      r0, r0, #0xc
	ASR      r0, r3, #0x20
	LSL      r0, r0, #0xc
	LDR      r5, [sp, #0x30]
	LSR      r1, r7, #1
	SUB      r4, r1, r4
	LSL      r0, r0, #0xc
	LDMIA    r1!, {r4, r5, r6, r7}
	LSR      r4, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	BGE      |loc_08010A88|
	LSR      r4, r0, #0x20
	LSR      r1, r5, #1
	LSR      r5, r0, #0x20
	LSL      r5, r6, #0x14
	LSR      r5, r0, #0x20
|loc_08010B80|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x3a0]
	ADD      r5, r1, #0
	LDR      r1, [pc, #0x3a0]
	STR      r0, [r4]
	MOV      r0, #0
	STR      r0, [r1]
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |Object_Destroy5|
	CMP      r5, #0
	BEQ      |loc_08010BB6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08010BB6|
	POP      {r3, r4, r5, pc}
|loc_08010BB8|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	MOV      r1, #1
	LSL      r1, r1, #9
	ADD      r4, r0, r1
	LDR      r0, [r4, #0x24]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	STR      r5, [r4, #0x24]
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	LDR      r0, [r0, #0x2c]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r0, r4, #0
	BL       |loc_0800EF08|
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	BL       |Battle_SpawnDamageObject|
	LDR      r0, [pc, #0x32c]
	LDR      r0, [r0, #4]
	CMP      r0, #0
	BNE      |loc_08010C10|
|loc_08010C04|
	ADD      r6, r5, #0
	LDR      r0, [r5, #0x18]
	ADD      r6, #0x18
	MOV      r7, #0
	CMP      r0, #0
	BNE      |sub_08010C14|
|loc_08010C10|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
