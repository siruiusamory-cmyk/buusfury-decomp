	CODE16
|sub_08048492|
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0x28]
	LDR      r1, [pc, #0x2c]
	STR      r0, [r1]
	MOV      r0, #3
	ADD      r1, #4
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x24]
	STR      r0, [r1]
	LDR      r0, [pc, #0x24]
	ADD      r1, #8
	STR      r0, [r1]
	MOV      r0, #3
	ADD      r1, #8
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x1c]
	STR      r0, [r1]
	ADD      r1, #8
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x18]
	STR      r0, [r1]
	BX       lr
|loc_080484C0|
	DCW      0xc384
	DCW      0x0804,0x2b38,0x0300,0xbef0,0x0804,0xc790,0x0804,0xc3a8
	DCW      0x0804,0xe00c,0x0804,0x4770
|loc_080484DA|
	LSL      r0, r0, #0
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
|loc_080484E0|
	STR      r0, [r1]
	BX       lr
|sub_080484E4|
|unk_080484E4|
	INCBIN	baserom.gba_0x484e4_0x484e6.extracted
