	CODE16
|sub_0804F7E2|
	LSL      r0, r0, #0
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	MOV      r0, #1
	SUB      sp, #0xc
	ADD      r5, sp, #4
	LSL      r0, r0, #9
	BL       |inc_0x03d784_0x041118| + 0x2348
	SUB      r0, #0xff
	SUB      r0, #1
	STR      r0, [sp, #4]
	MOV      r0, #1
	LSL      r0, r0, #9
	BL       |inc_0x03d784_0x041118| + 0x2348
	SUB      r0, #0xff
	SUB      r0, #1
	STR      r0, [sp, #8]
	LDR      r0, [r4, #0x10]
	ADD      r3, r5, #0
	ADD      r2, r4, #0
|unk_0804F80E|
	INCBIN	baserom.gba_0x4f80e_0x4f810.extracted
	ADD      r2, #8
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xd1b6
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xc]
	LDR      r0, [r0, #0x14]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0xc
	POP      {r4, r5, pc}
|sub_0804F826|
|unk_0804F826|
	INCBIN	baserom.gba_0x4f826_0x4f82a.extracted
