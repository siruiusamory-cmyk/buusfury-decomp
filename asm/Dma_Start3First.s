	CODE16
|Dma_Start3First|
	LDR      r6, [r1]
	MOV      r3, #0
	STR      r3, [sp, #0x10]
	LDR      r3, [sp, #0x1c]
	ADD      r1, r2, #4
	CMP      r3, #0
	STR      r6, [sp, #0x14]
	BGT      |loc_080081F6|
	ADD      r1, sp, #0x10
|loc_080081F6|
	LDR      r1, [r1]
	MOV      r6, #0x10
	STR      r6, [sp, #0xc]
	LDR      r6, [sp, #0x20]
	ADD      r3, r2, #0
	ADD      r3, #8
	CMP      r6, #0x10
	BLT      |loc_08008208|
	ADD      r3, sp, #0xc
|loc_08008208|
	LDR      r3, [r3]
	ADD      r2, #0xc
	STR      r3, [sp, #0x10]
	MOV      r3, #0x20
	STR      r3, [sp, #0xc]
	LDR      r3, [sp, #0x24]
	CMP      r3, #0x20
	BLT      |loc_0800821A|
	ADD      r2, sp, #0xc
|loc_0800821A|
	LDR      r3, [r2]
	LDR      r2, [sp, #0x1c]
	CMP      r2, #0
	BGE      |Dma_Start3Second|
	LDR      r2, [sp, #0x18]
	CMP      r2, #0
	BGE      |loc_08008292|
	MOV      r6, #1
	ADD      r2, r5, #0
	EOR      r2, r6
	EOR      r6, r4
	LSL      r6, r6, #5
	LSL      r2, r2, #0xb
	ADD      r2, r2, r6
	MOV      ip, r2
	LDR      r2, [sp, #0x18]
	LDR      r6, [pc, #0x26c]
	LSL      r2, r2, #0x1c
	LSR      r7, r2, #0x1b
	MOV      r2, #0x20
	ADD      ip, r6
	SUB      r6, r2, r7
	LDR      r2, [sp, #0x1c]
	STR      r6, [sp, #0xc]
	LSL      r2, r2, #0x1b
	LSR      r2, r2, #0x1b
	LSL      r6, r2, #6
	ADD      r6, ip
	MOV      ip, r6
	ADD      ip, r7
	LDR      r6, [r0, #8]
	MOV      lr, r7
	LSL      r7, r2, #5
	ADD      r6, r6, r7
	ADD      lr, r6
	CMP      r2, #0x20
	BGE      |loc_08008292|
	LDR      r6, [sp, #0xc]
	LDR      r7, [pc, #0x244]
	LSL      r6, r6, #0xf
	LSR      r6, r6, #0x10
	STR      r6, [sp, #0x4c]
|loc_0800826E|
	MOV      r6, lr
	STR      r6, [r7]
	MOV      r6, ip
	STR      r6, [r7, #4]
	LDR      r6, [sp, #0x4c]
	STRH     r6, [r7, #8]
	MOV      r6, #1
	LSL      r6, r6, #0xf
	STRH     r6, [r7, #0xa]
	MOV      r6, lr
	ADD      r6, #0x20
	MOV      lr, r6
	MOV      r6, ip
	ADD      r6, #0x40
	ADD      r2, #1
	CMP      r2, #0x20
	MOV      ip, r6
	BLT      |loc_0800826E|
|loc_08008292|
	MOV      r6, #1
	ADD      r2, r5, #0
	EOR      r2, r6
	LSL      r2, r2, #0xb
	STR      r2, [sp, #0x48]
	LSL      r6, r4, #5
	ADD      r2, r2, r6
	MOV      ip, r2
	LDR      r6, [pc, #0x204]
	LDR      r2, [sp, #0x10]
	ADD      ip, r6
	LDR      r6, [sp, #0x14]
	LSL      r7, r6, #1
	SUB      r2, r2, r6
	LSL      r6, r2, #1
	STR      r6, [sp, #0xc]
	MOV      lr, r7
	BEQ      |loc_080082FE|
	LDR      r2, [sp, #0x1c]
	LSL      r2, r2, #0x1b
	LSR      r2, r2, #0x1b
	LSL      r6, r2, #6
	ADD      r6, ip
	MOV      ip, r6
	LDR      r6, [r0, #0xc]
	LSL      r7, r2, #5
	ADD      r6, r6, r7
	ADD      ip, lr
	ADD      lr, r6
	CMP      r2, #0x20
	BGE      |loc_080082FE|
	LDR      r6, [sp, #0xc]
	LDR      r7, [pc, #0x1d8]
	LSL      r6, r6, #0xf
	LSR      r6, r6, #0x10
	STR      r6, [sp, #0x44]
|loc_080082DA|
	MOV      r6, lr
	STR      r6, [r7]
	MOV      r6, ip
	STR      r6, [r7, #4]
	LDR      r6, [sp, #0x44]
	STRH     r6, [r7, #8]
	MOV      r6, #1
	LSL      r6, r6, #0xf
	STRH     r6, [r7, #0xa]
	MOV      r6, lr
	ADD      r6, #0x20
	MOV      lr, r6
	MOV      r6, ip
	ADD      r6, #0x40
	ADD      r2, #1
	CMP      r2, #0x20
	MOV      ip, r6
	BLT      |loc_080082DA|
|loc_080082FE|
	LDR      r2, [sp, #0x20]
	CMP      r2, #0x10
	BLE      |Dma_Start3Second|
	B        |loc_08008308|
