	CODE16
|sub_08018E62|
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x70]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r0, #2
	POP      {r3, pc}
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x70]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	CMP      r3, #0xa4
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x1dc]
	ADD      r6, r1, #0
	STR      r0, [r5]
	LDR      r0, [r5, #8]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08018EB2|
|loc_08018E9A|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r5, #8]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08018E9A|
|loc_08018EB2|
	CMP      r6, #0
	BEQ      |loc_08018EBC|
	ADD      r0, r5, #0
	BL       |GBARam_Free|
|loc_08018EBC|
	POP      {r4, r5, r6, pc}
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x1a8]
	ADD      r7, r1, #0
	STR      r0, [r5]
	MOV      r0, #0
	STR      r0, [r5, #4]
	LDR      r0, [r1, #0xc]
	MOV      r4, #0
	CMP      r0, #0
	STR      r0, [r5, #8]
	BLE      |loc_08018EF0|
|loc_08018ED6|
	LSL      r6, r4, #2
	ADD      r0, r6, r7
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	LDR      r1, [sp, #8]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r6, r5
	STR      r0, [r1, #0xc]
	LDR      r0, [r5, #8]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08018ED6|
|loc_08018EF0|
	ADD      r0, r5, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	LDR      r2, [r0, #4]
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	LDR      r3, [r2]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	ADD      r5, r1, #0
	LDR      r1, [r4, #8]
	MOV      r6, #0
	CMP      r0, r1
	BLT      |loc_08018F22|
	MOV      r0, #1
	STR      r6, [r4, #4]
	POP      {r4, r5, r6, pc}
|loc_08018F22|
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r2, r2, r1
	ADD      r1, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_08018F70|
	LDR      r0, [r4, #4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r2, r2, r1
	ADD      r1, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [r4, #4]
	ADD      r0, #1
	STR      r0, [r4, #4]
	LDR      r1, [r4, #8]
	CMP      r0, r1
	BLT      |loc_08018F5E|
	MOV      r0, #1
	STR      r6, [r4, #4]
	POP      {r4, r5, r6, pc}
|loc_08018F5E|
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	ADD      r1, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08018F70|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	ADD      r3, r0, #4
	LDMIA    r3!, {r2, r3}
	CMP      r2, r3
	BGE      |loc_08018F8E|
	LSL      r2, r2, #2
	ADD      r0, r2, r0
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	LDR      r3, [r2, #8]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08018F8E|
	POP      {r3, pc}
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	LDR      r0, [r0, #0xc]
	SUB      sp, #4
	LSL      r0, r0, #2
	ADD      r0, #0x10
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_08018FD4|
	LDR      r0, [pc, #0xc8]
	MOV      r5, #0
	STR      r0, [r4]
	LDR      r0, [pc, #0xc0]
	STR      r0, [r4]
	MOV      r0, #0
	STR      r0, [r4, #4]
	LDR      r0, [r6, #0xc]
	STR      r0, [r4, #8]
	CMP      r0, r5
	BLE      |loc_08018FD4|
|loc_08018FBA|
	LSL      r7, r5, #2
	ADD      r0, r7, r6
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	LDR      r1, [sp, #8]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r7, r4
	STR      r0, [r1, #0xc]
	LDR      r0, [r4, #8]
	ADD      r5, #1
	CMP      r0, r5
	BGT      |loc_08018FBA|
|loc_08018FD4|
	ADD      r0, r4, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #0xc]
	ADD      r7, r2, #0
	ADD      r6, r1, #0
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_08019006|
|loc_08018FEA|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #0x10]
	ADD      r2, r7, #0
	ADD      r1, r6, #0
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	CMP      r0, #0
	BNE      |loc_08019008|
	LDR      r0, [r5, #0xc]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08018FEA|
|loc_08019006|
	MOV      r0, #0
|loc_08019008|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	LDR      r0, [r0, #0xc]
	ADD      r7, r2, #0
	MOV      r5, #1
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_0801903C|
	LSL      r0, r4, #2
	ADD      r0, r0, r6
	LDR      r0, [r0, #0x10]
	ADD      r2, r7, #0
	LDR      r3, [r0, #4]
	LDR      r1, [sp, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	CMP      r0, #2
	BNE      |sub_08019032|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
