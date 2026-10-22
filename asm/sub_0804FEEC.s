	CODE16
|sub_0804FEEC|
	MOV      r0, #0
	MOV      r1, #1
	SUB      r0, r1, r0
	BX       lr
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_0804FF02|
	MOV      r0, #0
|loc_0804FF02|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	SUB      r0, r6, r4
	LSL      r0, r0, #0xc
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_0804FF1A|
	MOV      r0, #0
|loc_0804FF1A|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	ADD      r1, #0x58
	LSL      r0, r0, #0xc
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_0804FF32|
	MOV      r0, #0
|loc_0804FF32|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	ADD      r0, #0xec
	LSL      r0, r0, #0xc
	MOV      r0, #0
	BX       lr
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	ADD      r0, r1, #0
	ADD      r4, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_0804FF66|
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0804FF66|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	MOV      r0, #1
	BX       lr
	LDR      r0, [pc, #0xc]
	ADD      r1, #0xff
	LDR      r0, [r0, #4]
	ADD      r1, #0xc1
	STR      r0, [r1, #0x28]
	MOV      r0, #1
	BX       lr
	LSL      r0, r0, #0
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #0x18]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_0804FFA2|
	MOV      r0, #0
|loc_0804FFA2|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	ADD      r1, #0x4c
	LSL      r0, r0, #0xc
	MOV      r0, #1
	BX       lr
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_0804FFBE|
	MOV      r0, #0
|loc_0804FFBE|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	SUB      r0, r6, r4
	LSL      r0, r0, #0xc
|loc_0804FFC8|
	LDR      r0, [pc, #0xc]
	ADD      r1, #0xff
	LDR      r0, [r0, #4]
	ADD      r1, #0xc1
	STR      r0, [r1, #0x2c]
	MOV      r0, #1
	BX       lr
	LSL      r0, r0, #0
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	LDR      r2, [r0]
	LDR      r3, [r2, #0x18]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r0, #1
	BX       lr
|loc_0804FFF4|
	DCW      0x2001
	DCW      0x4770
|loc_0804FFF8|
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_08050006|
	MOV      r0, #0
|loc_08050006|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	ADD      r2, #0x64
	LSL      r0, r0, #0xc
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_0805001E|
	MOV      r0, #0
|loc_0805001E|
	SUB      r0, r2, r0
	BX       lr
	LSL      r0, r0, #0
	ADD      r1, #0x28
	LSL      r0, r0, #0xc
	MOV      r0, #1
	BX       lr
|sub_0805002C|
|unk_0805002C|
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
