	CODE16
|sub_08008A36|
	PUSH     {lr}
	ADD      r1, r0, #0
	LDR      r0, [r0, #0xc]
	SUB      sp, #0x6c
	LSR      r2, r0, #0x10
	BEQ      |loc_08008A54|
	MOV      r0, #0
	LDR      r1, [r1, #0xc]
	STR      r0, [sp]
	STR      r0, [sp, #0x44]
	MOV      r0, sp
	MOV      r2, #0
	BL       |loc_08004038|
	LDR      r0, [sp, #4]
|loc_08008A54|
	ADD      sp, #0x6c
	POP      {pc}
|sub_08008A58|
|unk_08008A58|
; cited by 0x08008A0A (a pc-relative load targets 0x08008A58)
	INCBIN	baserom.gba_0x8a58_0x8aa0.extracted
