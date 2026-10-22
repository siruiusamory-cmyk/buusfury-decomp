	CODE16
|sub_0804F066|
	LSL      r0, r0, #0
	MOV      r0, #0
	BX       lr
|sub_0804F06C|
|unk_0804F06C|
		MOV r0, #1
		BX       lr
		LDR r0, [r0, #0x2c]
		BX       lr
		BX       lr
	INCBIN  baserom.gba_0x4f076_0x4f078.extracted
		BX       lr
