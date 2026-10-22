	CODE16
|sub_0803F876|
	LDR      r0, [r0]
	LDR      r2, [sp, #0x108]
	MOV      r1, ip
	LSR      r0, r2
	LDR      r2, [sp, #0x104]
	ADD      r1, #1
	AND      r0, r2
	LDR      r2, [sp, #0x10c]
	ADD      r7, #1
	CMP      r1, r2
	MOV      ip, r1
	BLT      |loc_0803F834|
	LDR      r0, [r6]
	ADD      r0, r0, r5
	ADD      r0, #1
	STR      r0, [r6]
	ADD      sp, #0x134
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7}
	LDR      r3, [r2, #4]
	LDR      r4, [r0, #0x28]
	LDR      r2, [r2]
	MUL      r3, r4
	LDR      r4, [r0, #0x24]
	MOV      r7, #0
	ADD      r3, r3, r4
	ADD      r6, r3, r2
	LDRH     r2, [r1, #2]
	ADD      r5, r1, #4
	CMP      r2, #0
	BLE      |loc_0803F8DE|
|loc_0803F8B4|
	LDRH     r4, [r1]
	ADD      r2, r6, #0
	MOV      r3, #0
	CMP      r4, #0
	BLE      |loc_0803F8D2|
|loc_0803F8BE|
	LDRB     r4, [r5]
	ADD      r5, #1
	CMP      r4, #0
	BEQ      |loc_0803F8C8|
	STRB     r4, [r2]
|loc_0803F8C8|
	LDRH     r4, [r1]
	ADD      r2, #1
	ADD      r3, #1
	CMP      r4, r3
	BGT      |loc_0803F8BE|
|loc_0803F8D2|
	LDR      r2, [r0, #0x28]
	ADD      r7, #1
	ADD      r6, r2, r6
	LDRH     r2, [r1, #2]
	CMP      r2, r7
	BGT      |loc_0803F8B4|
|loc_0803F8DE|
	POP      {r4, r5, r6, r7}
	BX       lr
	PUSH     {r4, r5, r6, r7}
	LDR      r4, [r2, #8]
	LDR      r6, [r2]
	LDR      r5, [r2, #0xc]
	LDR      r7, [r2, #4]
	SUB      r4, r4, r6
	SUB      r5, r5, r7
	ADD      r2, r4, #0
	MUL      r2, r5
	BEQ      |loc_0803F91E|
	LDR      r2, [r0, #0x28]
	LDR      r0, [r0, #0x24]
	MUL      r7, r2
	ADD      r0, r7, r0
	ADD      r0, r0, r6
	SUB      r2, r2, r4
	SUB      r7, r3, r4
|loc_0803F904|
	ADD      r6, r4, #0
|loc_0803F906|
	LDRB     r3, [r1]
	ADD      r1, #1
	CMP      r3, #0
	BEQ      |loc_0803F910|
	STRB     r3, [r0]
|loc_0803F910|
	ADD      r0, #1
	SUB      r6, #1
	BNE      |loc_0803F906|
	ADD      r0, r0, r2
	ADD      r1, r1, r7
	SUB      r5, #1
	BNE      |loc_0803F904|
|loc_0803F91E|
	POP      {r4, r5, r6, r7}
	BX       lr
	PUSH     {r4, r5, r6}
	LDR      r4, [r2, #4]
	ADD      r3, r1, #0
	LDR      r1, [r0, #0x28]
	ADD      r5, r4, #0
	LDR      r0, [r0, #0x24]
	MUL      r5, r1
	ADD      r0, r5, r0
	LDR      r5, [r2]
	LDR      r6, [r2, #8]
	LDR      r2, [r2, #0xc]
	ADD      r0, r0, r5
	SUB      r5, r6, r5
	SUB      r4, r2, r4
	SUB      r6, r1, r5
|loc_0803F940|
	ADD      r2, r5, #0
|loc_0803F942|
	LDRB     r1, [r3]
	ADD      r3, #1
	CMP      r1, #0
	BEQ      |loc_0803F94C|
	STRB     r1, [r0]
|loc_0803F94C|
	ADD      r0, #1
	SUB      r2, #1
	BNE      |loc_0803F942|
	ADD      r0, r0, r6
	SUB      r4, #1
	BNE      |loc_0803F940|
	POP      {r4, r5, r6}
	BX       lr
	LDR      r2, [r0, #0x30]
	LDR      r0, [r0, #0x24]
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
|loc_0803F964|
	LDRB     r3, [r0]
	CMP      r3, #0
	BNE      |loc_0803F96C|
	STRB     r1, [r0]
|loc_0803F96C|
	ADD      r0, #1
	SUB      r2, #1
	BNE      |loc_0803F964|
	BX       lr
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r6, r1, #0
	LDR      r1, [r1, #8]
	ADD      r7, r0, #0
	LDR      r0, [r6]
	SUB      sp, #8
	SUB      r1, r1, r0
	STR      r1, [sp, #4]
	LDR      r1, [r6, #4]
	LDR      r2, [r7, #0x28]
	ADD      r4, r1, #0
	MUL      r1, r2
	LDR      r2, [r7, #0x24]
	ADD      r1, r1, r2
	ADD      r5, r1, r0
	LDR      r0, [r6, #0xc]
	CMP      r0, r4
	BLE      |loc_0803F9AE|
|loc_0803F998|
	ADD      r0, r5, #0
	LDR      r1, [sp, #0x10]
	LDR      r2, [sp, #4]
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [r7, #0x28]
	ADD      r4, #1
	ADD      r5, r0, r5
	LDR      r0, [r6, #0xc]
	CMP      r0, r4
	BGT      |loc_0803F998|
|loc_0803F9AE|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	ADD      r5, r3, #6
	LSL      r0, r0, #0
	PUSH     {lr}
	SUB      sp, #0x14
	MOV      r2, #0
	STR      r2, [sp, #4]
	STR      r2, [sp, #8]
	LDR      r2, [r0, #0x2c]
	LDR      r3, [r0, #0x28]
	STR      r2, [sp, #0x10]
	ADD      r2, sp, #4
	STR      r3, [sp, #0xc]
	BL       |inc_0x049120_0x055620| + 0x3c
	ADD      sp, #0x14
	POP      {pc}
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	LDR      r0, [r1, #4]
	LDR      r2, [r1, #0xc]
	SUB      r5, r2, r0
	LDR      r2, [r1, #8]
	LDR      r1, [r1]
	SUB      r7, r2, r1
	LDR      r2, [r6, #0x28]
	MUL      r0, r2
	LDR      r2, [r6, #0x24]
	ADD      r0, r0, r2
	ADD      r4, r0, r1
	CMP      r5, #0
	BEQ      |loc_0803FA06|
|loc_0803F9F2|
	ADD      r3, r7, #0
	ADD      r1, r4, #0
	ADD      r0, r4, #0
	LDR      r2, [sp, #8]
	BL       |inc_0x049120_0x055620| + 0x6c
	LDR      r0, [r6, #0x28]
	ADD      r4, r0, r4
	SUB      r5, #1
	BNE      |loc_0803F9F2|
|loc_0803FA06|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	LDR      r0, [pc, #0x8c]
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	BL       |loc_0803F24A|
	LDR      r1, [pc, #0x88]
	MOV      r0, #0
	STRH     r0, [r1, #8]
	MOV      r1, #0x80
	LSL      r2, r1, #0x13
	STRH     r1, [r2]
	STRH     r0, [r2, #0x10]
	STRH     r0, [r2, #0x12]
	STRH     r0, [r2, #0x14]
	STRH     r0, [r2, #0x16]
	STRH     r0, [r2, #0x18]
	LDR      r1, [pc, #0x74]
	STRH     r0, [r2, #0x1a]
	STRH     r0, [r1]
	STRH     r0, [r1, #2]
	SWI      0
	POP      {r3, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x64]
	MOV      r1, #1
	LDRH     r0, [r0]
	LSL      r1, r1, #0x1a
	LDR      r5, [pc, #0x58]
	STR      r0, [sp]
	LDRH     r7, [r1]
	MOV      r0, #0x80
	MOV      r4, #0
	MOV      r6, #1
	STRH     r0, [r1]
|loc_0803FA50|
	ADD      r1, r6, #0
	LDR      r0, [r5]
	BL       |loc_0803F3F4|
	ADD      r4, #1
	CMP      r4, #0x1e
	BLT      |loc_0803FA50|
	LDR      r1, [pc, #0x40]
	MOV      r0, #3
	LSL      r0, r0, #0xc
	STRH     r0, [r1]
	LDR      r0, [pc, #0x40]
	ADD      r4, r1, #0
	SUB      r4, #0xe0
	STRH     r0, [r4, #0x12]
	SWI      3
	LDR      r0, [sp]
	LDR      r1, [pc, #0x2c]
	STRH     r0, [r1]
	MOV      r0, #0
	STRH     r0, [r4, #0x12]
	LSL      r1, r1, #0x11
	MOV      r4, #0xc1
	LSL      r4, r4, #2
	STRH     r7, [r1]
|loc_0803FA82|
	ADD      r1, r6, #0
	LDR      r0, [r5]
	BL       |loc_0803F3F4|
	LDR      r0, [r5, #8]
	BL       |inc_0x351c0_0x3d4d0| + 0x82e0
	LDR      r0, [r5, #8]
	LDRH     r0, [r0, #2]
	AND      r0, r4
	BNE      |loc_0803FA82|
	POP      {r3, r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	LDR      r0, [r4, #0x6c]
	LSR      r3, r7, #1
	LSL      r0, r0, #8
	LSL      r0, r0, #0x10
	LSL      r4, r3, #0
	LSL      r0, r0, #0x10
	STMIA    r3!, {r2}
	LSL      r0, r0, #0
