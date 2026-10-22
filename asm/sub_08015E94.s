	CODE16
|sub_08015E94|
	PUSH     {r4, r5, r6, r7}
	LDR      r1, [r0, #0x3c]
	SUB      sp, #0x10
	CMP      r1, #0
	BEQ      |loc_08015F16|
	SUB      r2, r1, #1
	STR      r2, [r0, #0x3c]
	LDR      r1, [r0, #0x34]
	CMP      r2, r1
	BGE      |loc_08015F16|
	STR      r2, [r0, #0x34]
	LDR      r1, [r0, #0x1c]
	LDR      r1, [r1, #0x10]
	CMP      r1, #0
	BEQ      |loc_08015F16|
	LDR      r1, [r0, #0x2c]
	LDR      r3, [r0, #0x24]
	STR      r2, [r0, #0x38]
	SUB      r7, r1, r3
	MOV      r1, #3
	MVN      r1, r1
	SUB      r7, #0x28
	LDR      r6, [r0, #0x4c]
	ADD      r4, r0, #0
	ADD      r4, #0x4c
|loc_08015EC6|
	LDR      r2, [r0, #0x38]
	ADD      r5, r1, #0
	CMP      r6, r2
	BLE      |loc_08015EE6|
	LSL      r3, r2, #1
	ADD      r3, r3, r2
	LSL      r3, r3, #2
	ADD      r3, r3, r4
	LDR      r3, [r3, #0xc]
	ADD      r1, r3, r1
	ADD      r1, #0xa
	CMP      r1, r7
	BGT      |loc_08015EE6|
	ADD      r2, #1
	STR      r2, [r0, #0x38]
	B        |loc_08015EC6|
|loc_08015EE6|
	ADD      r1, r0, #0
	ADD      r1, #0x24
	ADD      r2, r1, #0
	LDR      r3, [r0, #0x24]
	LDR      r4, [r0, #0x2c]
	ADD      r2, #8
	LDR      r1, [r0, #0x28]
	LDR      r2, [r2, #4]
	ADD      r3, r3, r4
	ADD      r1, r1, r2
	STR      r1, [sp, #4]
	ASR      r1, r1, #1
	ASR      r2, r3, #1
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	STR      r3, [sp]
	STR      r2, [sp]
	ADD      r1, r2, #0
	STR      r2, [sp, #8]
	LSR      r2, r5, #0x1f
	ADD      r2, r2, r5
	ASR      r2, r2, #1
	SUB      r1, r1, r2
	STR      r1, [r0, #0x48]
|loc_08015F16|
	ADD      sp, #0x10
	POP      {r4, r5, r6, r7}
	BX       lr
	PUSH     {r4, r5, r6}
	LDR      r2, [r0, #0x4c]
	LDR      r1, [r0, #0x3c]
	SUB      r2, #1
	CMP      r2, r1
	SUB      sp, #0x10
	BLE      |loc_08015FA2|
	ADD      r1, #1
	STR      r1, [r0, #0x3c]
	LDR      r2, [r0, #0x38]
	CMP      r1, r2
	BLT      |loc_08015FA2|
	ADD      r2, r1, #1
	STR      r2, [r0, #0x38]
	LDR      r1, [r0, #0x1c]
	LDR      r1, [r1, #0x10]
	CMP      r1, #0
	BEQ      |loc_08015FA2|
	LDR      r1, [r0, #0x2c]
	LDR      r3, [r0, #0x24]
	ADD      r4, r0, #0
	SUB      r6, r1, r3
	MOV      r1, #3
	MVN      r1, r1
	SUB      r6, #0x28
	ADD      r4, #0x4c
	STR      r2, [r0, #0x34]
|loc_08015F52|
	LDR      r2, [r0, #0x34]
	ADD      r5, r1, #0
	CMP      r2, #0
	BLE      |loc_08015F72|
	SUB      r2, #1
	LSL      r3, r2, #1
	ADD      r3, r3, r2
	LSL      r3, r3, #2
	ADD      r3, r3, r4
	LDR      r3, [r3, #0xc]
	ADD      r1, r3, r1
	ADD      r1, #0xa
	CMP      r1, r6
	BGT      |loc_08015F72|
	STR      r2, [r0, #0x34]
	B        |loc_08015F52|
|loc_08015F72|
	ADD      r1, r0, #0
	ADD      r1, #0x24
	ADD      r2, r1, #0
	LDR      r3, [r0, #0x24]
	LDR      r4, [r0, #0x2c]
	ADD      r2, #8
	LDR      r1, [r0, #0x28]
	LDR      r2, [r2, #4]
	ADD      r3, r3, r4
	ADD      r1, r1, r2
	STR      r1, [sp, #4]
	ASR      r1, r1, #1
	ASR      r2, r3, #1
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	STR      r3, [sp]
	STR      r2, [sp]
	ADD      r1, r2, #0
	STR      r2, [sp, #8]
	LSR      r2, r5, #0x1f
	ADD      r2, r2, r5
	ASR      r2, r2, #1
	SUB      r1, r1, r2
	STR      r1, [r0, #0x48]
|loc_08015FA2|
	ADD      sp, #0x10
	POP      {r4, r5, r6}
	BX       lr
	PUSH     {r4, r5, r6, r7}
	LDR      r5, [r0, #0x4c]
	MOV      r2, #0
	CMP      r5, #0
	BLE      |loc_08015FE6|
	ADD      r4, r0, #0
	ADD      r4, #0x4c
	ADD      r6, r4, #0
	ADD      r6, #0xb4
	MOV      r7, #0
|loc_08015FBC|
	LSL      r3, r2, #1
	ADD      r3, r3, r2
	LSL      r3, r3, #2
	ADD      r3, r3, r4
	LDR      r3, [r3, #8]
	CMP      r3, r1
	BNE      |loc_08015FE0|
	STR      r2, [r0, #0x3c]
	STR      r2, [r0, #0x40]
	LDR      r3, [r0, #0x1c]
	LDR      r3, [r3, #0x10]
	CMP      r3, #0
	BEQ      |loc_08015FE0|
	SUB      r3, r2, #1
	STR      r3, [r0, #0x34]
	BPL      |loc_08015FDE|
	STR      r7, [r0, #0x34]
|loc_08015FDE|
	STR      r7, [r6, #0x10]
|loc_08015FE0|
	ADD      r2, #1
	CMP      r5, r2
	BGT      |loc_08015FBC|
|loc_08015FE6|
	POP      {r4, r5, r6, r7}
	BX       lr
	LDR      r2, [r0, #0x1c]
	CMP      r2, r1
	BNE      |sub_08015FF2|
	B        |sub_08015E94|
