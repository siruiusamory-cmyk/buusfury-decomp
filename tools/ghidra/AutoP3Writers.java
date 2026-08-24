/* Report containing functions + decompilation for writer PC addresses. */
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Program;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class AutoP3Writers extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        Path out = Paths.get(args[0]);
        Program program = currentProgram;
        DecompInterface di = new DecompInterface();
        DecompileOptions opts = new DecompileOptions();
        di.setOptions(opts);
        di.openProgram(program);

        try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(out))) {
            for (int i = 1; i < args.length; i++) {
                Address addr = program.getAddressFactory()
                    .getDefaultAddressSpace().getAddress(
                        Long.parseLong(args[i], 16));
                Function f = getFunctionContaining(addr);
                w.println("=== PC 0x" + Long.toHexString(addr.getOffset()));
                if (f == null) {
                    w.println("  NO CONTAINING FUNCTION");
                    continue;
                }
                w.println("  func=" + f.getName() + " entry=0x"
                    + Long.toHexString(f.getEntryPoint().getOffset())
                    + " body=" + f.getBody().toString());
                DecompileResults res = di.decompileFunction(f, 30, monitor);
                if (res != null && res.decompileCompleted()) {
                    w.println(res.getDecompiledFunction().getC());
                } else {
                    w.println("  <decompile failed>");
                }
            }
        }
        di.dispose();
    }
}
