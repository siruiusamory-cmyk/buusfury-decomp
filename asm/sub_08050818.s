	CODE16
|sub_08050818|
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	BLE      |loc_08050890|
	LSR      r1, r6, #1
|unk_08050820|
	INCBIN	baserom.gba_0x50820_0x50822.extracted
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	LDMIA    r2!, {r7}
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r3, #0
	ADD      r5, r2, #0
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_08050842|
	MOV      r0, #0x28
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0805085C|
|loc_08050842|
	LDR      r1, [pc, #0x1c]
	MOV      r2, #0
	STMIA    r0!, {r1, r2}
	LDR      r1, [pc, #0x18]
	SUB      r0, #8
	LDMIA    r4!, {r3, r4}
	STR      r1, [r0]
	STR      r2, [r0, #0x20]
	STR      r3, [r0, #0x14]
	STR      r4, [r0, #0x18]
	STR      r6, [r0, #8]
	MOV      r1, #0x24
	STRB     r5, [r1, r0]
|loc_0805085C|
	POP      {r4, r5, r6, pc}
	LSL      r0, r0, #0
	ADD      r6, sp, #0x210
	LSR      r4, r0, #0x20
	BEQ      |loc_080507B0|
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	CMP      r0, #0
|loc_0805086C|
	BNE      |loc_08050874|
	MOV      r0, #2
	BL       |GBARam_Malloc|
|loc_08050874|
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #0x24
	LDR      r5, [sp, #0x5c]
	LDR      r6, [sp, #0x60]
	LDR      r7, [sp, #0x64]
	ADD      r4, r0, #0
	BNE      |sub_08050896|
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08050896|
|loc_08050890|
	ADD      r0, r4, #0
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
