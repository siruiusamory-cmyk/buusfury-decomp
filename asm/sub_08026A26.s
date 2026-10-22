	CODE16
|sub_08026A26|
	PUSH     {r4, r5, r6, lr}
	LDR      r0, [pc, #0x110]
	SUB      sp, #0x30
	MOV      r5, #0
	LDR      r0, [r0]
	ADD      r4, r1, #0
	LDR      r2, [pc, #0x110]
	ADD      r1, r5, #0
	CMP      r4, #0
	STR      r5, [sp, #0x28]
	LDR      r6, [pc, #0x104]
	STR      r0, [sp, #0x2c]
	STR      r2, [sp, #0x24]
	BEQ      |loc_08026A48|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_08026A48|
	ADD      r0, sp, #0x24
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	LDR      r0, [pc, #0xec]
	LDR      r0, [r0]
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #8]
	ADD      r0, r1, #0
	STR      r0, [sp, #0xc]
	STR      r1, [sp, #4]
	LDR      r1, [sp, #8]
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	STR      r1, [sp, #0x10]
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #8]
	ADD      r0, r1, #0
	STR      r1, [sp, #4]
	LDR      r1, [sp, #8]
	STR      r0, [sp, #0x14]
	STR      r1, [sp, #0x18]
	LDR      r1, [sp, #0x14]
	LDR      r0, [sp, #0xc]
	LDR      r2, [sp, #0x18]
	SUB      r1, r0, r1
	LDR      r0, [sp, #0x10]
	STR      r1, [sp, #4]
	SUB      r0, r0, r2
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x20]
	STR      r1, [sp, #0x1c]
	LDRB     r1, [r4, #0x10]
	MOV      r0, #1
	CMP      r1, #2
	BCS      |loc_08026AA2|
	MOV      r0, #0
|loc_08026AA2|
	LSL      r0, r0, #2
	ADD      r1, sp, #0x1c
	ADD      r0, r0, r1
	STR      r5, [r0]
	MOV      r0, #0x7f
	LDR      r1, [sp, #0x1c]
	MVN      r0, r0
	CMP      r1, r0
	BGE      |loc_08026AB6|
	STR      r0, [sp, #0x1c]
|loc_08026AB6|
	LDR      r2, [sp, #0x1c]
	MOV      r1, #0x80
	CMP      r2, #0x80
	BLE      |loc_08026AC0|
	STR      r1, [sp, #0x1c]
|loc_08026AC0|
	LDR      r2, [sp, #0x20]
	CMP      r2, r0
	BGE      |loc_08026AC8|
	STR      r0, [sp, #0x20]
|loc_08026AC8|
	LDR      r0, [sp, #0x20]
	CMP      r0, #0x80
	BLE      |loc_08026AD0|
	STR      r1, [sp, #0x20]
|loc_08026AD0|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08026AF0|
	LDR      r1, [pc, #0x54]
	LDR      r3, [pc, #0x54]
	STR      r1, [r0]
	LDR      r1, [sp, #0x1c]
	MUL      r1, r3
	ASR      r1, r1, #8
	STR      r1, [r0, #4]
	LDR      r1, [sp, #0x20]
	MUL      r1, r3
	ASR      r1, r1, #8
	STR      r1, [r0, #8]
|loc_08026AF0|
	ADD      r5, r0, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [sp, #0x28]
	STR      r6, [sp, #0x24]
	CMP      r0, #0
	BEQ      |loc_08026B16|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08026B16|
	ADD      sp, #0x30
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
|sub_08026B2C|
|unk_08026B2C|
	INCBIN	baserom.gba_0x26b2c_0x26b32.extracted
