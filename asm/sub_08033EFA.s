	CODE16
|sub_08033EFA|
	LSR      r4, r0, #0x20
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	ADD      r2, #0x20
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08033F20|
	LDR      r1, [pc, #8]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08033F20|
	POP      {r4, pc}
|sub_08033F22|
|unk_08033F22|
	INCBIN	baserom.gba_0x33f22_0x33f26.extracted
