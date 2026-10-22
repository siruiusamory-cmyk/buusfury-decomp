	CODE16
|sub_08048A56|
	LSL      r0, r0, #0xc
|loc_08048A58|
	LDR      r6, [sp, #0x2b0]
	LSR      r4, r0, #0x20
	STMIA    r2!, {r2, r7}
	LSR      r4, r0, #0x20
	ADD      r2, sp, #0xf0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0xc]
	LDR      r0, [pc, #0x10]
|loc_08048A68|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
|loc_08048A72|
	DCW      0x0000
	DCW      0x3158,0x0300,0xb788
|loc_08048A7A|
	LSR      r4, r0, #0x20
	ADR      r1, |loc_08048AC0|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
|loc_08048A84|
	STR      r0, [r1]
	BX       lr
|sub_08048A88|
|unk_08048A88|
	INCBIN	baserom.gba_0x48a88_0x48a8a.extracted
