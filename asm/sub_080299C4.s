	CODE16
|sub_080299C4|
	LDR      r0, [pc, #0x10]
	ADD      r0, #4
	BX       lr
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [pc, #8]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	MOV      r0, #1
	POP      {r3, pc}
|sub_080299D8|
|unk_080299D8|
	INCBIN	baserom.gba_0x299d8_0x299da.extracted
