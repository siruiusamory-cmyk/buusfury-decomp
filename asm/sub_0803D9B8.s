	CODE16
|sub_0803D9B8|
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	LDRH     r0, [r0]
	LSL      r0, r0, #0x1b
	BPL      |loc_0803D9C6|
	LDR      r0, [pc, #0xb0]
	BX       lr
|loc_0803D9C6|
	MOV      r0, #3
	LSL      r0, r0, #0x19
	BX       lr
	PUSH     {r4, r5, r6}
	LDR      r3, [r0]
	LDR      r4, [r0, #8]
	MOV      r5, #0x20
	SUB      r4, r4, r3
	SUB      r6, r5, r4
	LDR      r4, [r0, #4]
	LSL      r5, r4, #5
	ADD      r3, r5, r3
	LSL      r3, r3, #1
	ADD      r3, r3, r1
	LDR      r1, [r0, #0xc]
	CMP      r1, r4
	BLE      |loc_0803DA0C|
	LSL      r5, r2, #0x10
	LSR      r5, r5, #0x10
	LSL      r6, r6, #1
|loc_0803D9EE|
	LDR      r1, [r0]
	LDR      r2, [r0, #8]
	CMP      r2, r1
	BLE      |loc_0803DA02|
|loc_0803D9F6|
	STRH     r5, [r3]
	LDR      r2, [r0, #8]
	ADD      r3, #2
	ADD      r1, #1
	CMP      r2, r1
	BGT      |loc_0803D9F6|
|loc_0803DA02|
	LDR      r1, [r0, #0xc]
	ADD      r3, r6, r3
	ADD      r4, #1
	CMP      r1, r4
	BGT      |loc_0803D9EE|
|loc_0803DA0C|
	POP      {r4, r5, r6}
	BX       lr
	PUSH     {r4, r5, r6}
	LDR      r3, [r0]
	LDR      r4, [r0, #8]
	MOV      r5, #0x20
	SUB      r4, r4, r3
	SUB      r4, r5, r4
	LDR      r5, [r0, #4]
	LSL      r6, r5, #5
	ADD      r3, r6, r3
	LSL      r3, r3, #1
	ADD      r3, r3, r1
	LDR      r1, [r0, #0xc]
	CMP      r1, r5
	BLE      |loc_0803DA50|
	LSL      r6, r4, #1
|loc_0803DA2E|
	LDR      r1, [r0]
	LDR      r4, [r0, #8]
	CMP      r4, r1
	BLE      |loc_0803DA46|
|loc_0803DA36|
	ADD      r4, r2, #0
	STRH     r4, [r3]
	LDR      r4, [r0, #8]
	ADD      r3, #2
	ADD      r2, #1
	ADD      r1, #1
	CMP      r4, r1
	BGT      |loc_0803DA36|
|loc_0803DA46|
	LDR      r1, [r0, #0xc]
	ADD      r3, r6, r3
	ADD      r5, #1
	CMP      r1, r5
	BGT      |loc_0803DA2E|
|loc_0803DA50|
	POP      {r4, r5, r6}
	BX       lr
	MOV      r2, #1
	LSL      r2, r2, #0xa
	PUSH     {r3, lr}
	LSR      r1, r2, #1
	BL       |inc_0x049120_0x055620| + 0xc
	POP      {r3, pc}
	MOV      r2, #1
	ADD      r1, r0, #0
	MOV      r0, #7
	LSL      r2, r2, #0xa
	PUSH     {r3, lr}
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0x18
	POP      {r3, pc}
|sub_0803DA74|
|unk_0803DA74|
	INCBIN	baserom.gba_0x3da74_0x3da76.extracted
|sub_0803DA76|
	DCW      0x0600
