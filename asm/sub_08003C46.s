	CODE16
|sub_08003C46|
	LSR      r5, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ASR      r4, r0, #0x20
	LSL      r0, r0, #0xc
	MOV      r1, #0
|loc_08003C52|
	LDR      r3, [r0]
	LSL      r1, r1, #7
	LDRB     r2, [r3]
	ADD      r3, #1
	STR      r3, [r0]
	LSL      r3, r2, #0x19
	LSR      r3, r3, #0x19
	ADD      r1, r1, r3
	LSL      r2, r2, #0x18
	BMI      |loc_08003C52|
	LSL      r0, r1, #0x1f
	BPL      |sub_08003C70|
	ASR      r0, r1, #1
|unk_08003C6C|
	INCBIN	baserom.gba_0x3c6c_0x3c6e.extracted
	BX       lr
