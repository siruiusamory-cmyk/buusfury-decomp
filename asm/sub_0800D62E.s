	CODE16
|sub_0800D62E|
	STRH     r2, [r0, #6]
	STRH     r3, [r0, #8]
	STRH     r5, [r0, #0xa]
	LDR      r0, [r4, #0x34]
	MOV      r2, #0
	SUB      r0, #0x80
	STR      r0, [r4, #0x34]
	LDR      r1, [r4, #0x30]
	ADD      r1, r1, r0
	STR      r1, [r4, #0x30]
	CMP      r1, #0
	BGE      |loc_0800D666|
|unk_0800D646|
	INCBIN	baserom.gba_0xd646_0xd648.extracted
	ASR      r1, r1, #1
	STR      r1, [r4, #0x30]
	LDR      r5, [r4, #0x34]
	MOV      r1, #1
|unk_0800D650|
	INCBIN	baserom.gba_0xd650_0xd652.extracted
	ASR      r5, r5, #1
	ADD      r0, r4, #0
	ADD      r0, #0x30
	LSL      r1, r1, #9
	ADD      r3, r7, #0
	CMP      r5, r1
	STR      r5, [r4, #0x34]
	BGE      |loc_0800D666|
	STR      r2, [r0]
	STR      r3, [r4, #0x40]
|loc_0800D666|
	LDR      r5, [pc, #0x210]
	LDR      r2, [r4, #0x50]
	LDR      r0, [r5, #0xc]
	ADD      r1, r4, #0
	ADD      r0, #0x28
	LDR      r3, [r0]
	ADD      r1, #0x28
	SUB      r2, r2, r3
	LDR      r3, [r4, #0x54]
	LDR      r6, [r0, #4]
	STR      r2, [sp, #0x34]
	SUB      r3, r3, r6
	STR      r3, [sp, #0x38]
	STR      r2, [r4, #0x58]
	STR      r3, [r4, #0x5c]
	LDR      r2, [r4, #0x18]
	LDR      r3, [r0]
	SUB      r2, r2, r3
	LDR      r3, [r4, #0x1c]
	LDR      r0, [r0, #4]
	STR      r2, [sp, #0x34]
	SUB      r0, r3, r0
	STR      r0, [sp, #0x38]
	ADD      r0, r2, #0
	LDR      r2, [sp, #0x38]
	STMIA    r1!, {r0, r2}
	LDR      r0, [r4, #0x30]
	LDR      r1, [r4, #0x2c]
	ASR      r0, r0, #0xa
	SUB      r0, r1, r0
	STR      r0, [r4, #0x2c]
	LDR      r0, [r5, #0xc]
	LDR      r1, [r4, #0x18]
	ADD      r0, #0x18
	LDR      r2, [r0, #8]
	CMP      r1, r2
	BGE      |sub_0800D6CE|
	LDR      r1, [r0]
	LDR      r2, [r4, #0x20]
	CMP      r1, r2
	BGE      |sub_0800D6CE|
	LDR      r1, [r4, #0x1c]
	LDR      r2, [r0, #0xc]
	CMP      r1, r2
	BGE      |sub_0800D6CE|
	LDR      r0, [r0, #4]
	LDR      r1, [r4, #0x24]
	CMP      r0, r1
	BGE      |sub_0800D6CE|
	MOV      r0, #1
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
