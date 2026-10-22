	CODE16
|sub_0804851A|
	LSL      r0, r0, #0xc
	STR      r7, [sp, #0x390]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x14]
	MOV      r0, #4
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x14]
	STR      r0, [r1]
	ADD      r1, #8
	MOV      r0, #4
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0xc]
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	CMP      r3, #0xb4
	LSL      r0, r0, #0xc
	LDMIA    r4!, {r3, r4, r6}
	LSR      r4, r0, #0x20
	BGT      |loc_0804848C|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804854C|
|unk_0804854C|
	INCBIN	baserom.gba_0x4854c_0x4854e.extracted
