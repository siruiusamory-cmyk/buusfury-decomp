	CODE16
|sub_0803C7FE|
	PUSH     {r4, lr}
	LDRB     r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803C812|
	LDR      r1, [pc, #0x18]
	STR      r1, [r0]
	STRB     r4, [r0, #4]
|loc_0803C812|
	POP      {r4, pc}
|sub_0803C814|
|unk_0803C814|
	INCBIN	baserom.gba_0x3c814_0x3c816.extracted
