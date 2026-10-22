	CODE16
|sub_08018E28|
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08018E3C|
	LDR      r1, [pc, #0x10]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08018E3C|
	POP      {r4, pc}
	LSL      r0, r0, #0
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	CMP      r3, #0x9c
	LSL      r0, r0, #0xc
	LDR      r4, [sp, #0x160]
	LSR      r4, r0, #0x20
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x70]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	MOV      r0, #0
	POP      {r3, pc}
|sub_08018E5E|
|unk_08018E5E|
	INCBIN	baserom.gba_0x18e5e_0x18e62.extracted
