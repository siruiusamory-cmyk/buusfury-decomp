	CODE16
|sub_0803DFE0|
	ADD      r4, sp, #0x200
	ADD      r0, r4, #0
	BL       |loc_0803DADA|
	ADD      r3, sp, #0x200
	STRB     r6, [r3, #3]
	MOV      r1, #0xdc
	ADD      r0, r4, #0
	LDR      r2, [sp, #0x234]
	BL       |loc_0803DD66|
	MOV      r0, #5
	LDR      r1, [pc, #0x1c]
	LSL      r0, r0, #0x18
	MOV      r2, #0x20
	ADD      r1, #4
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #0x4b
	LSL      r2, r2, #9
	MOV      r0, #3
	LSL      r0, r0, #0x19
	LDR      r1, [sp, #0x224]
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0803E012|
	B        |loc_0803E012|
|sub_0803E014|
|unk_0803E014|
	INCBIN	baserom.gba_0x3e014_0x3e016.extracted
	CODE16
|dat_0803E016|
	DCW      0x0400
	DCW      0x5b94
	DCW      0x087b
	DCW      0x0404
	DCW      0x0000
	DCW      0xf5a5
	DCW      0x0803
|loc_0803E024|
	DCW      0x0041
	DCW      0x0073
	DCW      0x0073
	DCW      0x0065
	DCW      0x0072
	DCW      0x0074
	DCW      0x0069
	DCW      0x006f
	DCW      0x006e
	DCW      0x0020
	DCW      0x0046
	DCW      0x0061
	DCW      0x0069
	DCW      0x006c
	DCW      0x0075
	DCW      0x0072
	DCW      0x0065
	DCW      0x0021
	DCW      0x0000
	DCW      0x0000
|loc_0803E04C|
	DCW      0x0025
	DCW      0x0053
	DCW      0x0000
	DCW      0x0000
|loc_0803E054|
	DCW      0x0046
	DCW      0x0069
	DCW      0x006c
	DCW      0x0065
	DCW      0x000a
	DCW      0x0020
	DCW      0x0020
	DCW      0x0000
|loc_0803E064|
	DCW      0x000a
	DCW      0x004c
	DCW      0x0069
	DCW      0x006e
	DCW      0x0065
	DCW      0x000a
	DCW      0x0000
	DCW      0x0000
|loc_0803E074|
	DCW      0x0020
	DCW      0x0020
	DCW      0x0025
	DCW      0x0064
	DCW      0x000a
	DCW      0x000a
	DCW      0x0000
	DCW      0x0000
|loc_0803E084|
	DCW      0x0043
	DCW      0x006f
	DCW      0x006e
	DCW      0x0064
	DCW      0x0069
	DCW      0x0074
	DCW      0x0069
	DCW      0x006f
	DCW      0x006e
	DCW      0x000a
	DCW      0x0020
	DCW      0x0020
	DCW      0x0000
	DCW      0x0000
	DCW      0x0045
	DCW      0x0072
	DCW      0x0072
	DCW      0x006f
	DCW      0x0072
	DCW      0x000a
	DCW      0x0020
	DCW      0x0020
	DCW      0x0000
	DCW      0x0000
	DCW      0x4770

