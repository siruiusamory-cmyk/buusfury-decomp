	CODE16
|loc_08007D98|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [r1]
	SUB      sp, #0x24
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1b
	STR      r0, [sp, #8]
	LDR      r0, [r1, #4]
	LDR      r1, [pc, #0xd4]
	LSL      r0, r0, #0x18
	LSR      r6, r0, #0x1b
	LDRB     r0, [r5, #4]
	ADD      r4, r6, #0
	LSL      r0, r0, #0xb
	ADD      r7, r0, r1
	LDR      r1, [sp, #8]
	MOV      r0, #0x20
	SUB      r0, r0, r1
	STR      r0, [sp, #4]
	CMP      r6, #0x20
	BGE      |loc_08007DE8|
	LDR      r0, [sp, #4]
	LSL      r0, r0, #1
	STR      r0, [sp, #0x20]
	LDR      r0, [sp, #8]
	LSL      r2, r0, #1
	STR      r2, [sp, #0x1c]
|loc_08007DCE|
	LDR      r1, [r5, #0x10]
	LSL      r0, r4, #6
	ADD      r1, r1, r0
	LDR      r2, [sp, #0x1c]
	ADD      r0, r0, r7
	ADD      r1, r1, r2
	ADD      r0, r0, r2
	LDR      r2, [sp, #0x20]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      r4, #1
	CMP      r4, #0x20
	BLT      |loc_08007DCE|
|loc_08007DE8|
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_08007E0E|
	ADD      r4, r6, #0
	CMP      r6, #0x20
	BGE      |loc_08007E0E|
	LDR      r0, [sp, #8]
	LSL      r0, r0, #1
	STR      r0, [sp, #0x18]
|loc_08007DFA|
	LDR      r1, [r5, #0x14]
	LSL      r0, r4, #6
	ADD      r1, r1, r0
	ADD      r0, r0, r7
	LDR      r2, [sp, #0x18]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      r4, #1
	CMP      r4, #0x20
	BLT      |loc_08007DFA|
|loc_08007E0E|
	MOV      r4, #0
	CMP      r6, #0
	BLE      |loc_08007E3A|
	LDR      r0, [sp, #4]
	LSL      r0, r0, #1
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #8]
	LSL      r2, r0, #1
	STR      r2, [sp, #0x10]
|loc_08007E20|
	LDR      r1, [r5, #0x18]
	LSL      r0, r4, #6
	ADD      r1, r1, r0
	LDR      r2, [sp, #0x10]
	ADD      r0, r0, r7
	ADD      r1, r1, r2
	ADD      r0, r0, r2
	LDR      r2, [sp, #0x14]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      r4, #1
	CMP      r4, r6
	BLT      |loc_08007E20|
|loc_08007E3A|
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_08007E60|
	MOV      r4, #0
	CMP      r6, #0
	BLE      |loc_08007E60|
	LDR      r0, [sp, #8]
	LSL      r0, r0, #1
	STR      r0, [sp, #0xc]
|loc_08007E4C|
	LDR      r1, [r5, #0x1c]
	LSL      r0, r4, #6
	ADD      r1, r1, r0
	ADD      r0, r0, r7
	LDR      r2, [sp, #0xc]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      r4, #1
	CMP      r4, r6
	BLT      |loc_08007E4C|
|loc_08007E60|
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
|loc_08007E64|
	DCW      0x204c
	DCW      0x0000,0x9410,0x0804,0x0808,0x0807,0xf7e4,0xffff,0x1008
	DCW      0x0807,0x0804,0x0000,0x0824,0x0000,0xe000
|loc_08007E82|
	LSL      r0, r0, #0x18
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1, #0x18]
	ADD      r5, r1, #0
	LDR      r1, [r4, #0x3c]
	SUB      sp, #0x2c
	MUL      r1, r0
	LDR      r0, [r4, #0x44]
	LDR      r2, [pc, #0x1fc]
	ADD      r0, r1, r0
	LDR      r1, [r5, #0x30]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x24]
	LDR      r0, [r5, #0x1c]
	LDR      r1, [r4, #0x40]
	MUL      r1, r0
	LDR      r0, [r4, #0x48]
	ADD      r0, r1, r0
	LDR      r1, [r5, #0x34]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x28]
	LDR      r0, [sp, #0x24]
	ASR      r1, r0, #0xa
	LDR      r0, [sp, #0x28]
	STR      r1, [sp, #0x14]
	ASR      r0, r0, #0xa
	STR      r0, [sp, #0x18]
	STR      r0, [sp, #0x20]
	ADD      r0, r1, #0
	STR      r1, [sp, #0x1c]
	LDR      r1, [r2]
	SUB      r0, r0, r1
	LDR      r1, [sp, #0x20]
	LDR      r2, [r2, #4]
	STR      r0, [sp, #0xc]
	SUB      r1, r1, r2
	STR      r1, [sp, #0x10]
	STR      r1, [sp, #0x18]
	ASR      r1, r0, #8
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0x18]
	STR      r1, [sp, #4]
	ASR      r0, r0, #8
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x10]
	STR      r1, [sp, #0xc]
	ADD      r1, sp, #0xc
	ADD      r0, r4, #0
	BL       |sub_08007C12|
	ADD      r1, sp, #0x14
	ADD      r0, r4, #0
	BL       |loc_08007D98|
	LDRB     r0, [r4, #4]
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	ADD      r2, sp, #0x1c
	LDMIA    r2!, {r1, r2}
	ADD      r0, #0x10
	STRH     r1, [r0]
	STRH     r2, [r0, #2]
	LDR      r2, [sp, #0x1c]
	LDR      r3, [r5, #0x18]
	ADD      r0, r4, #0
	SUB      r2, r2, r3
	LDR      r3, [sp, #0x20]
	LDR      r1, [r5, #0x1c]
	STR      r2, [sp, #0xc]
	SUB      r1, r3, r1
	STR      r1, [sp, #0x10]
	ADD      r1, r2, #0
	LDR      r2, [sp, #0x10]
	LDR      r3, [r4, #0x2c]
	ADD      r0, #0x34
	SUB      r1, r1, r3
	LDR      r3, [r4, #0x30]
	STR      r1, [sp, #0xc]
	SUB      r2, r2, r3
	STR      r2, [sp, #0x10]
	STMIA    r0!, {r1, r2}
	ADD      sp, #0x2c
	POP      {r4, r5, pc}
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1, #0x18]
	ADD      r5, r1, #0
	LDR      r1, [r4, #0x3c]
	SUB      sp, #0x2c
	MUL      r1, r0
	LDR      r0, [r4, #0x44]
	LDR      r2, [pc, #0x154]
	ADD      r0, r1, r0
	LDR      r1, [r5, #0x30]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x24]
	LDR      r0, [r5, #0x1c]
	LDR      r1, [r4, #0x40]
	MUL      r1, r0
	LDR      r0, [r4, #0x48]
	ADD      r0, r1, r0
	LDR      r1, [r5, #0x34]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x28]
	LDR      r0, [sp, #0x24]
	ASR      r1, r0, #0xa
	LDR      r0, [sp, #0x28]
	STR      r1, [sp, #0x14]
	ASR      r0, r0, #0xa
	STR      r0, [sp, #0x18]
	STR      r0, [sp, #0x20]
	ADD      r0, r1, #0
	STR      r1, [sp, #0x1c]
	LDR      r1, [r2]
	SUB      r0, r0, r1
	LDR      r1, [sp, #0x20]
	LDR      r2, [r2, #4]
	STR      r0, [sp, #0xc]
	SUB      r1, r1, r2
	STR      r1, [sp, #0x10]
	STR      r1, [sp, #0x18]
	ASR      r1, r0, #8
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0x18]
	STR      r1, [sp, #4]
	ASR      r0, r0, #8
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x10]
	ADD      r0, r1, #0
	STR      r1, [sp, #0xc]
	LDR      r1, [r4, #0x24]
	CMP      r0, r1
	BNE      |loc_08007F9A|
	LDR      r0, [sp, #0x10]
	LDR      r1, [r4, #0x28]
	CMP      r0, r1
	BEQ      |loc_08007FA2|
|loc_08007F9A|
	ADD      r1, sp, #0xc
	ADD      r0, r4, #0
	BL       |sub_08007C12|
|loc_08007FA2|
	ADD      r1, sp, #0x14
	ADD      r0, r4, #0
	BL       |loc_08007D98|
	LDRB     r0, [r4, #4]
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	ADD      r2, sp, #0x1c
	LDMIA    r2!, {r1, r2}
	ADD      r0, #0x10
	STRH     r1, [r0]
	STRH     r2, [r0, #2]
	LDR      r2, [sp, #0x1c]
	LDR      r3, [r5, #0x18]
	ADD      r0, r4, #0
	SUB      r2, r2, r3
	LDR      r3, [sp, #0x20]
	LDR      r1, [r5, #0x1c]
	STR      r2, [sp, #4]
	SUB      r1, r3, r1
	STR      r1, [sp, #8]
	ADD      r1, r2, #0
	LDR      r2, [sp, #8]
	LDR      r3, [r4, #0x2c]
	ADD      r0, #0x34
	SUB      r1, r1, r3
	LDR      r3, [r4, #0x30]
	STR      r1, [sp, #4]
	SUB      r2, r2, r3
	STR      r2, [sp, #8]
	STMIA    r0!, {r1, r2}
	ADD      sp, #0x2c
	POP      {r4, r5, pc}
	PUSH     {r4}
	LDR      r3, [r0, #8]
	ADD      r3, #0xc
	LDMIA    r3!, {r4}
	STR      r4, [r0, #0x44]
	LDR      r3, [r3]
	STR      r3, [r0, #0x48]
	LDR      r2, [r1]
	LSL      r2, r2, #0xa
	ADD      r2, r4, r2
	STR      r2, [r0, #0x44]
	LDR      r1, [r1, #4]
	LSL      r1, r1, #0xa
	ADD      r1, r3, r1
	STR      r1, [r0, #0x48]
	POP      {r4}
	BX       lr
	PUSH     {r4, r5, r6}
	LDR      r3, [r1]
	LDR      r4, [r0, #0x34]
	SUB      sp, #8
	ADD      r3, r3, r4
	LDR      r4, [r1, #4]
	LDR      r5, [r0, #0x38]
	STR      r3, [sp]
	ADD      r4, r4, r5
	STR      r4, [sp, #4]
	ADD      r4, r3, #0
	LDR      r3, [sp, #4]
	ASR      r4, r4, #8
	ASR      r3, r3, #8
	STR      r3, [sp, #4]
	CMP      r4, #0
	STR      r4, [sp]
	BLT      |loc_0800803A|
	CMP      r3, #0
	BLT      |loc_0800803A|
	CMP      r4, #2
	BGE      |loc_0800803A|
	CMP      r3, #2
	BLT      |sub_08008042|
|loc_0800803A|
	MOV      r0, #0
	ADD      sp, #8
	POP      {r4, r5, r6}
	BX       lr
