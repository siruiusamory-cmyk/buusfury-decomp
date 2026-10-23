	CODE16
|sub_0804E958|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x14
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r0, #0xc8
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #8]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r2, #0x48
	LSL      r0, r0, #0xc
	MOV      r1, #0
	STR      r1, [r0, #4]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	MOV      r0, #0x41
	LSL      r0, r0, #3
	ADD      r0, r1, r0
	ADD      r4, r1, #0
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r2}
	STMIA    r0!, {r2}
	LDR      r1, [r1]
	STR      r1, [r0]
	MOV      r0, #4
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r5, r0, #0
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0804E9DA|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r5}
	SUB      r0, #8
|loc_0804E9DA|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
|sub_0804E9E4|
|unk_0804E9E4|
	INCBIN	baserom.gba_0x4e9e4_0x4e9e6.extracted
|sub_0804E9E6|
	DCW      0x0804
