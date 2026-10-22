	CODE16
|sub_0802C328|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
|sub_0802C33C|
|unk_0802C33C|
	INCBIN	baserom.gba_0x2c33c_0x2c340.extracted
|sub_0802C340|
	DCW      0xba00
	DCW      0xffff,0x4928
	LSR      r5, r6, #1
	BLS      |loc_0802C2EC|
	LSR      r7, r5, #1
	ADD      r0, #0x80
	LSL      r0, r0, #0xc
	ADD      r2, r1, #0
	ADD      r2, #0xff
	ADD      r0, #4
	ADD      r2, #0xa1
	LDMIA    r2!, {r3}
	STMIA    r0!, {r3}
	LDR      r2, [r2]
	STR      r2, [r0]
	MOV      r0, #0
	STRH     r0, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDRH     r0, [r1, #0x12]
	ADD      r6, r1, #0
	ADD      r4, r1, #0
	ADD      r0, #1
	SUB      sp, #0x18
	STRH     r0, [r1, #0x12]
	LSL      r0, r0, #0x1f
	BMI      |loc_0802C3BA|
	MOV      r0, #3
	BL       |inc_0x03d784_0x041118| + 0x2348
	SUB      r0, #1
	LSL      r0, r0, #8
	STR      r0, [sp, #0x10]
	MOV      r0, #3
	BL       |inc_0x03d784_0x041118| + 0x2348
	SUB      r0, #1
	LSL      r0, r0, #8
	STR      r0, [sp, #0x14]
	LDR      r2, [r5, #4]
	LDR      r3, [sp, #0x10]
	LDR      r1, [r5, #8]
	ADD      r2, r2, r3
	LDR      r3, [sp, #0x14]
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r1, r1, r3
	STR      r1, [sp, #4]
	ADD      r0, #0xa1
	ADD      r1, r2, #0
	STR      r2, [sp]
	LDR      r2, [sp, #4]
	STR      r1, [sp, #8]
	STR      r2, [sp, #0xc]
	STMIA    r0!, {r1}
	LDR      r1, [sp, #0xc]
	STR      r1, [r0]
|loc_0802C3BA|
	LDRH     r0, [r4, #0x12]
	CMP      r0, #0x40
	BNE      |loc_0802C3CE|
	LDR      r1, [r6]
	ADD      r0, r6, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0802C3CE|
	ADD      sp, #0x18
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r0, [r0, #4]
	ADD      r4, r1, #0
	LDR      r1, [r1, #0x14]
	SUB      sp, #0x24
	CMP      r1, r0
	BNE      |sub_0802C3E6|
	MOV      r0, #0
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
