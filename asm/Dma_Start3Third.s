	CODE16
|Dma_Start3Third|
	LSR      r4, r0, #0x20
	DCW      0xf000,0x0600
	LSL      r4, r2, #3
	LSL      r0, r0, #0x10
	BLT      |loc_08008468|
	LDR      r1, [sp, #0x24]
	CMP      r1, #0x20
	BLE      |loc_08008594|
	LDR      r1, [sp, #0x24]
	LDR      r2, [sp, #0x18]
	LSL      r1, r1, #0x1b
	LSR      r1, r1, #0x1b
	CMP      r2, #0
	BGE      |loc_08008516|
	MOV      r6, #1
	ADD      r2, r5, #0
	ADD      r3, r4, #0
	EOR      r3, r6
	EOR      r2, r6
	LSL      r2, r2, #0xb
	LDR      r6, [pc, #0x35c]
	LSL      r3, r3, #5
	ADD      r2, r2, r3
	ADD      r3, r2, r6
	LDR      r2, [sp, #0x18]
	MOV      ip, r3
	LSL      r2, r2, #0x1c
	LSR      r2, r2, #0x1b
	LDR      r3, [r0, #0x20]
	MOV      r6, #0x20
	SUB      r6, r6, r2
	ADD      ip, r2
	ADD      r2, r3, r2
	MOV      r3, #0
	CMP      r1, #0
	BLE      |loc_08008516|
	LSL      r6, r6, #0xf
	LSR      r6, r6, #0x10
	LDR      r7, [pc, #0x33c]
	STR      r6, [sp, #0x28]
|loc_080084F8|
	STR      r2, [r7]
	MOV      r6, ip
	STR      r6, [r7, #4]
	LDR      r6, [sp, #0x28]
	STRH     r6, [r7, #8]
	MOV      r6, #1
	LSL      r6, r6, #0xf
	STRH     r6, [r7, #0xa]
	MOV      r6, ip
	ADD      r6, #0x40
	ADD      r2, #0x20
	ADD      r3, #1
	CMP      r3, r1
	MOV      ip, r6
	BLT      |loc_080084F8|
|loc_08008516|
	MOV      r2, #1
	EOR      r5, r2
	LSL      r2, r5, #0xb
	MOV      ip, r2
	LDR      r3, [pc, #0x310]
	ADD      r7, sp, #0x34
	ADD      r2, lr
	ADD      r2, r2, r3
	LDMIA    r7!, {r6, r7}
	CMP      r6, #0
	BEQ      |loc_08008558|
	LDR      r3, [r0, #0x24]
	ADD      r2, r2, r7
	MOV      r5, #0
	ADD      r3, r3, r7
	CMP      r1, #0
	BLE      |loc_08008558|
	LSL      r6, r6, #0xf
	LSR      r7, r6, #0x10
	LDR      r6, [pc, #0x2f4]
	MOV      lr, r7
|loc_08008540|
	STR      r3, [r6]
	STR      r2, [r6, #4]
	MOV      r7, lr
	STRH     r7, [r6, #8]
	MOV      r7, #1
	LSL      r7, r7, #0xf
	STRH     r7, [r6, #0xa]
	ADD      r3, #0x20
	ADD      r2, #0x40
	ADD      r5, #1
	CMP      r5, r1
	BLT      |loc_08008540|
|loc_08008558|
	LDR      r2, [sp, #0x20]
	CMP      r2, #0x10
	BLE      |loc_08008594|
	MOV      r2, #1
	EOR      r4, r2
	LSL      r2, r4, #5
	LDR      r3, [pc, #0x2c8]
	ADD      r2, ip
	ADD      r2, r2, r3
	LDR      r3, [sp, #0x20]
	MOV      r4, #0
	LSL      r3, r3, #1
	SUB      r3, #0x20
	CMP      r1, #0
	LDR      r0, [r0, #0x28]
	BLE      |loc_08008594|
	MOV      r5, #1
	LSL      r5, r5, #0xf
	LDR      r6, [pc, #0x2b4]
	LSL      r3, r3, #0xf
	LSR      r3, r3, #0x10
|loc_08008582|
	STR      r0, [r6]
	STR      r2, [r6, #4]
	STRH     r3, [r6, #8]
	STRH     r5, [r6, #0xa]
	ADD      r0, #0x20
	ADD      r2, #0x40
	ADD      r4, #1
	CMP      r4, r1
	BLT      |loc_08008582|
|loc_08008594|
	ADD      sp, #0x50
	POP      {r4, r5, r6, r7, pc}
