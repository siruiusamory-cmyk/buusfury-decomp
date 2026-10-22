	CODE16
|sub_08030BCE|
	LDR      r0, [r5]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	BEQ      |loc_08030BF0|
	LDR      r0, [r4, #0x54]
	CMP      r0, #0
	BEQ      |loc_08030BE4|
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_08030BE4|
	LDR      r0, [r4, #0x5c]
	CMP      r0, #0
	BEQ      |loc_08030BEE|
	STR      r6, [r4, #0x60]
	B        |loc_08030BF0|
|loc_08030BEE|
	STR      r7, [r4, #0x60]
|loc_08030BF0|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
	LDR      r1, [r0, #0x58]
	MOV      r3, #0x10
	ADD      r1, #1
	ADD      r2, r1, #0
	STR      r1, [r0, #0x58]
	LDR      r1, [pc, #0x2f4]
	STRB     r2, [r1, #2]
	LDR      r2, [r0, #0x58]
	SUB      r2, r3, r2
	STRB     r2, [r1, #3]
	LDR      r1, [r0, #0x58]
	CMP      r1, #0x10
	BLT      |loc_08030C12|
	LDR      r1, [pc, #0x2f8]
	STR      r1, [r0, #0x60]
|loc_08030C12|
	MOV      r0, #0
	BX       lr
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	SUB      sp, #0x64
	ADD      r6, r0, #0
	BNE      |Bg_WriteScroll0AndBlendAlpha|
	MOV      r0, #0x64
	BL       |GBARam_Malloc|
	ADD      r6, r0, #0
	BNE      |Bg_WriteScroll0AndBlendAlpha|
	ADD      r0, r6, #0
	ADD      sp, #0x6c
	POP      {r4, r5, r6, r7, pc}
