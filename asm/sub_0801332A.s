	CODE16
|sub_0801332A|
	LSL      r0, r0, #0
	ADD      r3, #0xf8
	LSR      r4, r7, #0x20
	STR      r3, [sp, #0x350]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STMIA    r7!, {r2, r6}
	LSR      r4, r0, #0x20
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	BL       |Record_InitFields|
	MOV      r0, #0
	MOV      r1, #0xff
	ADD      r1, #0xcd
	STR      r0, [r1, r4]
	POP      {r4, pc}
	ADD      r0, r1, #0
	LDRB     r1, [r1, #0x10]
	LDR      r2, [pc, #0x1c]
	ADD      r0, #0xff
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	ADD      r0, #0x81
	LDR      r2, [r0, #0x20]
	LDR      r3, [r1]
	ADD      r2, r2, r3
	STR      r2, [r0, #0x20]
	LDR      r2, [r0, #0x24]
	LDR      r1, [r1, #4]
	ADD      r1, r2, r1
	STR      r1, [r0, #0x24]
	BX       lr
	LSL      r0, r0, #0
	ADD      r4, #0xb0
	LSR      r4, r7, #0x20
	CMP      r0, #0x32
	BGE      |loc_08013380|
	MOV      r0, #0
	BX       lr
|loc_08013380|
	LDR      r1, [pc, #0x28c]
	CMP      r0, #0xc8
	BLE      |loc_08013390|
	MOV      r0, #9
	LSL      r0, r0, #6
	ADD      r0, r1, r0
	LDR      r0, [r0, #0x18]
	BX       lr
|loc_08013390|
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	SUB      r0, #0xff
	SUB      r0, #1
	LDR      r0, [r0, #0x38]
	BX       lr
