	CODE16
|sub_080175CA|
	LDR      r0, [pc, #0xc8]
	LDR      r1, [pc, #0xc8]
	MOV      r5, #0
	LDR      r6, [pc, #0xc8]
	LDR      r0, [r0, #4]
	ADD      r3, r5, #0
	MOV      r2, #0x40
	SUB      r1, #0xc
	ADD      r0, r0, r6
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r1, [r0, #0x20]
	ADD      r1, #2
	STR      r1, [r0, #0x20]
	LDR      r2, [r0, #0x18]
	CMP      r1, r2
	BLT      |loc_080175F6|
	SUB      r2, #1
	STR      r2, [r0, #0x20]
|loc_080175F6|
	STR      r5, [r0, #0x10]
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x90]
	LDR      r2, [pc, #0x90]
	LDR      r0, [r0]
	MOV      r4, #0
	LDRH     r1, [r0, #4]
	LDR      r2, [r2, #4]
	LSL      r0, r1, #0x1c
	LSR      r3, r0, #0x1f
	LDR      r0, [pc, #0x88]
	ADD      r0, r2, r0
	LDR      r2, [pc, #0x90]
	CMP      r3, #0
	BEQ      |loc_0801762C|
	ADD      r1, r2, #0
	ADD      r1, #0xff
	ADD      r1, #0xe1
	ADD      r3, r4, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #4
	POP      {r4, r5, r6, pc}
|loc_0801762C|
	MOV      r6, #1
	MOV      r3, #0x30
	AND      r1, r3
	BEQ      |loc_0801765A|
	ADD      r1, r2, #0
	ADD      r1, #0xff
	ADD      r1, #0xd5
	ADD      r3, r4, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r2, [r0, #0x20]
	EOR      r2, r6
	STR      r2, [r0, #0x20]
	LDR      r1, [r0, #0x18]
	CMP      r2, r1
	BLT      |loc_08017658|
	SUB      r1, #1
	STR      r1, [r0, #0x20]
|loc_08017658|
	STR      r4, [r0, #0x10]
|loc_0801765A|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r2, [r0, #0x18]
	CMP      r2, #0
	BNE      |loc_0801766C|
	MOV      r0, #0
	BX       lr
|loc_0801766C|
	LDR      r2, [r0, #0x20]
	LDR      r3, [r0, #0x1c]
	ADD      r0, #0x1c
	SUB      r2, r2, r3
	LSL      r2, r2, #0x1f
	LSR      r2, r2, #0x1f
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LSL      r2, r2, #5
	ADD      r2, #0x10
	STR      r2, [r1]
	LDMIA    r0!, {r0, r2}
	MOV      r3, #0x34
	SUB      r0, r2, r0
	ASR      r0, r0, #1
	MUL      r0, r3
	ADD      r0, #0x25
	STR      r0, [r1, #4]
	MOV      r0, #1
	BX       lr
|sub_08017694|
|unk_08017694|
	INCBIN	baserom.gba_0x17694_0x17696.extracted
