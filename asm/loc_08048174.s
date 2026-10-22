	CODE16
|loc_08048174|
	PUSH     {r3, lr}
	ADD      r3, sp, #0
	STRB     r0, [r3]
	MOV      r0, #3
	MOV      r1, sp
	SWI      0xab
	ADD      sp, #4
	POP      {r3}
	BX       r3
|sub_08048186|
|unk_08048186|
	INCBIN	baserom.gba_0x48186_0x4818a.extracted
