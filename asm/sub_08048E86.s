	CODE16
|sub_08048E86|
	LSR      r4, r0, #0x20
	CMP      r3, #0xd4
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0x14]
	PUSH     {r3, lr}
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_08048EA2|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |Thunk_JumpRegister1|
|loc_08048EA2|
	POP      {r3, pc}
|sub_08048EA4|
|unk_08048EA4|
	INCBIN	baserom.gba_0x48ea4_0x48ea6.extracted
