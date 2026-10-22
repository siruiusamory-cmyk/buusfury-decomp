	CODE16
|sub_0804F944|
	ADD      r2, r0, #0
	ADD      r0, r1, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	SUB      sp, #8
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	STR      r1, [sp]
	LDR      r1, [sp, #4]
	STMIA    r2!, {r0, r1}
	ADD      sp, #8
	BX       lr
|sub_0804F964|
|unk_0804F964|
		MOV r0, #0
		BX       lr
