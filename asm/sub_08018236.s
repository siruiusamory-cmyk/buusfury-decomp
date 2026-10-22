	CODE16
|sub_08018236|
|unk_08018236|
; cited by 0x08017E9E (a pc-relative load targets 0x08018260)
		LDR r0, [pc, #0x30]
		LDR r0, [r0, #0xc]
		LDR r1, [sp, #0x2c]
		ADD r0, #0x18
		LDR r2, [r0, #8]
		CMP r1, r2
		BGE      |loc_08018280|
		LDR r1, [r0]
		LDR r2, [sp, #0x34]
		CMP r1, r2
		BGE      |loc_08018280|
		LDR r1, [sp, #0x30]
		LDR r2, [r0, #0xc]
		CMP r1, r2
		BGE      |loc_08018280|
		LDR r0, [r0, #4]
		LDR r1, [sp, #0x38]
		CMP r0, r1
		BGE      |loc_08018280|
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x2e40
		DCD     0x0804E444
		DCD     0x0804A0C0
		DCD     0x086FC23C
		DCD     0x000004F4
		DCD     0x083192A8
		DCD     0x000005C4
		DCD     0x08049CC4
		DCD     0x03000F90
