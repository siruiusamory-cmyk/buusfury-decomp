	CODE16
|unk_080549B8|
	CODE32
	ADD      ip, r0, #128, 16
	TST      ip, #0x7f000000
	BEQ      |arm_080549DC|
	MOVS     r1, r0, ASR #3
	MOV      r0, r0, LSL #0x1d
	ADD      r1, r1, #224, 10
	BXPL     lr
	SUB      r1, r1, #112, 8
	BX       lr
|arm_080549DC|
	TST      ip, #128, 16
	BEQ      |arm_08054A00|
	MOV      r1, r0
	MOVS     r0, r0, LSL #1
	BXEQ     lr
	AND      r2, r1, #128, 8
	ADD      r3, r2, #0x36800000
	MOV      r1, r1, LSL #3
	B        |arm_0805400C|
|arm_08054A00|
	MOVS     r2, r0, LSL #9
	LDR      ip, [pc, #0x10]
	BNE      |arm_08054A4C|
	B        |arm_08054A10|
|arm_08054A10|
	ORR      r1, r0, #112, 16
	MOV      r0, r2
	CODE16
	CODE16
	EXPORT |sub_08054A18|
|sub_08054A18|
|unk_08054A18|
	INCBIN	baserom.gba_0x54a18_0x54a1c.extracted
	LSL      r0, r3, #0
	LSL      r0, r0, #0x10
	BX       pc
	LSL      r0, r0, #0
