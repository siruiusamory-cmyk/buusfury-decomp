	CODE16
|sub_08011070|
|unk_08011070|
; cited by 0x0042EDF6 (a pool word names 0x080110A8)
		LDRB r0, [r5]
		CMP r0, #1
		BEQ      |loc_0801107A|
		CMP r0, #2
		BNE      |loc_080110CA|
|loc_0801107A|
		ADD r6, r5, #4
		ADD r1, r4, #0
		MOV r0, sp
		BL       |loc_0800FE78|
		LDR r0, [r6]
		LDR r1, [sp, #8]
		CMP r0, r1
		BGE      |loc_080110CA|
		LDR r0, [sp]
		LDR r1, [r6, #8]
		CMP r0, r1
		BGE      |loc_080110CA|
		LDR r0, [r6, #4]
		LDR r1, [sp, #0xc]
		CMP r0, r1
		BGE      |loc_080110CA|
		LDR r0, [sp, #4]
		LDR r1, [r6, #0xc]
		CMP r0, r1
		BGE      |loc_080110CA|
		MOV r0, #0xff
		ADD r0, #0xcd
		LDR r0, [r0, r4]
		CMP r0, #0
		BEQ      |loc_080110CA|
		ADD r5, #0x14
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |sub_0800E9D8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x58]
		ADD r2, r2, r1
		ADD r1, r5, #0
		BL       |loc_08046AA4|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x10f14
|loc_080110CA|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x10f14
|loc_080110CE|
|unk_080110CE|
		ADD r0, r4, #0
	INCBIN  baserom.gba_0x110d0_0x110d2.extracted
|sub_080110D2|
|unk_080110D2|
	INCBIN	baserom.gba_0x110d2_0x110d6.extracted
	LSL      r0, r0, #0
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r7, r2, #0
	ADD      r6, r3, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	LDR      r5, [sp, #0x28]
	BNE      |sub_080110FA|
	MOV      r0, #0xff
	ADD      r0, #0xbd
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_080110FA|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
