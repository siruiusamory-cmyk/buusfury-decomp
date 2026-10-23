	CODE16
|sub_080500D8|
	LDR      r0, [r0, #4]
	ADD      r1, #0xff
	ADD      r1, #0xc1
	STR      r0, [r1, #0x24]
	MOV      r0, #1
	BX       lr
|sub_080500E4|
|unk_080500E4|
		BX       lr
|sub_080500E6|
	DCW      0x0000
