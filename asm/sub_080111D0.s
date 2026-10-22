	CODE16
|sub_080111D0|
|unk_080111D0|
; cited by 0x08011100 (a pc-relative load targets 0x080111F4)
		LDR r2, [sp, #8]
		ADD r3, r5, #0
		ADD r1, r6, #0
		STR r2, [sp]
		LDR r2, [pc, #0x18]
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0xfc1c
		LDR r0, [pc, #0x14]
		ADD r1, r7, #0
		STR r0, [r4]
		ADD r0, r4, #0
		ADD r0, #0xff
		ADD r0, #0xb1
		BL       |inc_0x0158_0x143f2| + 0xa7e4
		ADD r0, r4, #0
		B        |inc_0x0158_0x143f2| + 0x11074
		DCD     0x03001B0C
		DCD     0x0804CEF4
		DCD     0x080727C0
