	CODE16
|sub_0803DEFA|
	PUSH     {r0, r1, r2, r3}
	PUSH     {r3, lr}
	ADD      r1, sp, #0x10
	STR      r1, [sp]
	LDR      r1, [sp, #0xc]
	MOV      r2, sp
	BL       |sub_0803DB7C|
	ADD      sp, #4
	POP      {r3}
	ADD      sp, #0x10
	BX       r3
|sub_0803DF12|
|unk_0803DF12|
	INCBIN	baserom.gba_0x3df12_0x3df14.extracted
