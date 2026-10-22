	CODE16
|sub_0800AE64|
	LDR      r1, [r0, #0x50]
	SUB      r1, #1
	STR      r1, [r0, #0x50]
	BNE      |sub_0800AE70|
	MOV      r0, #1
	BX       lr
