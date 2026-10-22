	CODE16
|sub_08025004|
	PUSH     {r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #0
	SUB      sp, #0x14
	STR      r0, [sp, #4]
	MOV      r0, #0xb
	LSL      r0, r0, #8
	ADD      r4, r5, r0
	LDR      r0, [r4, #0x18]
	ADD      r2, sp, #4
	STR      r0, [sp, #8]
	MOV      r0, #0x68
	STR      r0, [sp, #0xc]
	LDR      r0, [r4, #0x18]
	LDR      r1, [pc, #0x2f0]
	ADD      r0, #0x38
	STR      r0, [sp, #0x10]
	LDR      r0, [r4, #0xc]
	BL       |inc_0x049120_0x055620| + 0x3c
	MOV      r0, #0x2b
	LSL      r0, r0, #6
	ADD      r0, r5, r0
	LDR      r1, [r0, #0x3c]
	LDR      r2, [r4, #0x18]
	MOV      r0, #1
	CMP      r2, #0
	BGT      |loc_0802503E|
	MOV      r0, #0
|loc_0802503E|
	STR      r0, [r1, #0x20]
	LDR      r0, [r4]
	ADD      r4, #0x18
	LDMIA    r4!, {r1, r2}
	CMP      r1, r2
	BGE      |loc_0802504E|
	MOV      r1, #1
	B        |loc_08025050|
|loc_0802504E|
	MOV      r1, #0
|loc_08025050|
	STR      r1, [r0, #0x20]
	ADD      sp, #0x14
	POP      {r4, r5, pc}
|loc_08025056|
	PUSH     {r0, r4, r5, r6, r7, lr}
	LDR      r3, [pc, #0x2bc]
	MOV      r0, #0xb
	ADD      sp, r3
	MOV      r3, #0x21
	LSL      r3, r3, #7
	ADD      r3, sp
	LDR      r1, [r3]
	LSL      r0, r0, #8
	ADD      r4, r1, r0
	LDR      r0, [r4, #0x14]
	ADD      r1, #0x10
	SUB      r3, #0x80
	STR      r1, [r3, #0x7c]
	MOV      r7, #0
	ADD      r3, r0, #1
	BEQ      |loc_0802508C|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r1, [r3, #0x7c]
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x288]
	LSL      r0, r0, #4
	ADD      r7, r0, r1
|loc_0802508C|
	LDR      r0, [r4, #0xc]
	CMP      r0, #0
	BEQ      |loc_0802509C|
	MOV      r1, #1
	BL       |inc_0x03d784_0x041118| + 0x1e08
	MOV      r1, #0
	STR      r1, [r4, #0xc]
|loc_0802509C|
	LDR      r5, [pc, #0x27c]
	MOV      r2, #0xa0
	MOV      r1, #0xf0
	ADD      r5, sp
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	MOV      r3, #1
	LSL      r3, r3, #0xc
	LDR      r0, [pc, #0x25c]
	ADD      r3, sp
	LDR      r1, [r3, #0x68]
	ADD      r0, #0x14
	BL       |inc_0x03d784_0x041118| + 0x1bc
	MOV      r2, #0
	MVN      r2, r2
	ADD      r1, r5, #0
	ADD      r0, r7, #0
	BL       |sub_08024D94|
	CMP      r7, #0
	BEQ      |loc_080250F4|
	LDR      r0, [r7, #8]
	CMP      r0, #0
	BEQ      |loc_080250F4|
	LDR      r0, [r7, #8]
	BL       |inc_0x0158_0x143f2| + 0x11dc8
	ADD      r5, sp, #0x44
	ADD      r1, r5, #0
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r0, [pc, #0x240]
	ADD      r6, sp, #0x34
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r6!, {r0, r1, r2, r3}
	SUB      r6, #0x10
	LDR      r0, [pc, #0x230]
	ADD      r2, r6, #0
	ADD      r1, r5, #0
	ADD      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x219e
|loc_080250F4|
	LDR      r0, [pc, #0x224]
	LDR      r1, [pc, #0x22c]
	ADD      r0, sp
	BL       |inc_0x03d784_0x041118| + 0x2234
	MOV      r3, #0x21
	LSL      r3, r3, #7
	ADD      r3, sp
	LDR      r2, [r3]
	MOV      r1, #0x2b
	LSL      r1, r1, #6
	ADD      r1, r2, r1
	SUB      r3, #0x80
	LDRB     r0, [r2, #0xe]
	STR      r1, [r3, #0x78]
	MOV      r1, #0xed
	LSL      r1, r1, #2
	ADD      r6, r2, r1
	CMP      r0, #0
	BNE      |loc_08025202|
	MOV      r0, #0x68
	STR      r0, [r3, #0x6c]
	MOV      r0, #0x38
	STR      r0, [r3, #0x70]
	MOV      r0, #0x5b
	LSL      r0, r0, #6
	STR      r0, [r3, #0x74]
	LDR      r0, [r3, #0x6c]
	LDR      r1, [r3, #0x70]
	STR      r0, [r3, #0x5c]
	STR      r1, [r3, #0x60]
	MOV      r2, #0x5b
	LSL      r2, r2, #6
	MOV      r1, #0
	LDR      r0, [r3, #0x68]
	BL       |inc_0x046118_0x049114| + 0xd28
	MOV      r3, #0x41
	LSL      r3, r3, #6
	ADD      r3, sp
	MOV      r1, #1
	STRB     r1, [r3, #4]
	LDR      r0, [r6]
	MOV      r1, #0x34
	CMP      r0, #0
	BEQ      |sub_080251D4|
	LDR      r2, [r4, #0x10]
	SUB      r3, #0x40
	SUB      r5, r2, #3
	ADD      r2, #4
	CMP      r0, r2
	STR      r5, [r3, #0x40]
	BGT      |loc_08025162|
	SUB      r0, #7
	STR      r0, [r3, #0x40]
|loc_08025162|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r0, [r3, #0x40]
	CMP      r0, #0
	BGE      |loc_08025172|
	MOV      r0, #0
	STR      r0, [r3, #0x40]
|loc_08025172|
	MOV      r5, #0
|loc_08025174|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r0, [r3, #0x40]
	LDR      r1, [r6]
	ADD      r0, r5, r0
	CMP      r1, r0
	BLE      |sub_08025204|
	LSL      r1, r0, #3
	ADD      r1, r1, r6
	ADD      r1, #4
	MOV      ip, r1
	LDR      r2, [r4, #0x10]
	MOV      r1, #2
	CMP      r2, r0
	BEQ      |loc_08025196|
	MOV      r1, #0x75
|loc_08025196|
	MOV      r3, #0x41
	LSL      r3, r3, #6
	ADD      r3, sp
	STRB     r1, [r3, #7]
	LSL      r0, r5, #3
	ADD      r0, #7
	SUB      r3, #0x40
	STR      r0, [r3, #0x4c]
	MOV      r1, #0x34
	STR      r1, [r3, #0x48]
	MOV      r1, ip
	LDR      r1, [r1]
	LDR      r0, [r3, #0x7c]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x158]
	LSL      r0, r0, #4
	ADD      r0, r0, r1
	LDRH     r0, [r0]
	LDR      r1, [pc, #0x168]
	LSL      r0, r0, #2
	LDR      r1, [r1, r0]
	ADD      r0, r3, #0
	ADD      r0, #0x44
	BL       |inc_0x03d784_0x041118| + 0x356
	ADD      r5, #1
	CMP      r5, #7
	BLT      |loc_08025174|
	B        |sub_08025204|
