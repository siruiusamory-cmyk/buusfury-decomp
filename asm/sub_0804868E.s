	CODE16
|sub_0804868E|
	LSL      r0, r0, #0xc
	BVS      |loc_0804860C|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0xc]
	LDR      r0, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
|loc_080486A4|
	CMP      r7, #0xfc
	LSL      r0, r0, #0xc
	ADR      r7, |loc_080486AC|
	LSR      r4, r0, #0x20
|loc_080486AC|
	ADD      r2, sp, #0x390
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
|loc_080486B8|
	ADD      r1, #8
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BVS      |loc_080486A4|
	LSR      r4, r0, #0x20
	ADD      r0, #4
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r5, r6}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x10]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
|loc_080486DE|
	DCW      0x0000
	DCW      0x3014,0x0300,0xb740
|loc_080486E6|
	LSR      r4, r0, #0x20
	ADR      r0, |loc_08048A2C|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	STMIA    r2!, {r2, r3, r4, r5}
	LSR      r4, r0, #0x20
	ADD      r0, #0x1c
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x70
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048716|
|unk_08048716|
	INCBIN	baserom.gba_0x48716_0x4871a.extracted
