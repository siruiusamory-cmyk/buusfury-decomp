	CODE16
|sub_080299AC|
	EXPORT |sub_080299AC|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r4, #0
	LDR      r1, [pc, #0x24]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	ADD      r0, r4, #0
|unk_080299BA|
	INCBIN	baserom.gba_0x299ba_0x299bc.extracted
|loc_080299BC|
|unk_080299BC|
	INCBIN	baserom.gba_0x299bc_0x299be.extracted
	POP      {r4, pc}
|sub_080299C0|
|unk_080299C0|
		MOV r0, #1
		BX       lr
