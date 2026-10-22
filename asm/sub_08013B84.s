	CODE16
|sub_08013B84|
|unk_08013B84|
		ADD r3, #1
		CMP r5, r3
		BGT      |inc_0x0158_0x143f2| + 0x13a06
|loc_08013B8A|
|unk_08013B8A|
		MOV r3, #0
		MOV r2, #0xff
		ADD r2, #0x81
		ADR      r1, |inc_0x0158_0x143f2| + 0x13a54
		LDR r0, [pc, #0x34]
	INCBIN  baserom.gba_0x13b94_0x13b96.extracted
|sub_08013B96|
|unk_08013B96|
	INCBIN	baserom.gba_0x13b96_0x13b9a.extracted
	LSL      r0, r0, #0
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	STRB     r0, [r0, #2]
	LSR      r3, r5, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	LDMIA    r1!, {r3, r5, r6, r7}
	LSR      r7, r6, #1
	SUB      r2, #0x54
	STRH     r4, [r3, r5]
	STRB     r7, [r5, #0x15]
	STR      r2, [r6, #0x34]
	LDRB     r5, [r4, r1]
	LDR      r3, [r0, #4]
	STRB     r1, [r4, #9]
	STR      r1, [r4, #0x34]
	STR      r4, [r6, #0x54]
	ADD      r2, lr
	STRB     r1, [r4, #0x11]
	CMP      r6, #0x61
	STRB     r3, [r4, #1]
	LSL      r0, r6, #1
	STRB     r0, [r0, #0x10]
	LSR      r3, r5, #1
