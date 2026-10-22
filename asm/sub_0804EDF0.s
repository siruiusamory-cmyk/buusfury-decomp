	CODE16
|sub_0804EDF0|
	LDR      r1, [pc, #0xc]
	MOV      r0, #1
	LDR      r1, [r1]
	CMP      r1, #0
	BGT      |loc_0804EDFC|
	MOV      r0, #0
|loc_0804EDFC|
	BX       lr
	LSL      r0, r0, #0
	CMP      r7, #0xe4
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x18]
	SUB      sp, #0x10
	LDR      r4, [r0]
	MOV      r0, sp
	BL       |inc_0x0158_0x143f2| + 0xfca2
	ADD      r4, #0x80
	LDR      r1, [r4, #0x30]
	MOV      r0, sp
	BL       |inc_0x0158_0x143f2| + 0x91cc
	ADD      sp, #0x10
	POP      {r4, pc}
|sub_0804EE20|
|unk_0804EE20|
	INCBIN	baserom.gba_0x4ee20_0x4ee22.extracted
