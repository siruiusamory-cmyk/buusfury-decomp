	CODE16
|sub_0800A624|
	LDR      r2, [r0, #0x48]
	LDR      r3, [r0, #0x38]
	CMP      r2, r3
	BGT      |loc_0800A644|
	LDR      r2, [r0, #0x4c]
	LDR      r3, [r0, #0x3c]
	CMP      r2, r3
	BGT      |loc_0800A644|
	LDR      r2, [r0, #0x50]
	LDR      r3, [r0, #0x40]
	CMP      r2, r3
	BLT      |loc_0800A644|
	LDR      r2, [r0, #0x54]
	LDR      r3, [r0, #0x44]
	CMP      r2, r3
	BGE      |sub_0800A648|
|loc_0800A644|
	MOV      r0, #0
	BX       lr
