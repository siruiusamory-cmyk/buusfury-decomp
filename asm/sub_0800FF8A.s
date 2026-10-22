	CODE16
|sub_0800FF8A|
|unk_0800FF8A|
		MOV r1, #0xff
		ADD r1, #0xa5
		LDR r1, [r1, r4]
		LDR r0, [sp, #8]
		ASR r1, r1, #8
		B        |loc_0800FF84|
|loc_0800FF96|
|unk_0800FF96|
		ADD r1, sp, #8
		LDMIA r1!, {r0, r1}
		B        |loc_0800FF84|
|loc_0800FF9C|
|unk_0800FF9C|
		LDR r0, [sp, #0x10]
		LDR r1, [sp, #0xc]
		B        |loc_0800FF84|
