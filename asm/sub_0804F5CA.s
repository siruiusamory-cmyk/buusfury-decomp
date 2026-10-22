	CODE16
|sub_0804F5CA|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	BL       |inc_0x0158_0x143f2| + 0xf7fc
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r0, #1
	ADD      r1, #0xff
	ADD      r1, #0xc1
	STR      r0, [r1, #0xc]
	BX       lr
|sub_0804F5E2|
|unk_0804F5E2|
	INCBIN  baserom.gba_0x4f5e2_0x4f5e4.extracted
		BX       lr
