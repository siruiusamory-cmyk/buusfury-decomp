	CODE16
|loc_08009BD4|
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	SUB      sp, #0x1fc
	SUB      sp, #0x1fc
	SUB      sp, #0x1fc
	MOV      r3, #7
	LSL      r3, r3, #8
	SUB      sp, #0x110
	ADD      r3, sp
	LDR      r1, [r3, #8]
	LDR      r0, [r1, #0x48]
	LDR      r0, [r0, #4]
	LSR      r1, r0, #0x1f
	ADD      r0, r1, r0
	LDR      r1, [r3, #8]
	ASR      r7, r0, #1
	LDR      r0, [r1, #0x48]
	ADD      r1, sp, #4
	BL       |inc_0x03d784_0x041118| + 0x1bc
	MOV      r0, #1
	CMP      r7, #1
	BLE      |loc_08009C18|
	ADD      r4, sp, #4
|loc_08009C02|
	LSL      r1, r0, #1
	ADD      r3, r1, r4
	SUB      r3, #0x20
	LDRH     r3, [r3, #0x1e]
	LDRH     r2, [r4, r1]
	ADD      r0, #1
	ADD      r2, r2, r3
	ADD      r2, #1
	STRH     r2, [r4, r1]
	CMP      r0, r7
	BLT      |loc_08009C02|
|loc_08009C18|
	MOV      r0, #1
	LSL      r0, r0, #0xe
	BL       |GBARam_Malloc|
	MOV      r6, #3
	LSL      r6, r6, #0x19
	MOV      r4, #0
	MOV      r5, #0
	CMP      r7, #0
	STR      r0, [sp]
	BLE      |loc_08009C84|
|loc_08009C2E|
	LSL      r0, r4, #1
	ADD      r1, sp, #4
	LDRH     r0, [r1, r0]
	LSR      r0, r0, #8
	B        |loc_08009C3A|
|loc_08009C38|
	ADD      r5, #1
|loc_08009C3A|
	CMP      r5, r7
	BGE      |loc_08009C4A|
	LSL      r1, r5, #1
	ADD      r2, sp, #4
	LDRH     r1, [r2, r1]
	LSR      r1, r1, #8
	CMP      r1, r0
	BEQ      |loc_08009C38|
|loc_08009C4A|
	MOV      r3, #7
	LSL      r3, r3, #8
	ADD      r3, sp
	LDR      r1, [r3, #8]
	LSL      r0, r0, #2
	LDR      r1, [r1, #0x4c]
	LDR      r0, [r1, r0]
	LDR      r1, [sp]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	CMP      r4, r5
	BGE      |loc_08009C80|
|loc_08009C62|
	LSL      r0, r4, #1
	ADD      r1, sp, #4
	LDRH     r0, [r1, r0]
	LDR      r1, [sp]
	MOV      r2, #0x40
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x12
	ADD      r1, r0, r1
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r6, #0x40
	ADD      r4, #1
	CMP      r4, r5
	BLT      |loc_08009C62|
|loc_08009C80|
	CMP      r4, r7
	BLT      |loc_08009C2E|
|loc_08009C84|
	LDR      r0, [sp]
	BL       |GBARam_Free|
	MOV      r3, #7
	LSL      r3, r3, #8
	ADD      r3, sp
	LDR      r0, [r3, #4]
	MOV      r4, #0
	LDR      r0, [r0, #4]
	CMP      r0, #0
	BLE      |loc_08009CB8|
	LDR      r5, [r3, #4]
	ADD      r5, #4
|loc_08009C9E|
	LSL      r0, r4, #3
	ADD      r0, r0, r5
	ADD      r0, #4
	BL       |loc_08009B12|
	MOV      r3, #7
	LSL      r3, r3, #8
	ADD      r3, sp
	LDR      r0, [r3, #4]
	ADD      r4, #1
	LDR      r0, [r0, #4]
	CMP      r0, r4
	BGT      |loc_08009C9E|
|loc_08009CB8|
	ADD      sp, #0x1fc
	ADD      sp, #0x1fc
	ADD      sp, #0x1fc
	ADD      sp, #0x118
	POP      {r4, r5, r6, r7, pc}
