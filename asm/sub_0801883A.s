	CODE16
|sub_0801883A|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #7
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	ADD      r4, #0xff
	ADD      r4, #0xc1
	STR      r0, [r4, #8]
	POP      {r4, pc}
	LSL      r0, r0, #0
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	CMP      r3, #0x98
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	ADD      r3, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x6c]
	ADD      r2, r2, r1
	LDR      r1, [r3, #4]
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0
	POP      {r3, pc}
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801888A|
	LDR      r1, [pc, #0x1c]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0801888A|
	POP      {r4, pc}
	PUSH     {r3, lr}
	ADD      r3, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x6c]
	ADD      r2, r2, r1
	LDR      r1, [r3, #0xc]
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	POP      {r3, pc}
	LSL      r0, r0, #0
	SUB      sp, #0xc0
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080188C8|
	LDR      r1, [pc, #0x2c]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_080188C8|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	ADD      r6, r2, #0
	LDR      r0, [r0, #0xc]
	BL       |inc_0x03d784_0x041118| + 0x235a
	CMP      r0, #0
	BEQ      |sub_080188EA|
	LDR      r0, [r4, #0x10]
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r4, r5, r6, pc}
