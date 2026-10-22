	CODE16
|loc_0803F296|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r0, #0
	MOV      r0, #1
	SUB      sp, #0x1c
	STR      r0, [r7]
	LDR      r0, [r7, #4]
	LDR      r4, [r7, #8]
	SUB      r1, r0, r4
	LSL      r5, r1, #0x16
	LSR      r5, r5, #0x16
	STR      r5, [sp, #0xc]
	CMP      r5, #0x40
	BLT      |loc_0803F390|
	STR      r0, [r7, #8]
	LDR      r0, [pc, #0xe4]
	ADD      r0, r7, r0
	STR      r0, [sp, #0x18]
	BL       |loc_0803E3F6|
	ADD      r0, r7, #0
	ADD      r0, #0xc
	STR      r0, [sp, #0x14]
	LDR      r0, [pc, #0x108]
	ADD      r6, r7, r0
|loc_0803F2C6|
	MOV      r1, #1
	LDR      r5, [sp, #0xc]
	LSL      r1, r1, #9
	CMP      r5, r1
	BLE      |loc_0803F2D2|
	ADD      r5, r1, #0
|loc_0803F2D2|
	ADD      r2, r5, #0
	ADD      r1, r6, #0
	LDR      r0, [sp, #0x14]
	BL       |loc_0803F07C|
	ADD      r2, r5, #0
	ADD      r1, r6, #0
	LDR      r0, [sp, #0x18]
	BL       |loc_0803E40C|
	ADD      r0, r4, r5
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	STR      r0, [sp, #0x10]
	BLE      |sub_0803F322|
	SUB      r3, r1, r4
	STR      r3, [sp, #8]
	SUB      r3, r0, r1
	LDR      r0, [pc, #0xd4]
	STR      r3, [sp, #4]
	ADD      r1, r4, r0
	LSL      r0, r0, #0x10
	ADD      r2, r6, #0
	ADD      r0, r4, r0
	LDR      r3, [sp, #8]
	BL       |inc_0x049120_0x055620| + 0x94
	LDR      r3, [sp, #8]
	LDR      r1, [pc, #0xbc]
	LSL      r0, r3, #2
	ADD      r0, r0, r7
	ADD      r2, r0, r1
	MOV      r0, #1
	LSL      r0, r0, #0x19
	LDR      r1, [pc, #0x90]
	LDR      r3, [sp, #4]
	BL       |inc_0x049120_0x055620| + 0x94
	B        |loc_0803F382|
