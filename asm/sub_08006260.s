	CODE16
|sub_08006260|
|unk_08006260|
; cited by 0x080060DA (a pc-relative load targets 0x0800627C)
		LDR r0, [pc, #0x24]
		LDR r1, [r4, #0x1c]
		LDR r0, [r0, #8]
		BL       |sub_0803FFE8|
		LDR r1, [r4, #0x20]
		ASR r0, r0, #1
		SUB r0, r1, r0
		STR r0, [r5]
		LDR r0, [r4, #0x24]
		SUB r0, #3
		STR r0, [r5, #4]
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x6106
		DCD     0x0804B2DC
		DCD     0x0806BCE8
		DCD     0x0803F5A5
		DCD     0x08070140
	INCBIN  baserom.gba_0x628c_0x628e.extracted
|sub_0800628E|
	DCW      0x0803
