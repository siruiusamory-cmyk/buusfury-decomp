	CODE16
|sub_08033AF6|
	ADD      r0, r1, #0
	MOV      r2, #5
	LSL      r2, r2, #7
	ADD      r2, r0, r2
	MOV      r1, #0
	PUSH     {r3, lr}
	STR      r1, [r2, #0x14]
	LDRB     r1, [r0, #0x10]
	MOV      r2, #1
	EOR      r1, r2
	MOV      r2, #0x29
	LSL      r2, r2, #4
	ADD      r2, r0, r2
	STRB     r1, [r2]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r3, lr}
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08033B30|
	LDR      r1, [pc, #0x18]
	STR      r1, [r0]
|loc_08033B30|
	POP      {r3, pc}
|sub_08033B32|
|unk_08033B32|
; cited by 0x080339A6 (a pc-relative load targets 0x08033B34)
	DCB	0x00,0x00
	DCD	|unk_03001C34|
	DCD	|unk_03001B00|
	DCD	|unk_08759334|
	DCD	0x0804C3CC
	DCD	|unk_03000F90|
	DCD	0x0804AB04
		PUSH {r3, r4, r5, lr}
		ADD r4, r1, #0
		MOV r0, #0xff
		ADD r0, #0x13
		LDR r5, [r1, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |loc_08033B70|
		MOV r0, #0xff
		ADD r0, #0x15
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800EDF8|
		B        |loc_08033BAA|
|loc_08033B70|
		MOV r0, #0xca
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |inc_0x331c0_0x341c0| + 0x9cc
		MOV r0, #0xcb
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x33b86_0x33b88.extracted
|sub_08033B88|
|unk_08033B88|
	INCBIN	baserom.gba_0x33b88_0x33b8c.extracted
	MOV      r0, #0xff
	ADD      r0, #0x21
	LDR      r5, [r4, #0x58]
	BL       |inc_0x0158_0x143f2|
	CMP      r5, r0
	BNE      |loc_08033BAA|
	MOV      r0, #0xff
	ADD      r0, #0x22
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
|loc_08033BAA|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xf7cc
	POP      {r3, r4, r5, pc}
|sub_08033BB2|
|unk_08033BB2|
	INCBIN	baserom.gba_0x33bb2_0x33bb6.extracted
