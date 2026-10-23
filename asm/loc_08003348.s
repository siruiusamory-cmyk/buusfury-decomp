	CODE16
|loc_08003348|
|unk_08003348|
		LDR r0, [pc, #0xfc]
		ADD r1, r7, r5
		LSL r2, r4, #0x1f
		LDR r0, [r0, #0x14]
		BEQ      |inc_0x0158_0x143f2| + 0x3200
	INCBIN  baserom.gba_0x3352_0x3354.extracted
|sub_08003354|
|unk_08003354|
	INCBIN	baserom.gba_0x3354_0x3358.extracted
	BL       |loc_08004396|
	ASR      r4, r4, #1
	ADD      r5, #1
	CMP      r5, r6
	BLT      |loc_08003348|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	MOV      r1, #1
	MOV      r0, #0
	BL       |loc_0802faba| + 0x1e6
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xd4]
	LDR      r0, [r0, #0x18]
	BL       |List_Append|
	POP      {r3, pc}
	LDR      r0, [pc, #0xc8]
	PUSH     {r3, lr}
	MOV      r2, #0
	MOV      r1, #0x1c
	LDR      r0, [r0, #0x18]
	BL       |loc_08011C0C|
	POP      {r3, pc}
	LDR      r0, [pc, #0xb8]
	MOV      r2, #0x13
	LDR      r1, [r0, #0x14]
	MOV      r0, #0
	LSL      r2, r2, #6
	ADD      r1, r1, r2
	STR      r0, [r1, #0x18]
	BX       lr
	LDR      r0, [pc, #0xa8]
	MOV      r2, #0x10
	LDR      r0, [r0, #0x14]
	LDRB     r1, [r0, #1]
	ORR      r1, r2
	STRB     r1, [r0, #1]
	BX       lr
	LDR      r0, [pc, #0x9c]
	MOV      r2, #0x10
	LDR      r0, [r0, #0x14]
	LDRB     r1, [r0, #1]
	BIC      r1, r2
	STRB     r1, [r0, #1]
	BX       lr
	LDR      r1, [pc, #0x8c]
	MOV      r2, #0x13
	LDR      r1, [r1, #0x14]
	LSL      r2, r2, #6
	ADD      r1, r1, r2
	LDR      r2, [r1, #0x18]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x64]
	LDR      r0, [r0, #0x14]
	BL       |loc_080043D8|
	POP      {r3, pc}
	LDR      r1, [pc, #0x5c]
	MOV      r3, #0x68
	LDR      r1, [r1, #0x14]
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	MOV      r2, #0x9f
	LSL      r2, r2, #3
	ADD      r1, r1, r2
	ADD      r1, #0x24
	LDR      r2, [r1]
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	BX       lr
	LDR      r0, [pc, #0x38]
	MOV      r2, #0x20
	LDR      r0, [r0, #0x14]
	LDRB     r1, [r0, #1]
	ORR      r1, r2
	STRB     r1, [r0, #1]
	BX       lr
	LDR      r0, [pc, #0x28]
	MOV      r2, #0x20
	LDR      r0, [r0, #0x14]
	LDRB     r1, [r0, #1]
	BIC      r1, r2
	STRB     r1, [r0, #1]
	BX       lr
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800343A|
	LDR      r1, [pc, #0x14]
	STR      r1, [r0]
|loc_0800343A|
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r3, pc}
|loc_08003440|
	DCW      0x1030
	DCW      0x0300,0xb704
|loc_08003446|
	LSR      r1, r7, #1
	LDR      r7, [pc, #0x2f0]
	LSR      r5, r0, #0x20
	PUSH     {r3, r4, r6, r7, lr}
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r1, [r0, #4]
	MOV      r0, #0
	BL       |inc_0x301c0_0x311c0| + 0x1c4
	BL       |inc_0x03d784_0x041118| + 0x11c
	SUB      r1, r0, #1
	LDR      r0, [r4]
	ADD      r2, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	STR      r2, [r4]
	STR      r1, [r0, #4]
	POP      {r4, pc}
	LDR      r0, [pc, #0x29c]
	PUSH     {r3, lr}
	MOV      r2, #0
	MOV      r1, #0x1f
	LDR      r0, [r0, #0x18]
	BL       |loc_08011C0C|
	POP      {r3, pc}
	PUSH     {r4, r5, r6, lr}
	MOV      r5, #0x9f
	LDR      r6, [pc, #0x288]
	MOV      r4, #0
	LSL      r5, r5, #3
|loc_08003494|
	MOV      r1, #0x68
	LDR      r0, [r6, #0x14]
	MUL      r1, r4
	ADD      r0, r1, r0
	ADD      r0, r0, r5
	LDRH     r2, [r0, #0x18]
	STRH     r2, [r0, #0x16]
	LDRH     r2, [r0, #0x1c]
	STRH     r2, [r0, #0x1a]
	LDRB     r1, [r0, #0x13]
	LSL      r1, r1, #0x1f
	BPL      |loc_080034B0|
	BL       |loc_08013C66|
|loc_080034B0|
	ADD      r4, #1
	CMP      r4, #9
	BLT      |loc_08003494|
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0]
	SUB      sp, #0x34
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #4]
	STR      r0, [sp, #0x30]
	LDR      r0, [r4]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #4]
	STR      r0, [sp, #0x2c]
	LDR      r0, [r4]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #4]
	BL       |loc_080001C6|
	ADD      r1, r0, #0
	ADD      r0, sp, #0xc
	BL       |Object_WriteBounds1|
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x14]
	LDR      r2, [sp, #0x18]
	ADD      r1, r0, r1
	STR      r1, [sp, #4]
	ASR      r1, r1, #1
	LDR      r0, [sp, #0x10]
	STR      r1, [sp, #4]
	ADD      r0, r0, r2
	STR      r0, [sp, #8]
	ASR      r0, r0, #1
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x20]
	STR      r1, [sp, #0x1c]
	LDR      r1, [sp, #0x2c]
	MOV      r0, #2
	BL       |inc_0x046118_0x049114| + 0xd40
	ADD      r5, r0, #0
	MOV      r0, #2
	LDR      r1, [sp, #0x30]
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [sp, #8]
	LDR      r2, [sp, #0x1c]
	LDR      r1, [sp, #8]
	SUB      r0, r2, r5
	LDR      r2, [sp, #0x20]
	STR      r5, [sp, #4]
	STR      r0, [sp, #4]
	SUB      r1, r2, r1
	STR      r0, [sp, #0x24]
	LDR      r0, [pc, #0x1e4]
	STR      r1, [sp, #8]
	STR      r1, [sp, #0x28]
	LDR      r1, [r0, #0x24]
	ADD      r0, sp, #0x14
	ADD      r2, sp, #0x24
	ADD      r3, sp, #0x2c
	BL       |loc_08009816|
	LDR      r2, [sp, #0x14]
	LDR      r0, [r4]
	ADD      r1, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	STR      r1, [r4]
	STR      r2, [r0, #4]
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0]
	SUB      sp, #0x34
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #4]
	STR      r0, [sp, #0x30]
	LDR      r0, [r4]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #4]
	STR      r0, [sp, #0x2c]
	LDR      r0, [r4]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #4]
	BL       |loc_080001C6|
	ADD      r1, r0, #0
	ADD      r0, sp, #0xc
	BL       |Object_WriteBounds1|
	LDR      r0, [sp, #0xc]
	LDR      r1, [sp, #0x14]
	LDR      r2, [sp, #0x18]
	ADD      r1, r0, r1
	STR      r1, [sp, #4]
	ASR      r1, r1, #1
	LDR      r0, [sp, #0x10]
	STR      r1, [sp, #4]
	ADD      r0, r0, r2
	STR      r0, [sp, #8]
	ASR      r0, r0, #1
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x20]
	STR      r1, [sp, #0x1c]
	LDR      r1, [sp, #0x2c]
	MOV      r0, #2
	BL       |inc_0x046118_0x049114| + 0xd40
	ADD      r5, r0, #0
	MOV      r0, #2
	LDR      r1, [sp, #0x30]
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [sp, #8]
	LDR      r2, [sp, #0x1c]
	LDR      r1, [sp, #8]
	SUB      r0, r2, r5
	LDR      r2, [sp, #0x20]
	STR      r5, [sp, #4]
	STR      r0, [sp, #4]
	SUB      r1, r2, r1
	STR      r0, [sp, #0x24]
	LDR      r0, [pc, #0x144]
	STR      r1, [sp, #8]
	STR      r1, [sp, #0x28]
	LDR      r1, [r0, #0x24]
	ADD      r0, sp, #0x14
	ADD      r2, sp, #0x24
	ADD      r3, sp, #0x2c
	BL       |loc_08009816|
	LDR      r2, [sp, #0x18]
	LDR      r0, [r4]
	ADD      r1, r0, #1
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	STR      r1, [r4]
	STR      r2, [r0, #4]
	ADD      sp, #0x34
	POP      {r4, r5, pc}
	PUSH     {r4, lr}
	LDR      r4, [r0]
	SUB      r4, #1
	LSL      r1, r4, #2
	STR      r4, [r0]
	ADD      r1, r1, r0
	LDR      r3, [r1, #4]
	SUB      r4, #1
	LSL      r1, r4, #2
	STR      r4, [r0]
	ADD      r1, r1, r0
	LDR      r2, [r1, #4]
	SUB      r4, #1
	LSL      r1, r4, #2
	STR      r4, [r0]
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	SUB      r4, #1
	STR      r4, [r0]
	LSL      r4, r4, #2
	ADD      r0, r4, r0
	LDR      r0, [r0, #4]
	BL       |sub_08031808|
	POP      {r4, pc}
	PUSH     {r4, lr}
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x746c
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r4, [pc, #0xe4]
	LDR      r0, [r4, #0x18]
	BL       |Object_Construct8|
	MOV      r0, #0
	BL       |sub_080315b0|
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r0, [r4, #0x18]
	BL       |loc_08011E0E|
	MOV      r1, #1
	LDR      r0, [r4, #0x24]
	BL       |loc_0800938C|
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7448
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x746c
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r5, [pc, #0xa8]
	LDR      r0, [r5, #0x18]
	BL       |Object_Construct8|
	LDR      r0, [r4]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r1, [r0, #4]
	MOV      r0, #0
	BL       |dat_08031832| + 0x652
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r0, [r5, #0x18]
	BL       |loc_08011E0E|
	MOV      r1, #1
	LDR      r0, [r5, #0x24]
	BL       |loc_0800938C|
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x7448
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	LDR      r4, [pc, #0x6c]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r6, [r0, #4]
	LDR      r0, [r4, #0x14]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MOV      r5, #0x9f
	LSL      r5, r5, #3
	MUL      r1, r3
	ADD      r0, r1, r0
	ADD      r0, r0, r5
	LDRB     r0, [r0, #0x14]
	LDR      r7, [pc, #0x54]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r7
	BL       |inc_0x153f2_0x1a3f2| + 0x1d3a
	LDR      r0, [r4, #0x14]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	MOV      r1, #5
	LSL      r1, r1, #8
	ADD      r0, r0, r1
	STRB     r6, [r0, #0xc]
	LDR      r0, [pc, #0x38]
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_080036FC|
	LDR      r1, [r4, #0x14]
	LDRB     r2, [r1]
	MUL      r2, r3
	ADD      r1, r2, r1
	ADD      r1, r1, r5
	BL       |loc_08010692|
|loc_080036FC|
	LDR      r0, [r4, #0x14]
	MOV      r3, #0x68
	LDRB     r1, [r0]
	MUL      r1, r3
	ADD      r0, r1, r0
	ADD      r0, r0, r5
	LDRB     r0, [r0, #0x14]
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #3
	ADD      r0, r0, r7
	BL       |inc_0x153f2_0x1a3f2| + 0x1d2a
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08003718|
|unk_08003718|
	INCBIN	baserom.gba_0x3718_0x371a.extracted
|sub_0800371A|
	DCW      0x0805
	DCW      0x82ec
	DCW      0x086b
	DCW      0x1c34
	DCW      0x0300
