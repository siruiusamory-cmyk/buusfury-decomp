	CODE16
|sub_08004DC0|
	MOV      r1, #0
|loc_08004DC2|
	LSL      r2, r1, #7
	LDR      r2, [r0, r2]
	CMP      r2, #0
	BEQ      |loc_08004DCE|
	MOV      r0, #1
	BX       lr
|loc_08004DCE|
	ADD      r1, #1
	CMP      r1, #3
	BLT      |loc_08004DC2|
	MOV      r0, #0
	BX       lr
	PUSH     {r3, lr}
	MOV      r3, #0
	LSL      r2, r1, #7
	STR      r3, [r0, r2]
	ADD      r0, r2, r0
	STR      r3, [r0, #0xc]
	ADD      r0, r1, #0
	BL       |loc_08004A3A|
	POP      {r3, pc}
|sub_08004DEC|
|unk_08004DEC|
	INCBIN	baserom.gba_0x4dec_0x4dee.extracted
