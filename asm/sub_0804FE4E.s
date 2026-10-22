	CODE16
|sub_0804FE4E|
	LSL      r0, r0, #0
	MOV      r5, #0xe8
	LSR      r7, r0, #0x20
	PUSH     {r3, lr}
	LDR      r2, [r0]
	SUB      r2, #1
	STR      r2, [r0]
	SUB      r2, r2, r1
	BEQ      |loc_0804FE70|
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	ADD      r1, r0, #0
	ADD      r1, #8
	LSL      r2, r2, #2
	ADD      r0, #4
	BL       |Thunk_VramCopy|
|loc_0804FE70|
	POP      {r3, pc}
|sub_0804FE72|
|unk_0804FE72|
	INCBIN  baserom.gba_0x4fe72_0x4fe74.extracted
		BX       lr
	INCBIN  baserom.gba_0x4fe76_0x4fe78.extracted
		BX       lr
	INCBIN  baserom.gba_0x4fe7a_0x4fe7c.extracted
		BX       lr
