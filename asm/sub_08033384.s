	CODE16
|sub_08033384|
	ADD      r2, r1, #0
	ADD      r1, r0, #0
	MOV      r0, #0x85
	LSL      r0, r0, #2
	ADD      r1, #0xc
	ADD      r2, r2, r0
	PUSH     {lr}
	SUB      sp, #0x6c
	MOV      r0, #0
	STR      r0, [sp]
	STR      r0, [sp, #0x44]
	MOV      r0, sp
	BL       |inc_0x0158_0x143f2| + 0x3ee0
	ADD      sp, #0x6c
	POP      {pc}
|sub_080333A4|
|unk_080333A4|
	INCBIN	baserom.gba_0x333a4_0x333a6.extracted
