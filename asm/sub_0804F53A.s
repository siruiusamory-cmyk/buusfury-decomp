	CODE16
|sub_0804F53A|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_0804F54E|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0804F54E|
	POP      {r3, pc}
|sub_0804F550|
|unk_0804F550|
		MOV r0, #0
		BX       lr
		BX       lr
	INCBIN  baserom.gba_0x4f556_0x4f558.extracted
		BX       lr
