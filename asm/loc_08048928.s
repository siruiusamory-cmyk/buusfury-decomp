	CODE16
|loc_08048928|
	LDR      r1, [pc, #0x10]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x10]
|loc_08048930|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
|loc_0804893A|
	DCW      0x0000
	DCW      0x30ec,0x0300,0xb7d0
|loc_08048942|
	LSR      r4, r0, #0x20
	ADR      r1, |loc_08048A68|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048950|
|unk_08048950|
	INCBIN	baserom.gba_0x48950_0x48952.extracted
