	CODE16
|Object_ClearFields3|
	CMP      r2, #0
	BGE      |loc_080216F2|
	CMP      r1, #0x10
	BGE      |loc_080216F2|
	MOV      r1, #2
	STR      r1, [r0, #0x38]
|loc_080216F2|
	LDR      r3, [pc, #0x34]
	LSL      r2, r4, #3
	ADD      r3, #0xa
	ADD      r2, r2, r3
	LDR      r4, [r2]
	LDR      r3, [r0, #0x34]
	LDR      r2, [r2, #4]
	MUL      r4, r3
	MUL      r2, r3
	STR      r2, [sp, #4]
	LDR      r3, [sp, #4]
	ADD      r2, r4, #0
	STR      r4, [sp]
	LDR      r4, [r0, #0x48]
	ADD      r1, r0, #0
	LDR      r0, [r0, #0x4c]
	ADD      r2, r4, r2
	ADD      r0, r0, r3
	STR      r0, [sp, #4]
	ADD      r1, #0x2c
	ADD      r0, r2, #0
	STR      r2, [sp]
	LDR      r2, [sp, #4]
	STMIA    r1!, {r0, r2}
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
|sub_08021728|
|unk_08021728|
	INCBIN	baserom.gba_0x21728_0x2172a.extracted
	CODE16
|dat_0802172A|
	DCW      0x0872
	DCW      0x9680
	DCW      0x0804
|unk_08021730|
	INCBIN	baserom.gba_0x21730_0x21732.extracted
|dat_08021732|
	DCW      0x0804
	DCW      0x0000
	DCW      0x0601
	DCW      0xca80
	DCW      0x0804
|unk_0802173C|
	INCBIN	baserom.gba_0x2173c_0x2173e.extracted
|dat_0802173E|
	DCW      0x0804
