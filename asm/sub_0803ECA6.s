	CODE16
|sub_0803ECA6|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_0803E4E4|
	MOV      r0, #0x5e
	LDRB     r0, [r0, r4]
	MOV      r1, #0x49
	STRB     r0, [r1, r4]
	STRB     r0, [r4, #0x13]
	LDRB     r0, [r4, #0x10]
	MOV      r1, #0x10
	ORR      r0, r1
	STRB     r0, [r4, #0x10]
	POP      {r4, pc}
|sub_0803ECC2|
|unk_0803ECC2|
	INCBIN	baserom.gba_0x3ecc2_0x3ecc6.extracted
