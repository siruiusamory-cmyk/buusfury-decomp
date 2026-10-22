	IMPORT |GBARam_Free|
	IMPORT |GBARam_Malloc|
	CODE16
	EXPORT |sub_080331C0|
	EXPORT |loc_080331CC|
	EXPORT |sub_08033208|
	EXPORT |loc_080332AC|
	EXPORT |sub_080332E0|
	EXPORT |loc_080332FC|
	EXPORT |sub_08033334|
	EXPORT |loc_08033338|
	EXPORT |sub_0803333C|
	EXPORT |loc_08033352|
	EXPORT |sub_08033380|
	EXPORT |sub_08033384|
	EXPORT |sub_080333A4|
	EXPORT |sub_080333A6|
	EXPORT |loc_08033442|
	EXPORT |loc_080334EC|
	EXPORT |sub_080335B4|
	EXPORT |sub_080335B6|
	EXPORT |loc_080335D4|
	EXPORT |loc_08033628|
	EXPORT |loc_0803362A|
	EXPORT |loc_0803365A|
	EXPORT |loc_08033664|
	EXPORT |loc_08033694|
	EXPORT |sub_0803377A|
	EXPORT |Blend_WriteAlpha4|
	EXPORT |sub_08033808|
	EXPORT |loc_08033826|
	EXPORT |loc_08033836|
	EXPORT |sub_08033862|
	EXPORT |loc_080338AC|
	EXPORT |loc_080338D8|
	EXPORT |sub_080338FC|
	EXPORT |sub_08033948|
	EXPORT |loc_08033966|
	EXPORT |sub_0803396E|
	EXPORT |sub_08033972|
	EXPORT |loc_08033996|
	EXPORT |loc_08033A14|
	EXPORT |sub_08033A40|
	EXPORT |sub_08033AF6|
	EXPORT |loc_08033B30|
	EXPORT |sub_08033B32|
	EXPORT |sub_08033B88|
	EXPORT |loc_08033BAA|
	EXPORT |sub_08033BB2|
	EXPORT |sub_08033BB6|
	EXPORT |sub_08033BC0|
	EXPORT |sub_08033BC4|
	EXPORT |loc_08033C3C|
	EXPORT |loc_08033C44|
	EXPORT |sub_08033C66|
	EXPORT |loc_08033C76|
	EXPORT |sub_08033CA4|
	EXPORT |sub_08033CB8|
	EXPORT |sub_08033CBA|
	EXPORT |loc_08033CEC|
	EXPORT |sub_08033CF0|
	EXPORT |sub_08033D2C|
	EXPORT |sub_08033D4C|
	EXPORT |sub_08033D66|
	EXPORT |sub_08033D80|
	EXPORT |sub_08033D82|
	EXPORT |sub_08033DC0|
	EXPORT |sub_08033E74|
	EXPORT |loc_08033E96|
	EXPORT |loc_08033EAA|
	EXPORT |loc_08033ED2|
	EXPORT |sub_08033EE8|
	EXPORT |sub_08033EFA|
	EXPORT |loc_08033F20|
	EXPORT |sub_08033F22|
	EXPORT |sub_08033F26|
	EXPORT |sub_08033F48|
	EXPORT |loc_080340A8|
	EXPORT |sub_080340C8|
	EXPORT |sub_080340E8|
	EXPORT |sub_080340F4|
	EXPORT |sub_08034120|
|sub_080331C0|
	BEQ      |loc_080331CC|
	LDR      r1, [pc, #0x24]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
|loc_080331CC|
	POP      {r4, pc}
	LSL      r0, r0, #0
	STMIA    r6!, {r4, r7}
	LSR      r4, r0, #0x20
	STR      r2, [sp, #0x170]
	LSR      r5, r6, #1
	BGE      |loc_080332AC|
	LSR      r1, r6, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	ADR      r6, |loc_080334EC|
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	SUB      sp, #0x40
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |sub_08033208|
	ADD      sp, #0x40
	POP      {r4, pc}
|sub_08033208|
|unk_08033208|
		LDR r0, [pc, #0xf4]
		LDR r1, [r0]
		ADD r0, sp, #8
		BL       |sub_0800FDFA|
		LDR r0, [sp, #8]
		LDR r1, [sp, #0x10]
		LDR r2, [sp, #0x14]
		ADD r1, r0, r1
		LDR r0, [sp, #0xc]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp]
		STR r1, [sp, #0x18]
		STR r0, [sp, #4]
		STR r0, [sp, #0x1c]
		ADD r0, sp, #0x20
		ADD r1, r4, #0
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0x20]
		LDR r1, [sp, #0x28]
		LDR r2, [sp, #0x2c]
		ADD r1, r0, r1
		LDR r0, [sp, #0x24]
		STR r1, [sp]
		ADD r0, r0, r2
		STR r0, [sp, #4]
		ASR r0, r0, #1
		STR r0, [sp, #4]
		STR r0, [sp, #0x34]
		ASR r1, r1, #1
		LDR r0, [sp, #0x18]
		STR r1, [sp]
		SUB r0, r0, r1
		STR r1, [sp, #0x30]
		LDR r1, [sp, #0x1c]
		LDR r2, [sp, #0x34]
		STR r0, [sp]
		SUB r1, r1, r2
		ADD r2, r0, #0
		CMP r0, #0
		STR r1, [sp, #4]
		STR r1, [sp, #0x3c]
		STR r0, [sp, #0x38]
		BGE      |loc_0803326C|
		NEG r0, r2
|loc_0803326C|
		ADD r1, r0, #0
		LDR r0, [sp, #0x3c]
		CMP r0, #0
		BGE      |loc_08033276|
		NEG r0, r0
|loc_08033276|
		STR r1, [sp, #0x30]
		STR r0, [sp, #0x34]
		LDRB r3, [r4, #0x10]
		ADD r0, r1, #0
		LDR r1, [sp, #0x34]
		CMP r3, #0
		BEQ      |inc_0x331c0_0x341c0| + 0x10a
		MOV r2, #0xf
		MVN r2, r2
		CMP r3, #1
		BEQ      |inc_0x331c0_0x341c0| + 0xf8
		CMP r3, #2
		BEQ      |loc_080332A6|
		CMP r3, #3
		BNE      |inc_0x331c0_0x341c0| + 0x11c
		CMP r1, #0x10
		BGE      |loc_080332A2|
		LDR r0, [sp, #0x38]
		CMP r0, #0x10
		BLE      |loc_080332A2|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x44
|loc_080332A2|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x44
|loc_080332A6|
		CMP r1, #0x10
		BGE      |loc_080332B4|
		LDR r0, [sp, #0x38]
|loc_080332AC|
|unk_080332AC|
		CMP r0, r2
		BGE      |loc_080332B4|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x44
|loc_080332B4|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x44
		CMP r0, #0x10
		BGE      |loc_080332C6|
		LDR r0, [sp, #0x3c]
		CMP r0, r2
		BGE      |loc_080332C6|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x44
|loc_080332C6|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x44
		CMP r0, #0x10
		BGE      |loc_080332D8|
		LDR r0, [sp, #0x3c]
		CMP r0, #0x10
		BLE      |loc_080332D8|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x44
|loc_080332D8|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x44
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x44
|sub_080332E0|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080332FC|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_080332FC|
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	POP      {r3, r4, r5, r7, pc}
	LSR      r4, r0, #0x20
	PUSH     {lr}
	ADD      r2, r1, #0
	LDR      r1, [r0, #4]
	MOV      r0, #0x85
	LSL      r0, r0, #2
	ADD      r2, r2, r0
	MOV      r0, #0
	SUB      sp, #0x6c
	STR      r0, [sp]
	STR      r0, [sp, #0x44]
	MOV      r0, sp
	BL       |inc_0x0158_0x143f2| + 0x3ee0
	LDR      r0, [sp]
	CMP      r0, #1
	BNE      |loc_08033338|
	LDR      r0, [sp, #4]
	CMP      r0, #0
	BEQ      |sub_08033334|
	MOV      r0, #1
	ADD      sp, #0x6c
	POP      {pc}
|sub_08033334|
|unk_08033334|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x170
|loc_08033338|
|unk_08033338|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x170
|sub_0803333C|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	ADD      r4, #0xc
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08033352|
	LDR      r1, [pc, #0x54]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08033352|
	POP      {r4, pc}
	ADD      r2, r1, #0
	ADD      r1, r0, #0
	MOV      r0, #0x85
	LSL      r0, r0, #2
	ADD      r1, #0xc
	ADD      r2, r2, r0
	PUSH     {lr}
	SUB      sp, #0x6c
	MOV      r0, #0
	STR      r0, [sp]
	STR      r0, [sp, #0x44]
	MOV      r0, sp
	BL       |inc_0x0158_0x143f2| + 0x3ee0
	LDR      r0, [sp]
	CMP      r0, #1
	BNE      |sub_08033380|
	LDR      r0, [sp, #4]
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	ADD      sp, #0x6c
	POP      {pc}
|sub_08033380|
|unk_08033380|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x1bc
|sub_08033384|
	ADD      r2, r1, #0
	ADD      r1, r0, #0
	MOV      r0, #0x85
	LSL      r0, r0, #2
	ADD      r1, #0xc
	ADD      r2, r2, r0
	PUSH     {lr}
	SUB      sp, #0x6c
	MOV      r0, #0
	STR      r0, [sp]
	STR      r0, [sp, #0x44]
	MOV      r0, sp
	BL       |inc_0x0158_0x143f2| + 0x3ee0
	ADD      sp, #0x6c
	POP      {pc}
|sub_080333A4|
|unk_080333A4|
	INCBIN	baserom.gba_0x333a4_0x333a6.extracted
|sub_080333A6|
	LSR      r4, r0, #0x20
	LSL      r3, r2, #1
	ADD      r2, r3, r2
	LDR      r3, [pc, #0x204]
	LSL      r2, r2, #2
	ADD      r3, r2, r3
	LSL      r0, r0, #2
	LDR      r3, [r3, r0]
	STR      r3, [r1, #8]
	LDR      r3, [pc, #0x1f8]
	ADD      r3, #0x18
	ADD      r2, r2, r3
	LDR      r0, [r2, r0]
	STR      r0, [r1, #0x10]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	SUB      sp, #0x3c
	ADD      r5, r1, #0
	ADD      r6, r2, #0
	ADD      r0, sp, #0x28
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	MOV      r0, #0xff
	ADD      r0, #0xa1
	LDR      r0, [r0, r5]
	ADD      r3, sp, #0
	ASR      r0, r0, #8
	STRH     r0, [r3, #0x24]
	MOV      r0, #0xff
	ADD      r0, #0xa5
	LDR      r0, [r0, r5]
	ASR      r0, r0, #8
	STRH     r0, [r3, #0x26]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x74]
	ADD      r3, r2, r1
	ADD      r2, r6, #0
	LDR      r1, [r4, #0x10]
	BL       |inc_0x046118_0x049114| + 0x98e
	LDR      r6, [pc, #0x1b8]
	ADD      r1, r5, #0
	SUB      r6, #0x24
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_08033442|
	LDR      r0, [sp, #0x28]
	LDR      r2, [sp, #0x30]
	LDR      r3, [sp, #0x34]
	ADD      r2, r0, r2
	STR      r2, [sp, #0x14]
	ASR      r2, r2, #1
	LDR      r0, [sp, #0x2c]
	STR      r2, [sp, #0x14]
	ADD      r0, r0, r3
	STR      r0, [sp, #0x18]
	ASR      r0, r0, #1
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x38
	STR      r0, [sp, #0x18]
	STR      r0, [sp, #0x20]
	MOV      r0, #0
	ADD      r1, sp, #0x1c
	BL       |inc_0x153f2_0x1a3f2| + 0x413a
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
|loc_08033442|
	LDR      r1, [pc, #0x170]
	MOV      r2, #0x20
	ADD      r5, sp, #4
	SUB      r1, #0x20
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0x24]
	STRH     r0, [r3, #0x10]
	LDRH     r0, [r3, #0x26]
	STRH     r0, [r3, #0x12]
	LDR      r7, [r4, #0xc]
	MOV      r0, #2
	BL       |inc_0x03d784_0x041118| + 0x2348
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0x14c]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LSL      r2, r7, #2
	LDR      r1, [r1, r2]
	MOV      r7, #0
	STR      r1, [sp, #0xc]
	LDR      r1, [pc, #0x13c]
	MVN      r7, r7
	ADD      r1, #0x18
	ADD      r0, r0, r1
	LDR      r0, [r0, r2]
	LDR      r1, [pc, #0x138]
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0xc]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	ADD      r3, r7, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [pc, #0x114]
	MOV      r2, #0x20
	SUB      r1, #0x20
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0x24]
	ADD      r0, #0x18
	STRH     r0, [r3, #0x10]
	LDRH     r0, [r3, #0x26]
	STRH     r0, [r3, #0x12]
	LDR      r2, [r4, #0xc]
	MOV      r0, #2
	STR      r2, [sp]
	BL       |inc_0x03d784_0x041118| + 0x2348
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0xec]
	LDR      r2, [sp]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LSL      r2, r2, #2
	LDR      r1, [r1, r2]
	STR      r1, [sp, #0xc]
	LDR      r1, [pc, #0xe0]
	ADD      r1, #0x18
	ADD      r0, r0, r1
	LDR      r0, [r0, r2]
	LDR      r1, [pc, #0xdc]
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0xc]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	ADD      r3, r7, #0
	ADD      r1, r5, #0
|loc_080334EC|
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [pc, #0xb8]
	MOV      r2, #0x20
	SUB      r1, #0x20
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0x24]
	ADD      r0, #0x18
	STRH     r0, [r3, #0x10]
	LDRH     r0, [r3, #0x26]
	ADD      r0, #0x18
	STR      r0, [sp, #0x38]
	STRH     r0, [r3, #0x12]
	LDR      r2, [r4, #0xc]
	MOV      r0, #2
	STR      r2, [sp]
	BL       |inc_0x03d784_0x041118| + 0x2348
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0x8c]
	LDR      r2, [sp]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LSL      r2, r2, #2
	LDR      r1, [r1, r2]
	STR      r1, [sp, #0xc]
	LDR      r1, [pc, #0x80]
	ADD      r1, #0x18
	ADD      r0, r0, r1
	LDR      r0, [r0, r2]
	LDR      r1, [pc, #0x7c]
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0xc]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	ADD      r3, r7, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [pc, #0x58]
	MOV      r2, #0x20
	SUB      r1, #0x20
	ADD      r0, r5, #0
	BL       |inc_0x049120_0x055620| + 0x18
	ADD      r3, sp, #0
	LDRH     r0, [r3, #0x24]
	STRH     r0, [r3, #0x10]
	LDR      r0, [sp, #0x38]
	STRH     r0, [r3, #0x12]
	LDR      r4, [r4, #0xc]
	MOV      r0, #2
	BL       |inc_0x03d784_0x041118| + 0x2348
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0x34]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LSL      r2, r4, #2
	LDR      r1, [r1, r2]
	STR      r1, [sp, #0xc]
	LDR      r1, [pc, #0x28]
	ADD      r1, #0x18
	ADD      r0, r0, r1
	LDR      r0, [r0, r2]
	LDR      r1, [pc, #0x24]
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0xc]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	ADD      r3, r7, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r1, r0, #0
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
|sub_080335B4|
|unk_080335B4|
	INCBIN	baserom.gba_0x335b4_0x335b6.extracted
|sub_080335B6|
	LSR      r5, r6, #1
	ASR      r4, r6, #9
	LSR      r1, r6, #1
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_080335D4|
	MOV      r0, #0x48
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_080335D4|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_080335D4|
	LDR      r0, [pc, #0x264]
	MOV      r2, #0x40
	STR      r0, [r4]
	ADD      r0, r4, #0
	ADD      r0, #0x14
	MOV      r1, #0xf0
	ADD      r5, r0, #0
	BL       |inc_0x03d784_0x041118| + 0x1dbc
	LDR      r0, [pc, #0x258]
	MOV      r2, #1
	STR      r0, [r4, #0x10]
	MOV      r0, #0x90
	STR      r0, [r4, #4]
	MOV      r0, #0
	STR      r0, [r4, #8]
	STR      r6, [r4, #0xc]
	MOV      r0, #2
	STRB     r0, [r4, #0x17]
	LDR      r1, [pc, #0x248]
	STRB     r2, [r5, #2]
	STR      r1, [r5, #0x20]
	STRB     r2, [r4, #0x14]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x230]
	ADD      r5, r1, #0
	STR      r0, [r4]
	ADD      r0, r4, #0
	MOV      r1, #0
	ADD      r0, #0x14
	BL       |inc_0x03d784_0x041118| + 0x1e08
	LDR      r0, [pc, #0x22c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08033628|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08033628|
	POP      {r3, r4, r5, pc}
|loc_0803362A|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	LDR      r2, [r0, #0x44]
	LDR      r0, [r0, #0x38]
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [pc, #0x210]
	LDR      r0, [r0, #0xc]
	STR      r0, [r4, #0x20]
	MOV      r0, #0x78
	STR      r0, [r4, #0x18]
	MOV      r0, #0x10
	STR      r0, [r4, #0x1c]
	MOV      r0, #8
	STRB     r0, [r4, #0x15]
	ADD      r4, #0x14
	CMP      r5, #0
	BEQ      |loc_0803365A|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
|loc_0803365A|
	LDR      r1, [pc, #0x1f4]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	POP      {r3, r4, r5, pc}
|loc_08033664|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	LDR      r2, [r0, #0x44]
	LDR      r0, [r0, #0x38]
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0xd28
	LDR      r0, [pc, #0x1d4]
	LDR      r0, [r0, #8]
	STR      r0, [r4, #0x20]
	MOV      r0, #0x78
	STR      r0, [r4, #0x18]
	MOV      r0, #0x18
	STR      r0, [r4, #0x1c]
	MOV      r0, #0x10
	STRB     r0, [r4, #0x15]
	ADD      r4, #0x14
	CMP      r5, #0
	BEQ      |loc_08033694|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x356
|loc_08033694|
	LDR      r1, [pc, #0x1bc]
	ADD      r0, r4, #0
	BL       |inc_0x049120_0x055620| + 0x30
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	LDR      r0, [pc, #0x1ac]
	SUB      sp, #0x10
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r1, #0
	MOV      r0, #5
	LSL      r0, r0, #0x18
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #3
	LSL      r2, r2, #0xf
	MOV      r1, #0
	LSL      r0, r2, #0xa
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x40
	MOV      r1, #0
	MOV      r0, #3
	LSL      r0, r0, #0x19
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #1
	LSL      r2, r2, #0xc
	MOV      r1, #0
	LDR      r0, [pc, #0x17c]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r0, #6
	STR      r0, [sp, #4]
	MOV      r0, #0xe
	MOV      r5, #0
	MOV      r6, #0x1e
	STR      r0, [sp, #0xc]
	MOV      r0, sp
	STR      r6, [sp, #8]
	MOV      r2, #1
	STR      r5, [sp]
	LDR      r1, [pc, #0x168]
	BL       |inc_0x03d784_0x041118| + 0x28c
	MOV      r0, #0xa
	STR      r0, [sp, #4]
	MOV      r0, #0x12
	STR      r0, [sp, #0xc]
	MOV      r0, sp
	MOV      r2, #0xf1
	STR      r5, [sp]
	STR      r6, [sp, #8]
	LDR      r1, [pc, #0x14c]
	BL       |inc_0x03d784_0x041118| + 0x28c
	LDR      r0, [pc, #0x150]
	MOV      r1, #1
	LSL      r1, r1, #0x1a
	STRH     r0, [r1, #8]
	ADD      r0, #0xff
	ADD      r0, #1
	STRH     r0, [r1, #0xa]
	MOV      r0, #0x52
	STRB     r5, [r0, r1]
	MOV      r0, #0x53
	STRB     r5, [r0, r1]
	STRH     r5, [r1, #0x10]
	STRH     r5, [r1, #0x12]
	LDR      r0, [pc, #0x138]
	LDR      r1, [pc, #0x140]
	STRH     r5, [r0]
	STRH     r5, [r0, #2]
	LDR      r0, [pc, #0x134]
	LDR      r5, [pc, #0x13c]
	STRH     r0, [r1, #0x10]
	MOV      r0, #3
	LSL      r0, r0, #8
	SUB      r1, #0x40
	STRH     r0, [r1]
	LDR      r0, [r4, #0x10]
	LSL      r0, r0, #2
	LDR      r1, [r5, r0]
	ADD      r0, r4, #0
	BL       |loc_08033664|
	LDR      r0, [r4, #0x10]
	ADD      r0, #1
	LSL      r0, r0, #2
	LDR      r1, [r5, r0]
	ADD      r0, r4, #0
	BL       |loc_0803362A|
	MOV      r2, #1
	LSL      r2, r2, #9
	MOV      r0, #5
	LSL      r0, r0, #0x18
	LDR      r1, [pc, #0x110]
	BL       |inc_0x049120_0x055620| + 0x24
	MOV      r2, #1
	LSL      r2, r2, #9
	LDR      r1, [pc, #0x108]
	LDR      r0, [pc, #0xe4]
	BL       |inc_0x049120_0x055620| + 0x24
	ADD      sp, #0x10
	POP      {r4, r5, r6, pc}
|sub_0803377A|
|unk_0803377A|
		BX       lr
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r0, [r0, #0xc]
		MOV r6, #0
		CMP r0, #0
		LDR r5, [pc, #0xc4]
		BNE      |loc_080337B2|
		LDR r0, [r4, #8]
		CMP r0, #0
		BNE      |loc_080337B2|
		LDR r0, [r5]
		LDRH r0, [r0, #4]
		LSL r1, r0, #0x1f
		BNE      |loc_0803379E|
		LSL r0, r0, #0x1e
		LSR r0, r0, #0x1f
		BEQ      |loc_080337B2|
|loc_0803379E|
		MOV r0, #1
		STR r0, [r4, #8]
		LDR r0, [r5, #4]
		LDR r7, [pc, #0xd8]
		ADD r3, r6, #0
		MOV r2, #0x40
		ADD r0, r0, r7
		LDR r1, [pc, #0xcc]
		BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_080337B2|
		LDR r0, [r4, #4]
		ADD r0, #1
		STR r0, [r4, #4]
		CMP r0, #0x80
		BGE      |loc_080337D2|
		LDR r0, [r4, #8]
		CMP r0, #0
		BNE      |loc_080337CC|
		LDR r0, [r5]
		LDRH r0, [r0, #2]
		LSL r0, r0, #0x18
		LSR r0, r0, #0x1f
		BEQ      |loc_08033836|
|loc_080337CC|
		MOV r0, #0x7f
		STR r0, [r4, #4]
		B        |loc_08033836|
|loc_080337D2|
		CMP r0, #0x80
		BNE      |Blend_WriteAlpha4|
		LDR r0, [r4, #0x10]
		LDR r1, [pc, #0xa8]
		ADD r0, #2
		STR r0, [r4, #0x10]
		CMP r0, r1
		BLT      |loc_08033836|
		MOV r0, #1
		STR r0, [r4, #8]
		LDR r0, [pc, #0x58]
		STR r0, [r4, #0x10]
		B        |loc_08033836|
|Blend_WriteAlpha4|
	LDR      r1, [pc, #0x98]
	CMP      r0, #0x90
	BGT      |loc_08033826|
	MOV      r2, #0x90
	SUB      r0, r2, r0
	STRB     r0, [r1, #2]
	LDR      r0, [r4, #4]
	CMP      r0, #0x90
	BNE      |loc_08033836|
	LDR      r0, [r4, #8]
	CMP      r0, #0
	BEQ      |sub_08033808|
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08033808|
|unk_08033808|
		LDR r0, [r4, #0x10]
		LDR r5, [pc, #0x68]
		LSL r0, r0, #2
		LDR r1, [r5, r0]
		ADD r0, r4, #0
		BL       |loc_08033664|
		LDR r0, [r4, #0x10]
		ADD r0, #1
		LSL r0, r0, #2
		LDR r1, [r5, r0]
		ADD r0, r4, #0
		BL       |loc_0803362A|
		B        |loc_08033836|
|loc_08033826|
|unk_08033826|
		CMP r0, #0xa0
		BGT      |loc_08033836|
		ADD r0, #0x70
		STRB r0, [r1, #2]
		LDR r0, [r4, #4]
		CMP r0, #0xa0
		BNE      |loc_08033836|
		STR r6, [r4, #4]
|loc_08033836|
|unk_08033836|
; cited by 0x080335D4 (a pc-relative load targets 0x0803383C)
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x646
	INCBIN  baserom.gba_0x3383a_0x33862.extracted
|sub_08033862|
	LSL      r0, r0, #0x18
	SUB      r3, r0, #2
	LSL      r0, r0, #0
	LSL      r4, r2, #0
	LSL      r0, r0, #0x10
	MOV      r0, #0x43
	LSL      r0, r0, #0
	LSL      r0, r0, #1
	LSL      r0, r0, #0x10
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	STR      r4, [r5, #0x50]
	LSR      r5, r0, #0x20
	STR      r4, [sp, #0x1c0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LSL      r1, r5, #0x16
	LSL      r0, r0, #0
	LSL      r0, r2, #1
	LSL      r0, r0, #0x10
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	LDR      r1, [pc, #0x68]
	LDR      r4, [r1]
	LDR      r5, [r0, #4]
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080338AC|
	MOV      r1, #1
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x58]
	STR      r1, [r0]
	STR      r5, [r0, #8]
	STR      r6, [r0, #0xc]
|loc_080338AC|
	ADD      r2, r0, #0
	MOV      r0, #0x61
	LSL      r0, r0, #4
	ADD      r0, r4, r0
	LDR      r1, [r0]
	ADD      r3, r1, #1
	STR      r3, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	STR      r2, [r0, #4]
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080338D8|
	LDR      r1, [pc, #0x30]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_080338D8|
	POP      {r4, pc}
	MOV      r2, #0x85
	LSL      r2, r2, #2
	PUSH     {r3, lr}
	LDR      r0, [r0, #0xc]
	ADD      r1, r1, r2
	BL       |inc_0x0158_0x143f2| + 0x12430
	MOV      r0, #1
	POP      {r3, pc}
	MOV      r2, #0x85
	LSL      r2, r2, #2
	PUSH     {r3, lr}
	LDR      r0, [r0, #0xc]
	ADD      r1, r1, r2
	BL       |inc_0x0158_0x143f2| + 0x12430
	POP      {r3, pc}
|sub_080338FC|
|unk_080338FC|
; cited by 0x08033890 (a pc-relative load targets 0x080338FC)
	INCBIN  baserom.gba_0x338fc_0x33908.extracted
		PUSH {r3, r4, r5, lr}
		ADD r4, r1, #0
		MOV r0, #0xff
		ADD r0, #0x15
		LDR r5, [r1, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |loc_0803392C|
		MOV r0, #0xff
		ADD r0, #0x13
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800EDF8|
		B        |loc_08033966|
|loc_0803392C|
		MOV r0, #0xcb
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |sub_08033948|
		MOV r0, #0xca
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800EDF8|
		B        |loc_08033966|
|sub_08033948|
	MOV      r0, #0xff
	ADD      r0, #0x22
	LDR      r5, [r4, #0x58]
	BL       |inc_0x0158_0x143f2|
	CMP      r5, r0
	BNE      |loc_08033966|
	MOV      r0, #0xff
	ADD      r0, #0x21
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
|loc_08033966|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xf7fc
	POP      {r3, r4, r5, pc}
|sub_0803396E|
|unk_0803396E|
	INCBIN	baserom.gba_0x3396e_0x33972.extracted
|sub_08033972|
	LSL      r0, r0, #0
	ADD      r2, #4
	LSL      r0, r0, #0xc
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	LDRH     r0, [r1, #0x12]
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x20
	BCC      |loc_08033996|
	MOV      r0, #0x10
	STRH     r0, [r1, #0x12]
|loc_08033996|
	LDRH     r0, [r1, #0x12]
	LSR      r0, r0, #3
	STRB     r0, [r1, #0x11]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	SUB      sp, #0x30
	MOV      r6, #0
	STR      r6, [r0, #8]
	LDR      r0, [pc, #0x18c]
	ADD      r5, r1, #0
	LDR      r4, [r0]
	MOV      r1, #9
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	STRB     r6, [r4, #0x11]
	LDRB     r0, [r5, #0x10]
	MOV      r1, #1
	EOR      r0, r1
	STRB     r0, [r4, #0x10]
	ADD      r0, r4, #0
	LDR      r1, [pc, #0x174]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x174]
	ADD      r6, sp, #0x10
	LDMIA    r0!, {r1, r2, r3}
	STMIA    r6!, {r1, r2, r3}
	LDMIA    r0!, {r1, r2, r3}
	STMIA    r6!, {r1, r2, r3}
	LDMIA    r0!, {r2, r3}
	STMIA    r6!, {r2, r3}
	ADD      r1, r4, #0
	LDRB     r2, [r5, #0x10]
	ADD      r1, #0xff
	ADD      r1, #0xa1
	SUB      r6, #0x20
	LSL      r2, r2, #3
	ADD      r2, r2, r6
	LDMIA    r1!, {r3}
	LDMIA    r2!, {r4}
	LDR      r1, [r1]
	ADD      r0, r5, #0
	ADD      r0, #0xff
	LDR      r2, [r2]
	SUB      r3, r3, r4
	ADD      r0, #0xa1
	SUB      r1, r1, r2
	STR      r1, [sp, #4]
	LDR      r2, [sp, #4]
	STR      r3, [sp]
	STR      r3, [sp, #8]
	STR      r2, [sp, #0xc]
	STMIA    r0!, {r3}
	LDR      r1, [sp, #0xc]
	STR      r1, [r0]
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08033A14|
	LDR      r1, [pc, #0x12c]
	STR      r1, [r0]
|loc_08033A14|
	ADD      r4, r0, #0
	MOV      r1, #0x12
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	ADD      sp, #0x30
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x104]
	ADD      r6, r1, #0
	LDR      r4, [r7]
	ADD      r5, r0, #0
	CMP      r4, #0
	SUB      sp, #0x1c
	BNE      |sub_08033A40|
	MOV      r0, #1
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|sub_08033A40|
|unk_08033A40|
		LDR r1, [r4]
		MOV r2, #0x80
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		ADD r0, #0x16
		MOV r3, #0
		LDRSH r0, [r0, r3]
		CMP r0, #0
		BGT      |loc_08033A5C|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x87c
|loc_08033A5C|
		LDR r1, [pc, #0xd8]
		LDR r0, [r4, #0x14]
		CMP r0, r1
		BEQ      |loc_08033A68|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x87c
|loc_08033A68|
		LDR r0, [pc, #0xd0]
		LDR r2, [pc, #0xd8]
		SUB r0, #4
		LDR r0, [r0]
		LDRH r1, [r0, #4]
		MOV r0, #0xf3
		AND r1, r0
		MOV r0, #0
		CMP r1, #0
		LDR r1, [r2, #4]
		BEQ      |loc_08033A9C|
		STR r1, [r5, #4]
		LDR r1, [r5, #8]
		ADD r1, #1
		STR r1, [r5, #8]
		CMP r1, #8
		BLE      |loc_08033AA6|
		LDR r0, [r7]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x87c
|loc_08033A9C|
		LDR r3, [r5, #4]
		SUB r1, r1, r3
		CMP r1, #0xa
		BLE      |loc_08033AA6|
		STR r0, [r5, #8]
|loc_08033AA6|
		LDR r1, [r2, #4]
		LSL r1, r1, #0x1c
		BNE      |loc_08033AD6|
		MOV r2, #0xff
		ADD r2, #0xb3
		LDRH r2, [r2, r6]
		STR r0, [sp, #0x10]
		ADD r0, r4, #0
		LSL r2, r2, #0xa
		STR r2, [sp, #0x18]
		LDR r2, [r4]
		MOV r1, sp
		LDR r3, [r2, #0x5c]
		ADD r5, sp, #0x18
		ADD r2, r3, r2
		BL       |loc_08046AA4|
		LDR r1, [r6]
		ADD r0, r6, #0
		LDR r2, [r1, #0x60]
		ADD r2, r2, r1
		ADD r1, r5, #0
		BL       |loc_08046AA4|
|loc_08033AD6|
		LDR r1, [r4]
		MOV r2, #0x80
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		ADD r0, #0x16
		MOV r3, #0
		LDRSH r0, [r0, r3]
		CMP r0, #0
		BGT      |loc_08033AF2|
		MOV r0, #1
		B        |inc_0x331c0_0x341c0| + 0x87c
|loc_08033AF2|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0x87c
|sub_08033AF6|
	ADD      r0, r1, #0
	MOV      r2, #5
	LSL      r2, r2, #7
	ADD      r2, r0, r2
	MOV      r1, #0
	PUSH     {r3, lr}
	STR      r1, [r2, #0x14]
	LDRB     r1, [r0, #0x10]
	MOV      r2, #1
	EOR      r1, r2
	MOV      r2, #0x29
	LSL      r2, r2, #4
	ADD      r2, r0, r2
	STRB     r1, [r2]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #9
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r3, lr}
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08033B30|
	LDR      r1, [pc, #0x18]
	STR      r1, [r0]
|loc_08033B30|
	POP      {r3, pc}
|sub_08033B32|
|unk_08033B32|
; cited by 0x080339A6 (a pc-relative load targets 0x08033B34)
	DCB	0x00,0x00
	DCD	|unk_03001C34|
	DCD	|unk_03001B00|
	DCD	|unk_08759334|
	DCD	0x0804C3CC
	DCD	|unk_03000F90|
	DCD	0x0804AB04
		PUSH {r3, r4, r5, lr}
		ADD r4, r1, #0
		MOV r0, #0xff
		ADD r0, #0x13
		LDR r5, [r1, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |loc_08033B70|
		MOV r0, #0xff
		ADD r0, #0x15
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800EDF8|
		B        |loc_08033BAA|
|loc_08033B70|
		MOV r0, #0xca
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |inc_0x331c0_0x341c0| + 0x9cc
		MOV r0, #0xcb
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x33b86_0x33b88.extracted
|sub_08033B88|
|unk_08033B88|
	INCBIN	baserom.gba_0x33b88_0x33b8c.extracted
	MOV      r0, #0xff
	ADD      r0, #0x21
	LDR      r5, [r4, #0x58]
	BL       |inc_0x0158_0x143f2|
	CMP      r5, r0
	BNE      |loc_08033BAA|
	MOV      r0, #0xff
	ADD      r0, #0x22
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
|loc_08033BAA|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xf7cc
	POP      {r3, r4, r5, pc}
|sub_08033BB2|
|unk_08033BB2|
	INCBIN	baserom.gba_0x33bb2_0x33bb6.extracted
|sub_08033BB6|
	LSL      r0, r0, #0
	ADD      r2, #8
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0]
	BX       lr
|sub_08033BC0|
	DCW      0x320c
	DCW      0x0300
|sub_08033BC4|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x19c]
	ADD      r4, r1, #0
	LDR      r5, [r0]
	SUB      sp, #0x6c
	CMP      r5, #0
	BEQ      |sub_08033CB8|
	MOV      r0, #0xff
	ADD      r0, #0xcd
	LDR      r0, [r0, r5]
	CMP      r0, #0
	BEQ      |sub_08033CB8|
	ADD      r1, r5, #0
	ADD      r0, sp, #0x5c
	BL       |inc_0x0158_0x143f2| + 0xfd20
	ADD      r1, r4, #0
	ADD      r0, sp, #0x4c
	BL       |inc_0x0158_0x143f2| + 0xfd20
	LDR      r0, [sp, #0x4c]
	LDR      r1, [sp, #0x54]
	LDR      r2, [sp, #0x58]
	ADD      r0, r0, r1
	LDR      r1, [sp, #0x50]
	STR      r0, [sp, #0x3c]
	ADD      r1, r1, r2
	ASR      r0, r0, #1
	ASR      r3, r1, #1
	STR      r0, [sp, #0x44]
	STR      r0, [sp, #0x3c]
	STR      r1, [sp, #0x40]
	LDR      r1, [sp, #0x64]
	LDR      r0, [sp, #0x5c]
	STR      r3, [sp, #0x40]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0x60]
	STR      r3, [sp, #0x48]
	LDR      r2, [sp, #0x68]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r0, [sp, #4]
	STR      r0, [sp, #0xc]
	ADD      r0, r1, #0
	STR      r1, [sp]
	STR      r1, [sp, #8]
	LDR      r1, [sp, #0x44]
	LDR      r2, [sp, #0x48]
	SUB      r0, r0, r1
	LDR      r1, [sp, #0xc]
	STR      r0, [sp]
	SUB      r6, r1, r2
	ADD      r1, r0, #0
	CMP      r0, #0
	STR      r6, [sp, #4]
	BGE      |loc_08033C3C|
|unk_08033C3A|
	INCBIN	baserom.gba_0x33c3a_0x33c3c.extracted
|loc_08033C3C|
	ADD      r2, r6, #0
	CMP      r6, #0
	BGE      |loc_08033C44|
|unk_08033C42|
	INCBIN	baserom.gba_0x33c42_0x33c44.extracted
|loc_08033C44|
	MOV      r7, #0
	CMP      r1, r2
	BLE      |loc_08033C76|
	STR      r3, [sp, #0x18]
	LDR      r1, [sp, #0x58]
	ADD      r1, #3
	STR      r1, [sp, #0x20]
	CMP      r0, #0
	BLE      |sub_08033C66|
	MOV      r0, #3
	STRB     r0, [r4, #0x10]
	LDR      r0, [sp, #0x44]
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0x54]
	ADD      r0, #3
	STR      r0, [sp, #0x1c]
	B        |sub_08033CA4|
|sub_08033C66|
|unk_08033C66|
		MOV r0, #2
		STRB r0, [r4, #0x10]
		LDR r0, [sp, #0x4c]
		SUB r0, #4
		STR r0, [sp, #0x14]
		LDR r0, [sp, #0x44]
		STR r0, [sp, #0x1c]
		B        |sub_08033CA4|
|loc_08033C76|
|unk_08033C76|
		ADD r1, r4, #0
		MOV r0, sp
		BL       |sub_0800FDFA|
		LDR r0, [sp]
		CMP r6, #0
		STR r0, [sp, #0x14]
		LDR r0, [sp, #8]
		STR r0, [sp, #0x1c]
		BLE      |loc_08033C98|
		STRB r7, [r4, #0x10]
		LDR r0, [sp, #0x50]
		STR r0, [sp, #0x18]
		LDR r0, [sp, #0x58]
		SUB r0, #6
		STR r0, [sp, #0x20]
		B        |sub_08033CA4|
|loc_08033C98|
		MOV r0, #1
		STRB r0, [r4, #0x10]
		LDR r0, [sp, #0x50]
		STR r0, [sp, #0x18]
		LDR r0, [sp, #4]
		STR r0, [sp, #0x20]
|sub_08033CA4|
	STR      r4, [sp, #0x30]
	LDRB     r0, [r4, #0x10]
	ADD      r3, sp, #0x20
	ADD      r2, sp, #0x10
	STRB     r0, [r3, #4]
	LDR      r0, [pc, #0xb8]
	STR      r0, [sp, #0x2c]
	MOV      r0, #1
	LSL      r0, r0, #0xa
	B        |sub_08033CBA|
|sub_08033CB8|
|unk_08033CB8|
		B        |loc_08033CEC|
|sub_08033CBA|
	STR      r0, [sp, #0x28]
	ADD      r3, sp, #0
	STRB     r7, [r3, #0x10]
	STR      r4, [sp, #0x40]
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r3, [r1, #0x24]
	ADD      r3, r3, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	CMP      r0, #0
	BEQ      |loc_08033CEC|
	LDR      r0, [pc, #0x94]
	MOV      r1, #0x5d
	LDR      r2, [pc, #0x94]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r4, [pc, #0x94]
	LDR      r0, [r0]
	MOV      r2, #0x40
	ADD      r3, r7, #0
	ADD      r0, r0, r4
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08033CEC|
	ADD      sp, #0x6c
	POP      {r4, r5, r6, r7, pc}
|sub_08033CF0|
|unk_08033CF0|
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r4, r1, #0
		LDRH r1, [r1, #0x12]
		ADD r1, #1
		LSL r3, r1, #0x10
		LSR r3, r3, #0x10
		ADD r1, r4, #0
		ADD r1, #0xff
		ADD r1, #0xc1
		STRH r3, [r4, #0x12]
		LDR r2, [r4, #0x50]
		CMP r3, #0x20
		BHS      |loc_08033D12|
		MOV r5, #0
		MOV r3, #1
		STR r3, [r1, #0xc]
		B        |inc_0x331c0_0x341c0| + 0xb78
|loc_08033D12|
		LDR r6, [r2]
		LDRB r7, [r0, #4]
		SUB r5, r6, #2
		LSL r5, r7
		ADD r5, #0x20
		CMP r5, r3
		BLE      |sub_08033D2C|
		SUB r3, #0x20
		ASR r3, r7
		ADD r5, r3, #1
		MOV r3, #0
		STR r3, [r1, #0xc]
		B        |inc_0x331c0_0x341c0| + 0xb78
|sub_08033D2C|
	SUB      r3, r3, r5
	ASR      r3, r3, #5
	ADD      r5, r6, r3
	SUB      r5, #1
	MOV      r3, #1
	STR      r3, [r1, #0xc]
	LDR      r1, [r2]
	CMP      r1, r5
	BGT      |sub_08033D4C|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r2, r2, r1
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08033D4C|
|unk_08033D4C|
		CMP r5, #1
		BNE      |loc_08033D5C|
		LDRB r1, [r4, #0x11]
		CMP r1, #0
		BNE      |loc_08033D5C|
		ADD r1, r4, #0
		BL       |sub_08033BC4|
|loc_08033D5C|
		STRB r5, [r4, #0x11]
		B        |inc_0x331c0_0x341c0| + 0xb8a
	INCBIN  baserom.gba_0x33d60_0x33d66.extracted
|sub_08033D66|
	LSL      r0, r0, #0xc
	STRH     r0, [r3, #4]
	LSR      r3, r5, #1
	STR      r3, [sp, #0x1f0]
	LSR      r5, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	ADD      r2, #0x10
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0]
	BX       lr
|sub_08033D80|
|unk_08033D80|
	INCBIN	baserom.gba_0x33d80_0x33d82.extracted
|sub_08033D82|
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	ADD      r0, r1, #0
	MOV      r1, #0x38
	STRB     r1, [r0, #8]
	STRB     r2, [r0, #0x11]
	MOV      r1, #0x13
	BL       |inc_0x0158_0x143f2| + 0xeb82
	POP      {r3, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x3c
	ADD      r4, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #0x20
	BCC      |sub_08033DC0|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
|sub_08033DC0|
|unk_08033DC0|
		LSR r0, r0, #3
		STRB r0, [r4, #0x11]
		LDRH r0, [r4, #0x12]
		CMP r0, #8
		BNE      |inc_0x331c0_0x341c0| + 0xbfc
		LDR r0, [pc, #0x120]
		LDR r5, [r0]
		CMP r5, #0
		BEQ      |inc_0x331c0_0x341c0| + 0xbfc
		MOV r0, #0x40
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r6, r0, #0
		SUB r6, #0x20
		MOV r0, #0x40
		BL       |inc_0x03d784_0x041118| + 0x2348
		ADD r7, r0, #0
		LDR r0, [pc, #0x108]
		SUB r7, #0x20
		LDR r0, [r0]
		BL       |loc_080116FC|
		CMP r0, #0x80
		BLT      |inc_0x331c0_0x341c0| + 0xbfc
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xa1
		LDMIA r0!, {r1}
		LDR r0, [r0]
		ASR r1, r1, #8
		ASR r0, r0, #8
		STR r0, [sp, #8]
		ADD r0, r1, #0
		STR r1, [sp, #4]
		LDR r1, [sp, #8]
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		LDRB r0, [r4, #0x10]
		LDR r1, [pc, #0xe0]
		ADD r1, #4
		LSL r0, r0, #3
		ADD r0, r0, r1
		LDR r1, [sp, #0xc]
		LDR r2, [r0]
		ADD r1, r1, r2
		LDR r2, [sp, #0x10]
		LDR r0, [r0, #4]
		STR r1, [sp, #4]
		ADD r0, r2, r0
		STR r0, [sp, #8]
		ADD r0, r1, #0
		LDR r1, [sp, #8]
		STR r0, [sp, #0x14]
		STR r1, [sp, #0x18]
		ADD r1, r5, #0
		ADD r0, sp, #0x1c
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0x1c]
		LDR r1, [sp, #0x24]
		LDR r2, [sp, #0x28]
		ADD r1, r0, r1
		LDR r0, [sp, #0x20]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x30]
		ADD r0, r1, r6
		STR r1, [sp, #4]
		STR r1, [sp, #0x2c]
		LDR r1, [sp, #0x30]
		STR r0, [sp, #4]
		ADD r1, r1, r7
		STR r1, [sp, #8]
		STR r1, [sp, #0x38]
		ADD r3, r4, #0
		STR r0, [sp, #0x34]
		MOV r0, #0
		ADD r1, sp, #0x14
		ADD r2, sp, #0x34
		BL       |inc_0x331c0_0x341c0| + 0xd68
		ADD r1, r0, #0
		LDR r0, [pc, #0x80]
		LDR r0, [r0]
	INCBIN  baserom.gba_0x33e72_0x33e74.extracted
|sub_08033E74|
|unk_08033E74|
	INCBIN	baserom.gba_0x33e74_0x33e78.extracted
	PUSH     {r4, r5, lr}
	LDR      r0, [pc, #0x70]
	SUB      sp, #0xc
	ADD      r4, r1, #0
	LDR      r0, [r0]
	MOV      r1, #0
	LDR      r2, [pc, #0x6c]
	STR      r1, [sp, #4]
	CMP      r4, #0
	STR      r0, [sp, #8]
	STR      r2, [sp]
	BEQ      |loc_08033E96|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_08033E96|
	MOV      r0, sp
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08033EAA|
	LDR      r1, [pc, #0x50]
	STR      r1, [r0]
|loc_08033EAA|
	ADD      r5, r0, #0
	MOV      r1, #4
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x3c]
	STR      r0, [sp]
	LDR      r0, [sp, #4]
	CMP      r0, #0
	BEQ      |loc_08033ED2|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08033ED2|
	ADD      sp, #0xc
	POP      {r4, r5, pc}
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
|sub_08033EE8|
|unk_08033EE8|
; cited by 0x08033DCA (a pc-relative load targets 0x08033EEC)
	INCBIN	baserom.gba_0x33ee8_0x33efa.extracted
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
|sub_08033F26|
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0xc
	BNE      |sub_08033F48|
	MOV      r0, #0x4c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08033F48|
	ADD      r0, r4, #0
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_08033F48|
|unk_08033F48|
		ADD r2, r7, #0
		MOV r1, #0x40
		ADD r0, r4, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x4712
		LDR r0, [pc, #0x194]
		LDR r3, [pc, #0x194]
		STR r0, [r4]
		LDR r1, [r5]
		LDR r2, [r5, #4]
		MOV r0, #0x16
		STR r0, [r4, #0x48]
		LSL r1, r1, #8
		STR r1, [r4, #0x20]
		LSL r2, r2, #8
		STR r2, [r4, #0x24]
		LDR r0, [r6]
		LDR r1, [r5]
		SUB r0, r0, r1
		LDR r1, [r6, #4]
		LDR r2, [r5, #4]
		STR r0, [sp, #4]
		SUB r1, r1, r2
		STR r1, [sp, #8]
		ADD r1, r0, #0
		LDR r0, [sp, #8]
		MUL r1, r3
		ASR r1, r1, #8
		STR r1, [r4, #0x40]
		LDR r1, [pc, #0x16c]
		MUL r0, r3
		ADD r0, r0, r1
		MOV r1, #1
		LSL r1, r1, #9
		ASR r0, r0, #8
		SUB r0, r0, r1
		STR r0, [r4, #0x44]
		LDR r0, [pc, #0x160]
		STR r0, [r4, #0x18]
		MOV r0, #0x38
		STRB r0, [r4, #8]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		ADD r0, r4, #0
		B        |inc_0x331c0_0x341c0| + 0xd84
		PUSH {r4, r5, r6, r7, lr}
		LDR r2, [r0, #0x44]
		SUB sp, #0x44
		ADD r2, #0x20
		STR r2, [r0, #0x44]
		ADD r4, r0, #0
		ADD r0, #0x40
		ADD r5, r1, #0
		LDR r1, [r4, #0x20]
		LDR r3, [r0]
		ADD r2, #0x20
		ADD r6, r1, r3
		STR r6, [r4, #0x20]
		ADD r1, r0, #4
		LDR r7, [r1]
		LDR r0, [r4, #0x24]
		ADD r0, r0, r7
		STR r0, [r4, #0x24]
		STR r2, [r4, #0x44]
		ADD r2, r6, r3
		STR r2, [r4, #0x20]
		LDR r1, [r1]
		ADD r0, r0, r1
		STR r0, [r4, #0x24]
		ADD r0, r4, #0
		BL       |loc_08019B4E|
		LDR r0, [r4, #0x48]
		SUB r0, #1
		STR r0, [r4, #0x48]
		BNE      |loc_080340C6|
		ADD r6, r4, #0
		ADD r6, #0x20
		ADD r0, r5, #0
		ADD r5, r6, #4
		CMP r0, #0
		BEQ      |loc_08034088|
		LDR r0, [r6]
		LDR r1, [r5]
		ASR r0, r0, #8
		ASR r1, r1, #8
		STR r1, [sp, #0x38]
		STR r1, [sp, #0x40]
		LDR r1, [pc, #0xf8]
		STR r0, [sp, #0x34]
		SUB r1, #0xc
		ADD r1, r1, #4
		STR r0, [sp, #0x3c]
		LDMIA r1!, {r0, r1}
		LDR r2, [r4, #0x1c]
		ADD r3, sp, #0
		STR r2, [sp, #0x28]
		LDRB r2, [r4, #0x10]
		MOV r7, #0
		STRB r2, [r3, #0x1c]
		LDR r2, [pc, #0xe4]
		STR r7, [sp, #0x20]
		STR r2, [sp, #0x24]
		LDR r2, [sp, #0x3c]
		SUB r3, r2, r0
		LDR r2, [sp, #0x40]
		STR r3, [sp]
		SUB r2, r2, r1
		STR r2, [sp, #4]
		STR r2, [sp, #0x10]
		LDR r2, [sp, #0x3c]
		STR r3, [sp, #0xc]
		ADD r0, r2, r0
		LDR r2, [sp, #0x40]
		STR r0, [sp]
		ADD r1, r2, r1
		STR r1, [sp, #4]
		STR r1, [sp, #0x18]
		STR r0, [sp, #0x14]
		LDR r0, [pc, #0xb8]
		ADD r3, sp, #0
		STRB r7, [r3, #8]
		MOV r1, #1
		SUB r0, #0xc
		STR r4, [sp, #0x38]
		LDR r0, [r0]
		ADD r2, sp, #8
		BL       |loc_08011C70|
		CMP r0, #0
		BEQ      |loc_08034088|
		LDR r0, [pc, #0xa0]
		LDR r7, [pc, #0xa8]
		SUB r0, #0xc
		LDR r0, [r0]
		STR r0, [sp, #4]
		MOV r0, #0x10
		DCD     0xFAACF009
		CMP r0, #0
		BEQ      |loc_08034072|
		MOV r1, #1
		STR r1, [r0, #4]
		LDR r1, [pc, #0x94]
		STR r1, [r0]
		STR r7, [r0, #8]
		MOV r7, #0
		STR r7, [r0, #0xc]
|loc_08034072|
		ADD r2, r0, #0
		LDR r0, [sp, #4]
		MOV r1, #0x61
		LSL r1, r1, #4
		ADD r0, r0, r1
		LDR r1, [r0]
		ADD r3, r1, #1
		STR r3, [r0]
		LSL r1, r1, #2
		ADD r0, r1, r0
		STR r2, [r0, #4]
|loc_08034088|
		LDR r7, [pc, #0x68]
		SUB r7, #0xc
		LDR r0, [r7]
		BL       |loc_080116FC|
		MOV r1, #1
		LSL r1, r1, #0xa
		CMP r0, r1
		BLT      |inc_0x331c0_0x341c0| + 0xf1c
		LSL r0, r1, #2
		BL       |inc_0x03d784_0x041118| + 0x2348
		MOV r1, #1
		LSL r1, r1, #0xc
		ADD r0, r0, r1
		LDR r1, [r6]
|loc_080340A8|
|unk_080340A8|
		LDR r2, [r5]
		ASR r1, r1, #8
		ASR r2, r2, #8
		STR r2, [sp, #0x40]
		STR r2, [sp, #0x38]
		MOV r2, #0x38
		STR r1, [sp, #0x34]
		STR r1, [sp, #0x3c]
		MOV r1, #1
		LSL r1, r1, #0xa
		STR r1, [sp, #4]
		STR r2, [sp, #8]
		STR r0, [sp]
		ADD r5, sp, #0x3c
		B        |sub_080340C8|
|loc_080340C6|
		B        |inc_0x331c0_0x341c0| + 0xf24
|sub_080340C8|
	MOV      r3, #4
	ADD      r1, r5, #0
	MOV      r0, #0
	LDR      r2, [pc, #0x34]
	BL       |inc_0x1c3f2_0x2ab4c| + 0xe42a
	ADD      r1, r0, #0
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r1, r4, #0
	LDR      r0, [r7]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
|sub_080340E8|
	DCW      0xce50
	DCW      0x0804,0x05d3,0x0000,0x45a0,0xffff
|sub_080340F4|
	STR      r3, [sp, #0x360]
	LSR      r5, r6, #1
	STRH     r0, [r2, #4]
	LSR      r3, r5, #1
	ADD      r0, #0x84
	LSR      r0, r7, #1
	STR      r2, [sp, #0x190]
	LSR      r4, r0, #0x20
	BLS      |loc_080340A8|
	LSR      r7, r5, #1
	PUSH     {r3, r4, r5, lr}
	LDRB     r3, [r1, #0x10]
	LDRB     r4, [r2]
	MOV      r5, #1
	EOR      r4, r5
	CMP      r3, r4
	BNE      |sub_08034120|
	LDR      r0, [r0, #0xc]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, r4, r5, pc}
|sub_08034120|
|unk_08034120|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0xf5e
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r1, [r4, #4]
		LDR r2, [pc, #0x154]
		ADD r1, #0xff
		ADD r1, #0xad
		LDR r1, [r1]
		LDR r5, [r2]
		SUB sp, #0xc
		STR r1, [r5, #0xc]
		LDR r0, [r0, #4]
		LDR r1, [r4, #8]
		ADD r0, #0xff
		ADD r0, #0xa9
		LDR r0, [r0]
		CMP r1, r0
		BEQ      |loc_0803418A|
		STR r0, [r4, #8]
		LDR r0, [r4, #4]
		ADD r0, #0xff
		ADD r0, #0x81
		LDR r0, [r0, #0x28]
		ASR r6, r0, #0x1f
		ADD r3, r6, #0
		ADD r7, r0, #0
		ADD r2, r0, #0
		ADD r1, r6, #0
		BL       |__16_ll_mul|
		DCW     0xA249
		LDMIA r2!, {r2, r3}
		BL       |sub_08046BA4|
		STR r1, [sp, #8]
		ADD r1, r6, #0
		STR r0, [sp, #4]
		MOV r2, #0xda
		ADD r0, r7, #0
		BL       |sub_08046B64|
		ADD r3, sp, #4
		LDMIA r3!, {r2, r3}
		ADD r0, r0, r2
		ADC r1, r3
		LDR r2, [pc, #0x10c]
		BL       |inc_0x042118_0x049114| + 0x4a00
		MOV r2, #0xa
		BL       |__16_ll_sshift_r|
		STR r0, [r5, #0x10]
|loc_0803418A|
		LDR r1, [r5, #0x10]
		ASR r2, r1, #0xa
		ADD r3, r2, #0
		LSL r0, r2, #0x18
		LSR r2, r0, #0x16
		LDR r0, [pc, #0xf8]
		LSL r1, r1, #0x16
		LDR r6, [r0, r2]
		ADD r2, r3, #1
		LSL r2, r2, #0x18
		LSR r2, r2, #0x16
		LDR r2, [r0, r2]
		LSR r1, r1, #0x16
		MOV ip, r2
		MOV r2, #1
		LSL r2, r2, #0xa
		SUB r2, r2, r1
		ADD r7, r2, #0
		MUL r7, r6
		MOV r6, ip
		MUL r6, r1
		ADD r6, r7, r6
		ASR r6, r6, #0x10
		MOV ip, r6
		ADD r3, #0x40
		LSL r6, r3, #0x18
		ADD r3, #1