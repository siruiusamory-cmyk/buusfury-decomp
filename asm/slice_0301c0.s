	IMPORT |GBARam_Free|
	IMPORT |GBARam_Malloc|
	CODE16
	EXPORT |sub_080301C0|
	EXPORT |loc_080301D8|
	EXPORT |loc_080301E2|
	EXPORT |loc_080301E4|
	EXPORT |sub_08030210|
	EXPORT |sub_08030274|
	EXPORT |loc_080302A2|
	EXPORT |loc_080302BC|
	EXPORT |loc_080302CC|
	EXPORT |loc_0803031C|
	EXPORT |loc_0803031E|
	EXPORT |sub_080303A0|
	EXPORT |sub_080303C4|
	EXPORT |loc_08030402|
	EXPORT |loc_08030424|
	EXPORT |loc_0803042E|
	EXPORT |sub_0803043A|
	EXPORT |sub_0803043E|
	EXPORT |sub_0803046E|
	EXPORT |sub_080304DE|
	EXPORT |loc_0803054E|
	EXPORT |loc_08030582|
	EXPORT |loc_080305A8|
	EXPORT |sub_08030604|
	EXPORT |sub_08030606|
	EXPORT |sub_08030630|
	EXPORT |sub_08030740|
	EXPORT |loc_0803076E|
	EXPORT |loc_080307B0|
	EXPORT |loc_080307F6|
	EXPORT |sub_080307FA|
	EXPORT |sub_08030838|
	EXPORT |loc_08030840|
	EXPORT |sub_0803084C|
	EXPORT |sub_08030850|
	EXPORT |loc_08030860|
	EXPORT |sub_0803087E|
	EXPORT |sub_08030950|
	EXPORT |loc_08030992|
	EXPORT |loc_080309CE|
	EXPORT |loc_080309D6|
	EXPORT |loc_080309E6|
	EXPORT |sub_08030A0C|
	EXPORT |sub_08030A42|
	EXPORT |loc_08030A64|
	EXPORT |sub_08030A68|
	EXPORT |sub_08030AA2|
	EXPORT |loc_08030AC4|
	EXPORT |loc_08030AD4|
	EXPORT |sub_08030AD8|
	EXPORT |loc_08030AE4|
	EXPORT |sub_08030B14|
	EXPORT |loc_08030B42|
	EXPORT |loc_08030B5A|
	EXPORT |loc_08030B66|
	EXPORT |loc_08030B90|
	EXPORT |loc_08030BA4|
	EXPORT |loc_08030BC2|
	EXPORT |sub_08030BCC|
	EXPORT |sub_08030BCE|
	EXPORT |loc_08030BE4|
	EXPORT |loc_08030BEE|
	EXPORT |loc_08030BF0|
	EXPORT |loc_08030C12|
	EXPORT |Bg_WriteScroll0AndBlendAlpha|
	EXPORT |Blend_WriteControlAndAlpha5|
	EXPORT |loc_08030FA4|
	EXPORT |loc_08030FB2|
	EXPORT |sub_08030FB4|
	EXPORT |sub_08030FB8|
	EXPORT |loc_08030FE6|
	EXPORT |loc_08030FFA|
	EXPORT |sub_0803101A|
|sub_080301C0|
	MOV      r3, #0xf3
	LDRH     r1, [r1, #4]
	AND      r1, r3
	LDR      r3, [r0, #0x20]
	BEQ      |loc_080301E4|
	ADD      r3, #0xa
	STR      r3, [r0, #0x20]
	CMP      r3, #0x55
	BLT      |loc_080301D8|
	MOV      r1, #0x55
	STR      r1, [r0, #0x20]
	STR      r2, [r0, #0x24]
|loc_080301D8|
	LDR      r1, [r0, #0x20]
	LDR      r2, [r0, #0x1c]
	CMP      r2, r1
	BGE      |loc_080301E2|
	STR      r1, [r0, #0x1c]
|loc_080301E2|
	BX       lr
|loc_080301E4|
	ADD      r1, r3, #0
	LSL      r3, r1, #5
	SUB      r1, r3, r1
	ASR      r1, r1, #5
	STR      r1, [r0, #0x20]
	BX       lr
	LDRB     r4, [r3, #0xd]
	LSR      r5, r6, #1
|unk_080301F4|
	INCBIN	baserom.gba_0x301f4_0x301f6.extracted
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08030210|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08030210|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08030210|
|unk_08030210|
		LDR r0, [pc, #0x158]
		MOV r6, #7
		LSL r6, r6, #7
		LDR r5, [pc, #0x158]
		STR r0, [r4]
		STRH r6, [r4, #0xe]
		LDR r0, [r5]
		ADD r1, r6, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08030238|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |sub_08011732|
		ADD r1, r6, #0
		LDR r0, [r5]
		BL       |loc_0801124C|
|loc_08030238|
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		LDR r1, [pc, #0x134]
		STRH r0, [r4, #0xc]
		STR r1, [r4]
		LDR r1, [r7, #4]
		LDR r2, [r7]
		STR r1, [r4, #0x14]
		STR r2, [r4, #0x10]
		MOV r2, #0x55
		STR r2, [r4, #0x20]
		MOV r2, #0
		MVN r2, r2
		STR r2, [r4, #0x18]
		STR r2, [r4, #0x1c]
		MOV r2, #0x10
		STRB r2, [r4, #8]
		STR r1, [r4, #4]
		LDR r1, [pc, #0x118]
		LSL r0, r0, #5
		ADD r0, r0, r1
		LSR r1, r1, #0x11
		ADD r0, r0, r1
		LDR r1, [pc, #0x108]
		MOV r2, #0x80
		ADD r1, #4
		BL       |Thunk_VramCopy|
		ADD r0, r4, #0
		B        |inc_0x301c0_0x311c0| + 0x4e
|sub_08030274|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x20]
	ADD      r5, r1, #0
	LDR      r1, [r4, #0x18]
	SUB      sp, #0x1fc
	SUB      sp, #0x108
	CMP      r0, r1
	BEQ      |loc_080302CC|
	LDR      r1, [pc, #0xe8]
	MOV      r2, #3
	LSL      r2, r2, #8
	ADD      r6, sp, #4
	STR      r0, [r4, #0x18]
	ADD      r1, #0x84
	ADD      r0, r6, #0
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [r4, #0x20]
	CMP      r0, #0x55
	BGE      |loc_080302BC|
	LDR      r7, [pc, #0xdc]
	MOV      r1, #1
|loc_080302A2|
	LSL      r2, r0, #3
	LDRH     r3, [r7, r2]
	ADD      r2, r2, r7
	ADD      r0, #1
	STRB     r1, [r6, r3]
	LDRH     r3, [r2, #2]
	CMP      r0, #0x55
	STRB     r1, [r6, r3]
	LDRH     r3, [r2, #4]
	STRB     r1, [r6, r3]
	LDRH     r2, [r2, #6]
	STRB     r1, [r6, r2]
	BLT      |loc_080302A2|
|loc_080302BC|
	LDRH     r0, [r4, #0xc]
	LDR      r1, [pc, #0xb8]
	LSL      r0, r0, #5
	ADD      r0, r0, r1
	LSR      r2, r1, #0x11
	ADD      r1, r6, #0
	BL       |inc_0x049120_0x055620| + 0x18
|loc_080302CC|
	LDR      r0, [r5]
	LDR      r1, [r4, #0x1c]
	MOV      r2, #1
	MOV      r6, #3
	LSL      r6, r6, #0xa
	LSL      r2, r2, #0xa
	ADD      r3, r1, #1
	BEQ      |loc_0803031C|
	MOV      r7, #5
	LSL      r7, r7, #0xd
	STR      r7, [r0]
	LDR      r1, [r4, #0x10]
	LDR      r3, [r4, #0x1c]
	ADD      r1, r1, r3
	ADD      r1, #1
	LSL      r1, r1, #0x17
	LSR      r1, r1, #7
	ORR      r1, r7
	STR      r1, [r0]
	LDR      r3, [r4, #0x14]
	LSR      r1, r1, #8
	ADD      r3, #0xfd
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r1, r1, #8
	ORR      r1, r3
	STR      r1, [r0]
	LDR      r1, [r0, #4]
	BIC      r1, r6
	ADD      r1, r1, r2
	STR      r1, [r0, #4]
	LDRH     r3, [r4, #0xc]
	LSR      r1, r1, #0xa
	LSL      r1, r1, #0xa
	ADD      r3, #0x18
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	ORR      r1, r3
	STR      r1, [r0, #4]
	ADD      r0, #8
|loc_0803031C|
	MOV      r1, #0
|loc_0803031E|
	LDR      r7, [pc, #0x60]
	LSL      r3, r1, #5
	STR      r7, [r0]
	LDR      r2, [r4, #0x10]
	ADD      r2, r2, r3
	LSL      r2, r2, #0x17
	LSR      r2, r2, #7
	ORR      r2, r7
	STR      r2, [r0]
	LDR      r3, [r4, #0x14]
	LSR      r2, r2, #8
	LSL      r3, r3, #0x18
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r0]
	LDR      r2, [r0, #4]
	LSR      r3, r7, #0x14
	BIC      r2, r6
	ADD      r2, r2, r3
	STR      r2, [r0, #4]
	LDRH     r3, [r4, #0xc]
	LSL      r7, r1, #3
	LSR      r2, r2, #0xa
	ADD      r3, r3, r7
	LSL      r3, r3, #0x16
	LSR      r3, r3, #0x16
	LSL      r2, r2, #0xa
	ORR      r2, r3
	STR      r2, [r0, #4]
	ADD      r0, #8
	ADD      r1, #1
	CMP      r1, #3
	BLT      |loc_0803031E|
	STR      r0, [r5]
	ADD      sp, #0x1fc
	ADD      sp, #0x108
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
	LDRB     r4, [r4, #0xd]
	LSR      r5, r6, #1
	STMIA    r0!, {r5}
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	LDRB     r0, [r5, #0x1b]
	LSR      r5, r6, #1
	STR      r0, [r0]
	AND      r0, r0
	PUSH     {r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0xc
	BNE      |sub_080303A0|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080303A0|
	ADD      r0, r4, #0
	ADD      sp, #0xc
	POP      {r4, r5, pc}
|sub_080303A0|
|unk_080303A0|
		LDR r0, [pc, #0x9c]
		ADD r1, r5, #0
		STR r0, [r4]
		MOV r0, #0
		BL       |inc_0x301c0_0x311c0| + 0x834
		STR r0, [r4, #4]
		MOV r0, #0x78
		STR r0, [sp, #4]
		MOV r0, #0x94
		STR r0, [sp, #8]
		MOV r0, #0x98
		ADD r1, sp, #4
		BL       |sub_08030950|
		STR r0, [r4, #8]
		ADD r0, r4, #0
		B        |inc_0x301c0_0x311c0| + 0x1dc
|sub_080303C4|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x7c]
	LDR      r1, [r0, #4]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [r4, #8]
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x64]
	LDR      r1, [r0, #8]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r1, [r4, #4]
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      r0, r4, #0
	BEQ      |loc_08030402|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08030402|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #4]
	LDR      r0, [r0, #0x2c]
	CMP      r0, #0
	BEQ      |sub_0803043A|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
|loc_08030424|
	BEQ      |loc_0803042E|
	LDR      r1, [pc, #0x20]
	STR      r1, [r0]
	MOV      r1, #0x1e
	STR      r1, [r0, #4]
|loc_0803042E|
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r0, [r4, #4]
	LDR      r0, [r0, #0x1c]
	ADD      r0, #1
	POP      {r4, pc}
|sub_0803043A|
|unk_0803043A|
		MOV r0, #0
		POP {r4, pc}
|sub_0803043E|
	LSL      r0, r0, #0
	BHI      |loc_08030424|
	LSR      r4, r0, #0x20
	STRH     r0, [r2, #0xc]
	LSR      r5, r6, #1
	LDR      r1, [sp, #0x1e0]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r1, #0
	MOV      r0, #0x2d
	SUB      sp, #0x2c
	BL       |inc_0x0158_0x143f2|
	ADD      r2, r0, #0
	LDR      r6, [pc, #0x80]
	MOV      r1, #5
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x11b18
	CMP      r0, #0
	BEQ      |sub_0803046E|
	MOV      r0, #1
	ADD      sp, #0x2c
	POP      {r4, r5, r6, r7, pc}
|sub_0803046E|
|unk_0803046E|
		ADD r5, r4, #0
		ADD r5, #0xff
		ADD r5, #0xa1
		LDR r0, [r5, #4]
		LDR r1, [r5]
		STR r0, [sp, #0x28]
		STR r1, [sp, #0x24]
		LDR r1, [sp, #0x28]
		MOV r0, #1
		LSL r0, r0, #0xe
		ADD r0, r1, r0
		STR r0, [sp, #0x28]
		MOV r0, #0x2d
		ADD r7, sp, #0x24
		BL       |inc_0x0158_0x143f2|
		ADD r2, r0, #0
		ADD r2, #8
		ADD r1, r7, #0
		LDR r0, [r6, #4]
		BL       |loc_08009904|
		CMP r0, #0
		BNE      |loc_080304A2|
		MOV r0, #1
		B        |inc_0x301c0_0x311c0| + 0x2aa
|loc_080304A2|
		LDR r1, [pc, #0x38]
		MOV r2, #0x20
		ADD r7, sp, #4
		ADD r1, #8
		ADD r0, r7, #0
		BL       |Thunk_VramCopy|
		LDR r0, [r5]
		ADD r3, sp, #0
		ASR r0, r0, #8
		STRH r0, [r3, #0x10]
		MOV r0, #0xff
		ADD r0, #0xa5
		LDR r0, [r0, r4]
		LDR r2, [pc, #0x20]
		ASR r0, r0, #8
		STRH r0, [r3, #0x12]
		MOV r3, #0
		MVN r3, r3
		ADD r1, r7, #0
		MOV r0, #0
		BL       |loc_0800F68C|
		ADD r1, r0, #0
		LDR r0, [r6]
		BL       |List_Append|
		MOV r0, #1
		B        |inc_0x301c0_0x311c0| + 0x2aa
	INCBIN  baserom.gba_0x304dc_0x304de.extracted
|sub_080304DE|
	LSR      r5, r6, #1
	ASR      r4, r7, #0xf
	LSR      r1, r6, #1
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r0, #0
	MOV      r5, #0
	STRH     r5, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	MOV      r0, #0xff
	ADD      r0, #0x77
	STRB     r5, [r1, #0x11]
	STRH     r5, [r0, r1]
	ADD      r0, r1, #0
	ADD      r4, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [pc, #0xf8]
	ADD      r0, r4, #0
	LDR      r1, [r1]
	ADD      r0, #0xff
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r2}
	ADD      r0, #0xa1
	STMIA    r0!, {r2}
	LDR      r1, [r1]
	STR      r1, [r0]
	LDR      r1, [r0]
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r1, [r0]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	STRB     r5, [r6, #4]
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	LDR      r0, [pc, #0xcc]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	MOV      r2, #0xf0
	LDRH     r1, [r1, #4]
	AND      r1, r2
	BEQ      |loc_0803054E|
	LDRH     r1, [r4, #0x12]
	ADD      r1, #2
	STRH     r1, [r4, #0x12]
|loc_0803054E|
	MOV      r3, #0x5a
	MOV      r2, #0x10
	MOV      r1, #0xf3
	LDR      r0, [r0]
	BL       |inc_0x03d784_0x041118| + 0x2b00
	CMP      r0, #0
	BEQ      |loc_08030582|
	LDR      r0, [pc, #0xa4]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0
	STRB     r0, [r4, #0x11]
	STRH     r0, [r4, #0x12]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08030582|
	POP      {r4, pc}
	LDRH     r0, [r1, #0x12]
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STRH     r0, [r1, #0x12]
	CMP      r0, #7
	BLS      |loc_080305A8|
	MOV      r0, #0
	STRH     r0, [r1, #0x12]
	LDRB     r0, [r1, #0x11]
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRB     r0, [r1, #0x11]
	CMP      r0, #5
	BLS      |loc_080305A8|
	MOV      r0, #4
	STRB     r0, [r1, #0x11]
|loc_080305A8|
	BX       lr
	PUSH     {r4, r5, r6, lr}
	LDR      r6, [pc, #0x54]
	ADD      r5, r1, #0
	LDR      r4, [r6]
	MOV      r0, #0
	STRB     r0, [r4, #0x11]
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x4c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r1, [pc, #0x48]
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x10a60
	MOV      r1, #0x12
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x38]
	ADD      r1, #8
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x1c]
	LDR      r0, [r4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [pc, #0x1c]
	LDR      r0, [r4]
	BL       |inc_0x0158_0x143f2| + 0x10a60
	POP      {r4, pc}
	LDR      r0, [pc, #0x10]
	ADD      r0, #4
	BX       lr
|sub_08030604|
|unk_08030604|
	INCBIN	baserom.gba_0x30604_0x30606.extracted
|sub_08030606|
	LSL      r0, r0, #0xc
	STRH     r0, [r1, #0xe]
	LSR      r5, r6, #1
	SUB      r0, r0, r4
	LSL      r0, r0, #0xc
	ADD      r1, #0x44
	LSL      r0, r0, #0xc
	ADD      r4, r7, #0
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	MOV      r3, #0
	STRH     r3, [r1, #0x12]
	MOV      r2, #0x38
	STRB     r2, [r1, #8]
	STRB     r3, [r1, #0x11]
	LDR      r2, [r0]
	LDR      r3, [r2, #8]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
|sub_08030630|
|unk_08030630|
		PUSH {r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		LDR r0, [pc, #0x218]
		ADD r4, r1, #0
		LDR r7, [r0]
		SUB sp, #0x44
		CMP r7, #0
		BEQ      |loc_08030722|
		LDRH r0, [r4, #0x12]
		ADD r6, r5, #4
		ADD r3, r6, #4
		STR r3, [sp, #0x40]
		CMP r0, #0
		BNE      |loc_08030724|
		ADD r1, r7, #0
		ADD r0, sp, #0x10
		BL       |sub_0800FDFA|
		ADD r1, sp, #0x10
		ADD r0, sp, #0x20
		BL       |inc_0x049120_0x055620| + 0x67e0
		ADD r1, r4, #0
		ADD r0, sp, #0x28
		BL       |sub_0800FDFA|
		ADD r1, sp, #0x28
		ADD r0, sp, #0x38
		BL       |inc_0x049120_0x055620| + 0x67e0
		LDR r0, [sp, #0x20]
		LDR r1, [sp, #0x38]
		LDR r2, [sp, #0x3c]
		SUB r0, r0, r1
		LDR r1, [sp, #0x24]
		STR r0, [sp, #8]
		SUB r1, r1, r2
		MOV r2, #1
		ADD r3, r2, #0
		CMP r0, #0
		STR r1, [sp, #0xc]
		BGT      |loc_08030686|
		NEG r3, r2
|loc_08030686|
		LSL r3, r3, #8
		MOV r2, #1
		CMP r1, #0
		BGT      |loc_08030690|
		NEG r2, r2
|loc_08030690|
		STR r3, [r6]
		LDR r3, [sp, #0x40]
		LSL r2, r2, #8
		STR r2, [r3]
		MOV r2, #0x20
		NEG r3, r2
		CMP r0, #0
		BGT      |loc_080306A2|
		ADD r2, r3, #0
|loc_080306A2|
		MOV r0, #0x20
		CMP r1, #0
		BGT      |loc_080306AA|
		ADD r0, r3, #0
|loc_080306AA|
		ADD r1, r7, #0
		ADD r7, sp, #8
		STR r0, [sp, #0x3c]
		ADD r0, r7, #0
		STR r2, [sp, #0x38]
		BL       |sub_0800FDFA|
		ADD r1, r7, #0
		ADD r0, sp, #0x18
		BL       |inc_0x049120_0x055620| + 0x67e0
		ADD r1, r4, #0
		ADD r7, sp, #0x20
		ADD r0, r7, #0
		BL       |sub_0800FDFA|
		ADD r1, r7, #0
		ADD r0, sp, #0x30
		BL       |inc_0x049120_0x055620| + 0x67e0
		LDR r0, [sp, #0x30]
		LDR r2, [sp, #0x38]
		MOV r3, #1
		ADD r1, r0, r2
		LDR r0, [sp, #0x3c]
		LDR r2, [sp, #0x34]
		STR r1, [sp]
		ADD r0, r2, r0
		LDR r2, [sp, #0x18]
		STR r0, [sp, #4]
		SUB r1, r2, r1
		LDR r2, [sp, #0x1c]
		STR r1, [sp]
		SUB r0, r2, r0
		ADD r2, r3, #0
		CMP r1, #0
		STR r0, [sp, #4]
		BGT      |loc_080306F8|
		NEG r2, r2
|loc_080306F8|
		LSL r1, r2, #8
		CMP r0, #0
		BGT      |loc_08030702|
		MOV r3, #0
		MVN r3, r3
|loc_08030702|
		LSL r0, r3, #8
		STR r0, [sp, #0x34]
		STR r1, [sp, #0x30]
		LDR r0, [r5, #4]
		MUL r0, r1
		ASR r0, r0, #8
		MOV r1, #0
		CMP r0, #0
		BGE      |loc_08030726|
		LDR r0, [r5, #8]
		LDR r2, [sp, #0x34]
		MUL r0, r2
		ASR r0, r0, #8
		BPL      |loc_08030726|
		MOV r0, #1
		B        |loc_08030728|
|loc_08030722|
		B        |loc_080307F6|
|loc_08030724|
		B        |inc_0x301c0_0x311c0| + 0x58a
|loc_08030726|
		MOV r0, #0
|loc_08030728|
		STRB r0, [r5, #0xc]
		STRB r1, [r4, #0x11]
		LDRB r0, [r5, #0xc]
		CMP r0, #0
		BEQ      |sub_08030740|
		CMP r0, #1
		BNE      |inc_0x301c0_0x311c0| + 0x58a
		MOV r1, #0xe
		ADD r0, r4, #0
		BL       |Record_SelectIndexed|
		B        |inc_0x301c0_0x311c0| + 0x58a
|sub_08030740|
	STRH     r1, [r4, #0x12]
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r7, r4, #0
	LDRB     r0, [r5, #0xc]
	ADD      r7, #0xff
	ADD      r7, #0xa1
	CMP      r0, #0
	BEQ      |loc_0803076E|
	LDR      r0, [r6]
	LDR      r3, [sp, #0x40]
	LSL      r0, r0, #9
	LDR      r1, [r3]
	ASR      r0, r0, #8
	LSL      r1, r1, #9
	ASR      r1, r1, #8
	STR      r1, [sp, #0x24]
	STR      r1, [sp, #0x2c]
	STR      r0, [sp, #0x20]
	STR      r0, [sp, #0x28]
	ADD      r6, sp, #0x28
|loc_0803076E|
	LDR      r0, [r7]
	LDR      r1, [r6]
	LDR      r2, [r7, #4]
	ADD      r0, r0, r1
	LDR      r1, [r6, #4]
	STR      r0, [sp, #0x20]
	ADD      r1, r2, r1
	STR      r1, [sp, #0x24]
	STR      r1, [sp, #0x34]
	STR      r1, [sp, #0x3c]
	STR      r0, [sp, #0x30]
	STR      r0, [sp, #0x38]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r5, r7, #4
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x54]
	ADD      r2, r2, r1
	ADD      r1, sp, #0x38
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BEQ      |loc_080307B0|
	LDR      r0, [sp, #0x38]
	STR      r0, [r7]
	LDR      r0, [sp, #0x3c]
	STR      r0, [r5]
|loc_080307B0|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x48]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r1, r4, #0
	ADD      r0, sp, #0x18
	BL       |inc_0x0158_0x143f2| + 0xfd20
	LDR      r0, [pc, #0x8c]
	LDR      r1, [r0]
	ADD      r0, sp, #0x28
	BL       |inc_0x0158_0x143f2| + 0xfd20
	LDR      r0, [sp, #0x18]
	LDR      r1, [sp, #0x30]
	CMP      r0, r1
	BGE      |loc_080307F6|
	LDR      r0, [sp, #0x28]
	LDR      r1, [sp, #0x20]
	CMP      r0, r1
	BGE      |loc_080307F6|
	LDR      r0, [sp, #0x1c]
	LDR      r1, [sp, #0x34]
	CMP      r0, r1
	BGE      |loc_080307F6|
	LDR      r0, [sp, #0x2c]
	LDR      r1, [sp, #0x24]
	CMP      r0, r1
	BGE      |loc_080307F6|
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xed20
|loc_080307F6|
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
|sub_080307FA|
|unk_080307FA|
		PUSH {r4}
		LDRB r3, [r0, #0xc]
		ADD r2, r1, #0
		ADD r2, #0xff
		ADD r2, #0x61
		CMP r3, #0
		LDRH r0, [r1, #0x12]
		LDR r4, [pc, #0x4c]
		BEQ      |loc_08030826|
		CMP r3, #1
		BNE      |loc_08030840|
		LSL r3, r0, #0x18
		LSR r3, r3, #0x16
		LDR r3, [r4, r3]
		NEG r3, r3
		ASR r3, r3, #0xb
		STRH r3, [r2, #0x16]
		CMP r0, #0x30
		BNE      |sub_08030838|
		MOV r2, #1
		STRB r2, [r1, #0x11]
		B        |loc_08030840|
|loc_08030826|
		MOV r3, #0
		STRB r3, [r1, #0x11]
		LSL r3, r0, #0x18
		LSR r3, r3, #0x16
		LDR r3, [r4, r3]
		NEG r3, r3
		ASR r3, r3, #0xd
		STRH r3, [r2, #0x16]
		B        |loc_08030840|
|sub_08030838|
	CMP      r0, #0x50
	BNE      |loc_08030840|
	MOV      r2, #2
	STRB     r2, [r1, #0x11]
|loc_08030840|
	ADD      r0, #8
	LSL      r0, r0, #0x19
	LSR      r0, r0, #0x19
	STRH     r0, [r1, #0x12]
	POP      {r4}
	BX       lr
|sub_0803084C|
|unk_0803084C|
	INCBIN	baserom.gba_0x3084c_0x30850.extracted
|sub_08030850|
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	LDR      r4, [r5, #0x6c]
	LSR      r3, r7, #1
	ADD      r1, #0x54
	LSL      r0, r0, #0xc
|loc_08030860|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r7, r3, #0
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x44
	BNE      |sub_0803087E|
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0803087E|
	ADD      r0, r4, #0
	ADD      sp, #0x54
	POP      {r4, r5, r6, r7, pc}
|sub_0803087E|
|unk_0803087E|
		LDR r0, [pc, #0x158]
		LSL r5, r6, #4
		STR r0, [r4]
		LDR r0, [pc, #0x154]
		STRH r5, [r4, #0xe]
		LDR r0, [r0]
		ADD r1, r5, #0
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_080308A8|
		LDR r0, [pc, #0x144]
		ADD r1, r5, #0
		LDR r0, [r0]
		BL       |sub_08011732|
		LDR r0, [pc, #0x13c]
		ADD r1, r5, #0
		LDR r0, [r0]
		BL       |loc_0801124C|
|loc_080308A8|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x134]
		MOV r2, #0x10
		MOV r5, sp
		STR r0, [r4]
		ADD r5, r5, r2
		ADD r1, r6, #0
		ADD r0, r5, #0
		STR r6, [r4, #0x10]
		BL       |loc_0803F540|
		LDR r0, [pc, #0x11c]
		ADD r3, sp, #0
		LDR r0, [r0, #4]
		MOV r1, #2
		STR r0, [sp, #0x1c]
		MOV r0, #1
		STRB r0, [r3, #0x10]
		STRB r1, [r3, #0x13]
		STRB r0, [r3, #0x12]
		LDR r0, [pc, #0x110]
		STR r0, [sp, #0x30]
		LDR r0, [r4, #0x10]
		LDR r2, [sp, #0x40]
		LSR r1, r0, #0x1f
		ADD r0, r1, r0
		ASR r0, r0, #1
		STR r0, [sp, #0x14]
		MOV r0, #0xc
		STR r0, [sp, #0x18]
		LDR r0, [sp, #0x34]
		MOV r1, #0
		BL       |sub_08046E40|
		ADD r0, r5, #0
		LDR r1, [sp, #0x4c]
		BL       |loc_0803DADA|
		LDR r0, [r4, #0x10]
		LSR r1, r0, #0x1f
		ADD r0, r1, r0
		LDR r1, [r7]
		ASR r0, r0, #1
		SUB r0, r1, r0
		STR r0, [r4, #0x14]
		LDR r0, [r7, #4]
		SUB r0, #8
		STR r0, [r4, #0x18]
		MOV r0, #0
		STR r0, [sp, #4]
		MOV r0, #0x10
		STR r0, [sp, #0xc]
		LDR r1, [r4, #0x10]
		MOV r0, #0
		CMP r1, #0
		BLE      |loc_0803093E|
		MOV r7, sp
|loc_0803091A|
		ADD r6, r0, #0
		ADD r6, #0x20
		STR r6, [sp, #8]
		STR r0, [sp]
		LDRH r1, [r4, #0xc]
		LDR r2, [pc, #0xc0]
		LSL r0, r0, #4
		LSL r1, r1, #5
		ADD r1, r1, r2
		ADD r1, r1, r0
		ADD r2, r7, #0
		ADD r0, r5, #0
		BL       |sub_0804915C|
		LDR r1, [r4, #0x10]
		ADD r0, r6, #0
		CMP r1, r6
		BGT      |loc_0803091A|
|loc_0803093E|
		MOV r0, #0
		STR r0, [r4, #4]
		STRB r0, [r4, #8]
		MOV r1, #0
		ADD r0, r5, #0
		BL       |sub_0803F58C|
		ADD r0, r4, #0
		B        |inc_0x301c0_0x311c0| + 0x6ba
|sub_08030950|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	LDR      r1, [pc, #0x94]
	LSL      r0, r0, #2
	LDR      r4, [r1, r0]
	LDR      r6, [pc, #0x80]
	ADD      r1, r4, #0
	LDR      r0, [r6, #4]
	BL       |inc_0x03d784_0x041118| + 0x2864
	ADD      r0, #0x21
	LSR      r5, r0, #5
	LSL      r5, r5, #5
	LSL      r1, r5, #4
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x115da
	ADD      r3, r7, #0
	ADD      r2, r4, #0
	ADD      r1, r5, #0
	MOV      r0, #0
	BL       |loc_08030860|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, r7}
	LDR      r2, [r1]
	LDR      r4, [r0, #0x10]
	MOV      r3, #0
	CMP      r4, #0
	BLE      |loc_080309CE|
	MOV      r6, #3
	LDR      r7, [pc, #0x60]
	LSL      r6, r6, #0xa
|loc_08030992|
	STR      r7, [r2]
	LDR      r4, [r0, #0x14]
	ADD      r4, r4, r3
	LSL      r4, r4, #0x17
	LSR      r4, r4, #7
	ORR      r4, r7
	STR      r4, [r2]
	LDR      r5, [r0, #0x18]
	LSR      r4, r4, #8
	LSL      r5, r5, #0x18
	LSR      r5, r5, #0x18
	LSL      r4, r4, #8
	ORR      r4, r5
	STR      r4, [r2]
	LDRH     r4, [r0, #0xc]
	ASR      r5, r3, #1
	ADD      r3, #0x20
	ADD      r4, r4, r5
	LDR      r5, [r2, #4]
	LSL      r4, r4, #0x16
	LSR      r5, r5, #0xa
	LSL      r5, r5, #0xa
	LSR      r4, r4, #0x16
	ORR      r4, r5
	BIC      r4, r6
	STR      r4, [r2, #4]
	LDR      r4, [r0, #0x10]
	ADD      r2, #8
	CMP      r4, r3
	BGT      |loc_08030992|
|loc_080309CE|
	STR      r2, [r1]
	POP      {r4, r5, r6, r7}
	MOV      r0, #0
	BX       lr
|loc_080309D6|
	DCW      0x0000
	DCW      0x9680,0x0804,0x81e4,0x0875,0xaf78,0x0804,0xf70d
|loc_080309E6|
	LSR      r3, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	STR      r0, [r0]
	STRH     r0, [r0]
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08030A0C|
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08030A0C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
|sub_08030A0C|
|unk_08030A0C|
		LDR r1, [pc, #0x94]
		ADD r0, r4, #0
		BL       |inc_0x301c0_0x311c0| + 0x38
		LDR r0, [pc, #0x90]
		STR r0, [r4]
		MOV r0, #0
		STR r0, [r4, #0x24]
		STR r0, [r4, #0x2c]
		MOV r0, #0x29
		LSL r0, r0, #4
		MUL r0, r5
		ASR r0, r0, #8
		STR r0, [r4, #0x28]
		ADD r0, r4, #0
		B        |inc_0x301c0_0x311c0| + 0x84a
		LDR r1, [r0, #0x2c]
		CMP r1, #0
		BEQ      |inc_0x301c0_0x311c0| + 0x888
		LDR r1, [pc, #0x78]
		LDR r1, [r1, #4]
		LSL r1, r1, #0x1d
		BPL      |sub_08030A42|
		LDR r1, [r0, #0x24]
		ASR r1, r1, #8
		STR r1, [r0, #0x1c]
		B        |inc_0x301c0_0x311c0| + 0x888
|sub_08030A42|
	MOV      r1, #0
	MVN      r1, r1
	STR      r1, [r0, #0x1c]
	MOV      r0, #1
	BX       lr
	PUSH     {r4}
	LDR      r1, [r0, #0x2c]
	CMP      r1, #0
	BNE      |loc_08030A64|
	LDR      r1, [pc, #0x4c]
	SUB      r1, #8
	LDR      r1, [r1]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x1f
	BEQ      |sub_08030A68|
	MOV      r1, #1
	STR      r1, [r0, #0x2c]
|loc_08030A64|
	POP      {r4}
	BX       lr
|sub_08030A68|
|unk_08030A68|
		LDR r1, [r0, #0x24]
		LDR r2, [r0, #0x28]
		ADD r1, r1, r2
		ADD r2, r0, #0
		ADD r2, #0x28
		SUB r3, r2, #4
		CMP r1, #0
		STR r1, [r0, #0x24]
		BGE      |loc_08030A86|
		NEG r1, r1
		STR r1, [r3]
		LDR r1, [r0, #0x28]
		NEG r1, r1
		STR r1, [r2]
		B        |loc_08030A9A|
|loc_08030A86|
		MOV r4, #0x55
		LSL r4, r4, #8
		CMP r1, r4
		BLE      |loc_08030A9A|
		LSL r4, r4, #1
		SUB r1, r4, r1
		STR r1, [r3]
		LDR r1, [r0, #0x28]
		NEG r1, r1
		STR r1, [r2]
|loc_08030A9A|
		LDR r1, [r0, #0x24]
		ASR r1, r1, #8
		STR r1, [r0, #0x1c]
		B        |loc_08030A64|
|sub_08030AA2|
	LSL      r0, r0, #0
	STRH     r4, [r6, #0xe]
	LSR      r5, r6, #1
	BCS      |loc_08030AC4|
	LSR      r4, r0, #0x20
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, lr}
	LDR      r5, [r1, #4]
	LDR      r1, [r0, #8]
	SUB      sp, #0x38
	ADD      r1, #1
	STR      r1, [r0, #8]
	LSL      r2, r1, #0x1d
	BNE      |loc_08030AD4|
	ASR      r4, r1, #3
	LDR      r2, [r0, #0x10]
|loc_08030AC4|
	MOV      r1, #1
	CMP      r2, #0
	BEQ      |sub_08030AD8|
	CMP      r4, #8
	BLT      |loc_08030AE4|
	MOV      r2, #0
	STR      r2, [r5, #0x1c]
	STR      r1, [r0, #0xc]
|loc_08030AD4|
	ADD      sp, #0x38
	POP      {r4, r5, r6, pc}
|sub_08030AD8|
|unk_08030AD8|
		CMP r4, #5
		BLT      |loc_08030AE0|
		STR r1, [r0, #0xc]
		B        |loc_08030AD4|
|loc_08030AE0|
		LDR r0, [pc, #0x34]
		LDRB r4, [r0, r4]
|loc_08030AE4|
|unk_08030AE4|
		MOV r2, #0x40
		MOV r1, #0x40
		ADD r6, sp, #4
		ADD r0, r6, #0
		BL       |loc_0803F540|
		LDR r2, [pc, #0x24]
		LSL r1, r4, #2
		ADD r2, #8
		ADD r1, r1, r2
		LDR r0, [sp, #0x28]
		LDR r1, [r1, #4]
		BL       |inc_0x049120_0x055620|
		LDRH r0, [r5, #0x16]
		LDR r1, [pc, #0x18]
		LSL r0, r0, #5
		ADD r1, r0, r1
		ADD r0, r6, #0
		BL       |inc_0x03d784_0x041118| + 0x2234
		MOV r1, #0
		ADD r0, r6, #0
	INCBIN  baserom.gba_0x30b12_0x30b14.extracted
|sub_08030B14|
|unk_08030B14|
	INCBIN	baserom.gba_0x30b14_0x30b18.extracted
	STRH     r4, [r7, #0xe]
	LSR      r5, r6, #1
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
|unk_08030B20|
	MOV      r0, #1
	BX       lr
|unk_08030B24|
	LDR      r1, [r0, #0x58]
	MOV      r3, #0x10
	SUB      r1, #1
	ADD      r2, r1, #0
	STR      r1, [r0, #0x58]
	LDR      r1, [pc, #0x3c4]
	STRB     r2, [r1, #2]
	LDR      r2, [r0, #0x58]
	SUB      r2, r3, r2
	STRB     r2, [r1, #3]
	LDR      r0, [r0, #0x58]
	MOV      r1, #1
	CMP      r0, #0
	BEQ      |loc_08030B42|
	MOV      r1, #0
|loc_08030B42|
	ADD      r0, r1, #0
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x54]
	CMP      r0, #0
	BEQ      |loc_08030B5A|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x3a4]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_08030B5A|
	LDR      r0, [r4, #0x5c]
	CMP      r0, #0
	BEQ      |loc_08030B66|
	LDR      r0, [pc, #0x398]
	STR      r0, [r4, #0x60]
	POP      {r4, pc}
|loc_08030B66|
	LDR      r0, [pc, #0x398]
	STR      r0, [r4, #0x60]
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r5, [pc, #0x388]
	LDR      r2, [r0, #0x10]
	ADD      r4, r0, #0
	LDR      r1, [r5]
	LDR      r0, [pc, #0x38c]
	CMP      r2, #0
	LDRH     r1, [r1, #4]
	BEQ      |loc_08030BA4|
	LSL      r3, r1, #0x19
	LSR      r3, r3, #0x1f
	BEQ      |loc_08030B90|
	LDR      r3, [r0]
	SUB      r3, #1
	STR      r3, [r0]
	BPL      |loc_08030B90|
	SUB      r3, r2, #1
	STR      r3, [r0]
|loc_08030B90|
	LSL      r3, r1, #0x18
	LSR      r3, r3, #0x1f
	BEQ      |loc_08030BA4|
	LDR      r3, [r0]
	ADD      r3, #1
	STR      r3, [r0]
	CMP      r2, r3
	BGT      |loc_08030BA4|
	MOV      r2, #0
	STR      r2, [r0]
|loc_08030BA4|
	LSL      r1, r1, #0x1e
	LSR      r1, r1, #0x1f
	LDR      r6, [pc, #0x350]
	LDR      r7, [pc, #0x354]
	BEQ      |sub_08030BCE|
	MOV      r1, #0
	MVN      r1, r1
	STR      r1, [r0]
	LDR      r0, [r4, #0x54]
	CMP      r0, #0
	BEQ      |loc_08030BC2|
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_08030BC2|
	LDR      r0, [r4, #0x5c]
	CMP      r0, #0
	BEQ      |sub_08030BCC|
	STR      r6, [r4, #0x60]
	B        |sub_08030BCE|
|sub_08030BCC|
|unk_08030BCC|
		STR r7, [r4, #0x60]
|sub_08030BCE|
	LDR      r0, [r5]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	BEQ      |loc_08030BF0|
	LDR      r0, [r4, #0x54]
	CMP      r0, #0
	BEQ      |loc_08030BE4|
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_08030BE4|
	LDR      r0, [r4, #0x5c]
	CMP      r0, #0
	BEQ      |loc_08030BEE|
	STR      r6, [r4, #0x60]
	B        |loc_08030BF0|
|loc_08030BEE|
	STR      r7, [r4, #0x60]
|loc_08030BF0|
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
	LDR      r1, [r0, #0x58]
	MOV      r3, #0x10
	ADD      r1, #1
	ADD      r2, r1, #0
	STR      r1, [r0, #0x58]
	LDR      r1, [pc, #0x2f4]
	STRB     r2, [r1, #2]
	LDR      r2, [r0, #0x58]
	SUB      r2, r3, r2
	STRB     r2, [r1, #3]
	LDR      r1, [r0, #0x58]
	CMP      r1, #0x10
	BLT      |loc_08030C12|
	LDR      r1, [pc, #0x2f8]
	STR      r1, [r0, #0x60]
|loc_08030C12|
	MOV      r0, #0
	BX       lr
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	SUB      sp, #0x64
	ADD      r6, r0, #0
	BNE      |Bg_WriteScroll0AndBlendAlpha|
	MOV      r0, #0x64
	BL       |GBARam_Malloc|
	ADD      r6, r0, #0
	BNE      |Bg_WriteScroll0AndBlendAlpha|
	ADD      r0, r6, #0
	ADD      sp, #0x6c
	POP      {r4, r5, r6, r7, pc}
|Bg_WriteScroll0AndBlendAlpha|
|unk_08030C2E|
; cited by 0x08030B2E (a pc-relative load targets 0x08030EF4)
		LDR r0, [pc, #0x2dc]
		ADD r1, r6, #0
		STR r0, [r6]
		LDR r0, [pc, #0x2d8]
		ADD r1, #0xc
		STR r1, [sp, #0x60]
		STR r0, [r6, #0xc]
		LDR r0, [pc, #0x2d4]
		STR r0, [r6]
		ADD r0, #0x2c
		STR r0, [r6, #0xc]
		ADD r2, r1, #4
		STR r2, [sp, #0x5c]
		MOV r0, #0
		STR r0, [r6, #0x10]
		MOV r2, #1
		LSL r2, r2, #0xb
		STR r0, [r6, #0x54]
		LDR r0, [pc, #0x2c4]
		MOV r1, #0
		BL       |sub_0804912C|
		MOV r0, #0
		LDR r4, [pc, #0x2bc]
		STR r0, [sp, #0x48]
		STR r0, [sp, #0x4c]
		LDR r1, [r4, #8]
		LDR r2, [r4]
		LDR r5, [pc, #0x290]
		SUB r1, r1, r2
		ASR r2, r1, #0x1f
		LSR r2, r2, #0x1d
		ADD r1, r2, r1
		ASR r2, r1, #3
		LDR r1, [r4, #0xc]
		LDR r3, [r4, #4]
		STR r2, [sp, #0x50]
		SUB r1, r1, r3
		ASR r3, r1, #0x1f
		LSR r3, r3, #0x1d
		ADD r1, r3, r1
		ASR r1, r1, #3
		STR r1, [sp, #0x54]
		LDR r1, [r5, #0x10]
		ADD r0, sp, #0x48
		LDRH r7, [r1]
		LDR r1, [pc, #0x28c]
		ADD r2, r7, #0
		BL       |inc_0x03d784_0x041118| + 0x28c
		MOV r0, #3
		LSL r0, r0, #0x19
		LSL r1, r7, #6
		ADD r0, r1, r0
		STR r0, [sp, #0x58]
		LDR r1, [r4, #8]
		LDR r2, [r4]
		SUB r1, r1, r2
		LDR r2, [r4, #0xc]
		LDR r3, [r4, #4]
		SUB r2, r2, r3
		MUL r2, r1
		MOV r1, #0
		BL       |sub_0804912C|
		LDR r0, [r4, #8]
		LDR r1, [r4]
		SUB r1, r0, r1
		LDR r0, [r4, #0xc]
		LDR r2, [r4, #4]
		ADD r4, sp, #0x14
		SUB r2, r0, r2
		ADD r0, r4, #0
		BL       |loc_0803F540|
		LDR r0, [r5, #0x14]
		ADD r3, sp, #0
		STR r0, [sp, #0x20]
		MOV r0, #0xe
		STRB r0, [r3, #0x15]
		MOV r0, #2
		STRB r0, [r3, #0x17]
		MOV r0, #1
		STRB r0, [r3, #0x16]
		LDR r0, [pc, #0x248]
		ADD r2, sp, #0x3c
		STR r0, [sp, #0x34]
		LDR r0, [sp, #0x3c]
		LDMIA r2!, {r1, r2}
		SUB r0, #8
		STR r0, [sp, #4]
		SUB r2, #8
		STR r2, [sp, #0x10]
		MOV r0, #0
		STR r0, [sp, #8]
		MOV r2, #0
		STR r1, [sp, #0xc]
		ADD r1, sp, #4
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0x21f0
		LDR r0, [sp, #0x40]
		ADD r2, sp, #0x3c
		LDMIA r2!, {r1, r2}
		MOV r3, #0
		SUB r0, #8
		STR r2, [sp, #0x10]
		MOV r2, #0
		STR r0, [sp, #8]
		STR r1, [sp, #0xc]
		ADD r1, sp, #4
		ADD r0, r4, #0
		STR r3, [sp, #4]
		BL       |inc_0x03d784_0x041118| + 0x21f0
		LDR r0, [sp, #0x3c]
		LDR r2, [sp, #0x40]
		SUB r0, #0xc
		SUB r2, #0xc
		STR r2, [sp, #0x10]
		MOV r1, #4
		SUB r2, #4
		SUB r3, r0, #4
		STR r2, [sp]
		STR r0, [sp, #0xc]
		ADD r0, sp, #0x14
		ADD r2, r1, #0
		STR r1, [sp, #4]
		STR r1, [sp, #8]
		BL       |loc_08004F1C|
		LDR r1, [sp, #0x40]
		LDR r0, [sp, #0x3c]
		MOV r2, #0
		SUB r1, #8
		SUB r0, #8
		STR r0, [sp, #0xc]
		STR r1, [sp, #0x10]
		ADD r1, sp, #4
		ADD r0, r4, #0
		STR r2, [sp, #4]
		STR r2, [sp, #8]
		BL       |loc_08004F50|
		LDR r0, [sp, #0x68]
		MOV r4, #0x14
		STR r0, [sp, #8]
		B        |loc_08030D5A|
|loc_08030D56|
		CMP r1, #0
		BEQ      |loc_08030DBE|
|loc_08030D5A|
		LDR r1, [pc, #0x1c0]
		MOV r7, #8
		LDR r0, [r1, #8]
		LDR r1, [r1]
		SUB r0, r0, r1
		SUB r0, #0x18
		STR r0, [sp]
		LDR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #8
		BNE      |loc_08030D84|
|loc_08030D70|
		LDR r0, [sp, #8]
		ADD r3, sp, #0
		LDRH r0, [r0, #2]
		STRB r0, [r3, #0x17]
		LDR r0, [sp, #8]
		ADD r0, #4
		STR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #8
		BEQ      |loc_08030D70|
|loc_08030D84|
		LDR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #0x2d
		BNE      |loc_08030DBE|
		LDR r0, [sp, #8]
		ADD r0, #2
		STR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #0x20
		BNE      |loc_08030DA4|
|loc_08030D98|
		LDR r0, [sp, #8]
		ADD r0, #2
		STR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #0x20
		BEQ      |loc_08030D98|
|loc_08030DA4|
		LDR r0, [sp]
		LDR r2, [sp, #0x5c]
		SUB r0, #0x10
		STR r0, [sp]
		LDR r0, [r2]
		ADD r7, #0x10
		ADD r1, r0, #1
		LSL r0, r0, #3
		ADD r0, r0, r2
		ADD r0, #4
		STR r1, [r2]
		STR r4, [r0, #4]
		STR r7, [r0]
|loc_08030DBE|
		ADD r5, r7, #0
		ADD r3, sp, #4
		ADD r0, sp, #0x14
		LDR r1, [sp, #8]
		LDR r2, [sp]
		BL       |inc_0x03d784_0x041118| + 0x6e6
		ADD r1, sp, #4
		LDMIA r1!, {r0, r1}
		CMP r0, r1
		BEQ      |loc_08030E26|
|loc_08030DD4|
		LDR r0, [sp, #4]
		LDRH r0, [r0]
		CMP r0, #8
		BNE      |loc_08030DEC|
		LDR r0, [sp, #4]
		ADD r3, sp, #0
		LDRH r0, [r0, #2]
		STRB r0, [r3, #0x17]
		LDR r0, [sp, #4]
		ADD r0, #4
		STR r0, [sp, #4]
		B        |loc_08030E1E|
|loc_08030DEC|
		LDR r0, [sp, #4]
		STR r5, [sp, #0x18]
		STR r4, [sp, #0x1c]
		LDRH r1, [r0]
		ADD r0, sp, #0x14
		BL       |sub_0803DE50|
		LDR r0, [sp, #4]
		LDRH r0, [r0]
		LDR r1, [sp, #0x20]
		CMP r0, #0xff
		BLO      |loc_08030E0A|
		LDR r0, [r1, #4]
		ADD r0, #1
		B        |loc_08030E16|
|loc_08030E0A|
		LDR r1, [r1]
		LSL r0, r0, #1
		LDRH r0, [r1, r0]
		LSL r0, r0, #1
		LDRH r0, [r1, r0]
		ADD r0, #1
|loc_08030E16|
		ADD r5, r0, r5
		LDR r0, [sp, #4]
		ADD r0, #2
		STR r0, [sp, #4]
|loc_08030E1E|
		ADD r1, sp, #4
		LDMIA r1!, {r0, r1}
		CMP r0, r1
		BNE      |loc_08030DD4|
|loc_08030E26|
		LDR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #0xa
		BEQ      |loc_08030E34|
		ADD r4, #0xe
		MOV r1, #0
		B        |loc_08030E44|
|loc_08030E34|
		MOV r1, #1
|loc_08030E36|
		LDR r0, [sp, #8]
		ADD r4, #0xe
		ADD r0, #2
		STR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #0xa
		BEQ      |loc_08030E36|
|loc_08030E44|
		LDR r0, [sp, #8]
		LDRH r0, [r0]
		CMP r0, #0
		BNE      |loc_08030D56|
		LDR r0, [pc, #0xd4]
		LDR r0, [r0]
		CMP r0, #0
		BEQ      |loc_08030E7E|
		MOV r0, #2
		ADD r3, sp, #0
		STRB r0, [r3, #0x14]
		LDR r0, [sp, #0x3c]
		LDR r1, [sp, #0x40]
		SUB r0, #0x10
		STR r0, [sp, #0x18]
		SUB r1, #0x10
		STR r1, [sp, #0x1c]
		LDR r0, [pc, #0x90]
		LDR r1, [pc, #0xbc]
		LDR r0, [r0, #8]
		ADD r0, r0, r1
		LDR r2, [r0]
		MOV r0, #0x99
		LDR r1, [pc, #0xb8]
		LSL r0, r0, #2
		LDR r1, [r1, r0]
		ADD r0, sp, #0x14
		BL       |sub_0803DC96|
|loc_08030E7E|
		LDR r0, [r6, #0x10]
		CMP r0, #0
		BEQ      |loc_08030EA4|
		MOV r0, #0
		LDR r1, [pc, #0x7c]
		CMP r6, #0
		STR r0, [r1]
		BEQ      |loc_08030E90|
		LDR r0, [sp, #0x60]
|loc_08030E90|
		ADD r1, r0, #0
		MOV r0, #0
		BL       |inc_0x153f2_0x1a3f2| + 0x24d6
		ADD r1, r0, #0
		STR r0, [r6, #0x54]
		LDR r0, [pc, #0x58]
		LDR r0, [r0, #4]
		BL       |List_Append|
|loc_08030EA4|
		LDR r4, [pc, #0x74]
		LDR r0, [r4, #8]
		LDR r1, [r4]
		SUB r0, r0, r1
		LDR r1, [r4, #0xc]
		LDR r2, [r4, #4]
		SUB r1, r1, r2
		MUL r0, r1
		LDR r1, [sp, #0x38]
		ADD r3, r0, #0
		ADD r0, r1, #0
		LDR r2, [pc, #0x74]
		BL       |sub_0804918C|
		LDR r0, [r4]
		LDR r1, [r4, #4]
		LDR r2, [pc, #0x6c]
		NEG r0, r0
		STRH r0, [r2]
		NEG r1, r1
		STRH r1, [r2, #2]
		ADD r1, r2, #0
		ADD r1, #0x30
		LDRH r0, [r1, #0x10]
		LSL r0, r0, #0x1a
		BNE      |loc_08030F48|
		LDR r0, [pc, #0x5c]
		MOV r3, #0
		STR r0, [r6, #0x60]
		MOV r0, #1
		STR r0, [r6, #0x5c]
		LDR r0, [pc, #0x58]
		LDR r2, [pc, #0x58]
		STRB r3, [r0]
		MOV r0, #0x10
		STRB r0, [r2]
		LDR r0, [pc, #0x54]
		STR r3, [r6, #0x58]
		STRH r0, [r1, #0x10]
		B        |loc_08030F50|
	INCBIN  baserom.gba_0x30ef4_0x30ef8.extracted
		DCD     0x08759154
	INCBIN  baserom.gba_0x30efc_0x30f04.extracted
		DCD     0x03002A60
	INCBIN  baserom.gba_0x30f08_0x30f0c.extracted
		DCD     0x0804E454
		DCD     0x080496B4
		DCD     0x0804ABD8
		DCD     0x0600E000
		DCD     0x03000F50
		DCD     0x0803F5A5
		DCD     0x03000F4C
		DCD     0x000004F4
		DCD     0x0806BCE8
		DCD     0x0805672C
		DCD     0x04000010
		DCD     0x08030BF5
		DCD     0x04000052
		DCD     0x04000053
		DCD     0x00003E41
|loc_08030F48|
		LDR r0, [pc, #0x9c]
		STR r0, [r6, #0x60]
		MOV r0, #0
		STR r0, [r6, #0x5c]
|loc_08030F50|
		MOV r0, #0x39
		LSL r0, r0, #7
		MOV r1, #1
		LSL r1, r1, #0x1a
		STRH r0, [r1, #8]
		LDR r1, [sp, #0x58]
		ADD r0, sp, #0x14
		BL       |sub_08049150|
		LDR r0, [pc, #0x88]
		MOV r1, #0
		LDR r0, [r0, #0xc]
		BL       |loc_080096AC|
		MOV r1, #0
		ADD r0, sp, #0x14
		BL       |sub_0803F58C|
		ADD r0, r6, #0
		B        |inc_0x301c0_0x311c0| + 0xa6a
|Blend_WriteControlAndAlpha5|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x70]
	ADD      r5, r1, #0
	STR      r0, [r4]
	ADD      r0, #0x2c
	STR      r0, [r4, #0xc]
	LDR      r0, [pc, #0x64]
	MOV      r1, #0
	LDR      r0, [r0, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x953a
	LDR      r0, [r4, #0x5c]
	CMP      r0, #0
	BEQ      |loc_08030FA4|
	MOV      r0, #0x41
	LDR      r1, [pc, #0x58]
	LSL      r0, r0, #6
	STRH     r0, [r1, #0x10]
	MOV      r0, #0x10
	STRB     r0, [r1, #0x12]
	STRB     r0, [r1, #0x13]
|loc_08030FA4|
	LDR      r0, [pc, #0x50]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08030FB2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08030FB2|
	POP      {r3, r4, r5, pc}
|sub_08030FB4|
|unk_08030FB4|
		MOV r0, #0
		BX       lr
|sub_08030FB8|
	PUSH     {r4}
	LDR      r2, [pc, #0x40]
	ADD      r1, #0x10
	LDR      r2, [r2]
	LDR      r3, [pc, #0x3c]
	LSL      r2, r2, #3
	ADD      r1, r2, r1
	ADD      r1, #4
	LDR      r2, [r1]
	LDR      r4, [r3]
	LDR      r1, [r1, #4]
	LDR      r3, [r3, #4]
	SUB      sp, #8
	ADD      r2, r2, r4
	ADD      r1, r1, r3
	STR      r1, [sp, #4]
	ADD      r1, r2, #0
	STR      r2, [sp]
	LDR      r2, [sp, #4]
	STMIA    r0!, {r1, r2}
	ADD      sp, #8
	POP      {r4}
	BX       lr
|loc_08030FE6|
	DCW      0x0000
	DCW      0x0b6d,0x0803,0x9154,0x0875,0xabd8,0x0804,0x0040,0x0400
	DCW      0xe454
|loc_08030FFA|
	LSR      r4, r0, #0x20
	CMP      r2, #0x60
	LSL      r0, r0, #0xc
	LSR      r0, r2, #0x1d
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x240]
	ADD      r5, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x44
	CMP      r1, #0
	BNE      |sub_0803101A|
	MOV      r0, #0
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
|sub_0803101A|
|unk_0803101A|
		MOV r0, #1
		LSL r0, r0, #9
		ADD r2, r5, r0
		LDR r0, [r2, #4]
		ADD r6, r4, #4
		CMP r0, #0
		BEQ      |loc_08031090|
		MOV r3, #0x80
		BIC r0, r3
		LSL r3, r3, #3
		CMP r0, #0
		BEQ      |loc_08031056|
		CMP r0, #1
		BEQ      |loc_0803104E|
		CMP r0, #2
		BEQ      |loc_08031046|
		CMP r0, #3
		BNE      |loc_0803105C|
		LDR r0, [r4, #4]
		ADD r0, r0, r3
		STR r0, [r4, #4]
		B        |loc_0803105C|
|loc_08031046|
		LDR r0, [r4, #4]
		SUB r0, r0, r3
		STR r0, [r4, #4]
		B        |loc_0803105C|
|loc_0803104E|
		LDR r0, [r4, #8]
		SUB r0, r0, r3
		STR r0, [r4, #8]
		B        |loc_0803105C|
|loc_08031056|
		LDR r0, [r4, #8]
		ADD r0, r0, r3
		STR r0, [r4, #8]
|loc_0803105C|
		LDR r3, [r4, #4]
		CMP r3, #0x80
		BLE      |loc_08031068|
		MOV r0, #0x80
		STR r0, [r6]
		B        |loc_0803108C|
|loc_08031068|
		MOV r0, #0x7f
		MVN r0, r0
		ADD r7, r0, #0
		CMP r3, r7
		BGE      |loc_08031076|
		STR r0, [r6]
		B        |loc_0803108C|
|loc_08031076|
		ADD r3, r4, #0
		LDR r7, [r4, #8]
		ADD r3, #8
		CMP r7, #0x80
		BLE      |loc_08031086|
		MOV r0, #0x80
		STR r0, [r3]
		B        |loc_0803108C|
|loc_08031086|
		CMP r7, r0
		BGE      |loc_0803108C|
		STR r0, [r3]
|loc_0803108C|
		MOV r0, #0
		STR r0, [r2, #4]
|loc_08031090|
		ADD r0, sp, #0xc
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		ASR r1, r1, #1
		STR r1, [sp, #4]
		STR r1, [sp, #0x1c]
		STR r0, [sp, #8]
		STR r0, [sp, #0x20]
		ADD r0, sp, #0x24
		ADD r1, r5, #0
		BL       |sub_0800FDFA|
		LDR r0, [sp, #0x24]
		LDR r1, [sp, #0x2c]
		LDR r2, [sp, #0x30]
		ADD r1, r0, r1
		LDR r0, [sp, #0x28]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x38]
		ASR r1, r1, #1
		LDR r0, [sp, #0x1c]
		STR r1, [sp, #4]
		STR r1, [sp, #0x34]
		SUB r1, r0, r1
		LDR r0, [sp, #0x20]
		LDR r2, [sp, #0x38]
		STR r1, [sp, #4]
		STR r1, [sp, #0x3c]
		SUB r0, r0, r2
		LDR r1, [pc, #0x168]
		STR r0, [sp, #8]
		STR r0, [sp, #0x40]
		LDR r0, [r1, #4]
		ADD r7, r1, #0
		CMP r0, #0
		BNE      |loc_080310FE|
		MOV r0, #1
		STR r0, [r1, #4]
		LDR r0, [pc, #0x15c]
		BL       |sub_08054A64|
		STR r0, [r7]
|loc_080310FE|
		LDR r1, [sp, #0x3c]
		CMP r1, #0
		BLE      |loc_08031112|
		LDR r0, [r4, #4]
		CMP r0, #0x80
		BGE      |loc_08031122|
		LDR r1, [r7]
		ADD r0, r0, r1
		STR r0, [r4, #4]
		B        |loc_08031122|
|loc_08031112|
		MOV r1, #0x7f
		LDR r0, [r4, #4]
		MVN r1, r1
		CMP r0, r1
		BLE      |loc_08031122|
		LDR r1, [r7]
		SUB r0, r0, r1
		STR r0, [r4, #4]
|loc_08031122|
		LDR r0, [sp, #0x40]
		CMP r0, #0
		BLE      |loc_08031136|
		LDR r0, [r4, #8]
		CMP r0, #0x80
		BGE      |loc_08031146|
		LDR r1, [r7]
		ADD r0, r0, r1
		STR r0, [r4, #8]
		B        |loc_08031146|
|loc_08031136|
		MOV r1, #0x7f
		LDR r0, [r4, #8]
		MVN r1, r1
		CMP r0, r1
		BLE      |loc_08031146|
		LDR r1, [r7]
		SUB r0, r0, r1
		STR r0, [r4, #8]
|loc_08031146|
		LDR r0, [r4, #4]
		CMP r0, #0
		BLT      |loc_08031150|
		ADD r1, r0, #0
		B        |loc_08031152|
|loc_08031150|
		NEG r1, r0
|loc_08031152|
		LDR r2, [r4, #8]
		CMP r2, #0
		BLT      |loc_0803115C|
		ADD r3, r2, #0
		B        |loc_0803115E|
|loc_0803115C|
		NEG r3, r2
|loc_0803115E|
		CMP r1, r3
		BLE      |loc_08031170|
		CMP r0, #0
		BLE      |loc_0803116A|
		MOV r0, #3
		B        |loc_0803116C|
|loc_0803116A|
		MOV r0, #2
|loc_0803116C|
		STRB r0, [r5, #0x10]
		B        |loc_08031180|
|loc_08031170|
		CMP r2, #0
		BLE      |loc_08031178|
		MOV r0, #1
		B        |loc_0803117A|
|loc_08031178|
		MOV r0, #0
|loc_0803117A|
		MOV r1, #1
		SUB r0, r1, r0
		STRB r0, [r5, #0x10]
|loc_08031180|
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x48]
		ADD r2, r2, r1
		MOV r1, #1
		BL       |loc_08046AA4|
		ADD r4, r5, #0
		ADD r4, #0xff
		ADD r4, #0xa1
		LDR r0, [r4]
		LDR r1, [r6]
		LDR r2, [r4, #4]
		ADD r0, r0, r1
		LDR r1, [r6, #4]
		STR r0, [sp, #0x24]
		ADD r1, r2, r1
		STR r1, [sp, #0x28]
		STR r1, [sp, #0x30]
		STR r1, [sp, #0x38]
		STR r0, [sp, #0x2c]
		STR r0, [sp, #0x34]
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x54]
		ADD r7, r4, #4
		ADD r2, r2, r1
		ADD r1, sp, #0x34
		BL       |loc_08046AA4|
		CMP r0, #0
		DCW     0xD004
