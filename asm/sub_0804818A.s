	CODE16
|sub_0804818A|
	LSL      r0, r0, #0
	LDR      r1, [pc, #4]
	MOV      r0, #0
	STR      r0, [r1]
	BX       lr
|sub_08048194|
|unk_08048194|
	INCBIN	baserom.gba_0x48194_0x48196.extracted
|sub_08048196|
	DCW      0x0300
