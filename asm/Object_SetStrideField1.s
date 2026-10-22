	CODE16
|Object_SetStrideField1|
	PUSH     {r4, r5}
	MOV      r4, #0x10
	MOV      r2, #0
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
|loc_0803F196|
	LSL      r3, r2, #1
	ADD      r3, r3, r2
	LSL      r3, r3, #5
	ADD      r3, r3, r0
	ADD      r3, #0x18
	MOV      r5, #0x34
	STRB     r1, [r5, r3]
	LDRB     r5, [r3, #0x10]
	ADD      r2, #1
	ORR      r5, r4
	STRB     r5, [r3, #0x10]
	CMP      r2, #0xf
	BLT      |loc_0803F196|
	POP      {r4, r5}
	BX       lr
|sub_0803F1B4|
|unk_0803F1B4|
	INCBIN	baserom.gba_0x3f1b4_0x3f1b6.extracted
