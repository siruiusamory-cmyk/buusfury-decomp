	CODE16
|sub_0802AB02|
|unk_0802AB02|
		MOV r0, #0
		DCW     0xE7FC
	CODE16
|dat_0802AB06|
	DCW      0x0000
|unk_0802AB08|
	INCBIN	baserom.gba_0x2ab08_0x2ab0a.extracted
	LSR      r4, r0, #0x20
	CMP      r7, #0xe4
	LSL      r0, r0, #0xc
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	LDRH     r0, [r1, #0x12]
	SUB      sp, #0x1c
	ADD      r6, r1, #0
	ADD      r0, #1
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	ADD      r4, r1, #0
	CMP      r0, #8
	STRH     r0, [r1, #0x12]
	BCS      |sub_0802AB3A|
	MOV      r3, #0
	STRB     r3, [r4, #0x11]
|loc_0802AB36|
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}

