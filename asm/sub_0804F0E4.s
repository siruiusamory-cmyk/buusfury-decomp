	CODE16
|sub_0804F0E4|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_0804F0FE|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0804F0FE|
	POP      {r3, pc}
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_0804F112|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0804F112|
	POP      {r3, pc}
|sub_0804F114|
|unk_0804F114|
		BX       lr
	INCBIN  baserom.gba_0x4f116_0x4f118.extracted
		BX       lr
|sub_0804F11A|
	DCW      0x0000
