	CODE16
|sub_0802BDAA|
|unk_0802BDAA|
		MOV r2, #0xf
		BIC r2, r1
		DCW     0xD105
		LDR r1, [r0, #0x1c]
		SUB r1, #1
		STR r1, [r0, #0x1c]
		LDR r1, [r0, #0x24]
		SUB r1, #1
		STR r1, [r0, #0x24]
	INCBIN  baserom.gba_0x2bdbc_0x2bdbe.extracted
|sub_0802BDBE|
|unk_0802BDBE|
	INCBIN	baserom.gba_0x2bdbe_0x2bdc2.extracted
	LSL      r0, r0, #0
|unk_0802BDC4|
	INCBIN	baserom.gba_0x2bdc4_0x2bdc6.extracted
	LSR      r4, r0, #0x20
	SUB      r2, #0x10
	LSR      r5, r6, #1
	LDR      r2, [pc, #0x20]
	LDR      r1, [r1, #4]
	LDR      r2, [r2]
	ADD      r2, #0x80
	LDR      r2, [r2, #0x10]
	LDR      r0, [r0, #8]
	LSL      r0, r0, #0xa
	CMP      r2, #0
	BEQ      |loc_0802BDE6|
	ADD      r1, #0xff
	ADD      r1, #0xad
	STR      r0, [r1]
	BX       lr
|loc_0802BDE6|
	ADD      r1, #0xff
	ADD      r1, #0x81
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	SUB      r2, #0x14
	LSR      r5, r6, #1
	PUSH     {r4, r5}
	LDR      r2, [r1, #4]
	SUB      sp, #8
	ADD      r2, #0x24
	LDR      r4, [r2, #8]
	LDR      r5, [r2]
	LDR      r1, [r2, #0xc]
	SUB      r4, r4, r5
	LDR      r5, [r2, #4]
	STR      r4, [sp]
	SUB      r1, r1, r5
	STR      r1, [sp, #4]
	ADD      r1, r4, #0
	ADD      r3, r0, #0
	ADD      r3, #0x10
	LDR      r4, [sp, #4]
	STMIA    r3!, {r1, r4}
	LDR      r1, [r0, #8]
	LDR      r3, [r2]
	SUB      r1, r1, r3
	LDR      r3, [r0, #0xc]
	LDR      r4, [r2, #4]
	STR      r1, [sp]
	SUB      r3, r3, r4
	STR      r3, [sp, #4]
	LDR      r4, [r2]
	LDR      r2, [r2, #4]
	ADD      r5, r1, #0
	LSL      r2, r2, #8
	STR      r2, [r0, #0x24]
	LSL      r4, r4, #8
	STR      r4, [r0, #0x20]
	MOV      r2, #0x2c
	STR      r2, [r0, #0x28]
	LDR      r2, [pc, #0x88]
	ADD      r1, r3, #0
	LDR      r3, [pc, #0x84]
	MUL      r2, r5
	ASR      r2, r2, #8
	STR      r2, [r0, #0x18]
	LDR      r2, [pc, #0x80]
	MUL      r1, r3
	ADD      r1, r1, r2
	MOV      r2, #1
	LSL      r2, r2, #9
	ASR      r1, r1, #8
	SUB      r1, r1, r2
	STR      r1, [r0, #0x1c]
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
	PUSH     {r4, r5}
	LDR      r2, [r0, #0x1c]
	SUB      sp, #8
	ADD      r2, #0x20
	STR      r2, [r0, #0x1c]
	LDR      r3, [r0, #0x20]
	LDR      r4, [r0, #0x18]
	ADD      r3, r3, r4
	STR      r3, [r0, #0x20]
	LDR      r3, [r0, #0x24]
	ADD      r2, r3, r2
	STR      r2, [r0, #0x24]
	LDR      r2, [r0, #0x28]
	SUB      r2, #1
	STR      r2, [r0, #0x28]
	BNE      |loc_0802BE8A|
	LDR      r3, [r0, #8]
	LDR      r4, [r0, #0xc]
	LSL      r3, r3, #8
	LSL      r4, r4, #8
	MOV      r2, #1
	STR      r2, [r0, #0x2c]
	STR      r3, [r0, #0x20]
	STR      r4, [r0, #0x24]
|loc_0802BE8A|
	LDR      r1, [r1, #4]
	LDR      r3, [r0, #0x20]
	LDR      r4, [r0, #0x24]
	ASR      r3, r3, #8
	STR      r3, [r1, #0x24]
	ASR      r4, r4, #8
	STR      r4, [r1, #0x28]
	ADD      r2, r1, #0
	ADD      r2, #0x24
	ADD      r3, r2, #0
	LDR      r2, [r2, #4]
	LDR      r4, [r1, #0x24]
	LDR      r5, [r0, #0x10]
	LDR      r0, [r0, #0x14]
	ADD      r4, r4, r5
	ADD      r0, r2, r0
	STR      r0, [sp, #4]
	LDR      r2, [sp, #4]
	STR      r4, [sp]
	ADD      r3, #8
	STR      r2, [r3, #4]
	STR      r4, [r3]
	LDR      r0, [r1, #0x30]
	LDR      r2, [r1, #0x18]
	ADD      r0, r0, r2
	STR      r0, [r1, #4]
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
|loc_0802BEC4|
	DCW      0x05d3
	DCW      0x0000,0x45a0,0xffff
