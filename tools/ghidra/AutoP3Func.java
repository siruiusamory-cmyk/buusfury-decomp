/* Create functions at addresses if missing, decompile, and list callers. */
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Program;
import ghidra.program.model.symbol.Reference;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class AutoP3Func extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        Path out = Paths.get(args[0]);
        Program program = currentProgram;
        DecompInterface di = new DecompInterface();
        di.openProgram(program);

        try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(out))) {
            for (int i = 1; i < args.length; i++) {
                Address addr = program.getAddressFactory()
                    .getDefaultAddressSpace().getAddress(
                        Long.parseLong(args[i], 16));
                Function f = getFunctionContaining(addr);
                if (f == null) {
                    disassemble(addr);
                    f = createFunction(addr, null);
                }
                w.println("=== PC 0x" + Long.toHexString(addr.getOffset()));
                if (f == null) {
                    w.println("  STILL NO FUNCTION");
                    continue;
                }
                w.println("  func=" + f.getName() + " entry=0x"
                    + Long.toHexString(f.getEntryPoint().getOffset())
                    + " body=" + f.getBody().toString());
                for (Reference r : getReferencesTo(f.getEntryPoint())) {
                    Address from = r.getFromAddress();
                    Function cf = getFunctionContaining(from);
                    w.println("  ref-from=0x" + Long.toHexString(
                        from.getOffset()) + " caller="
                        + (cf == null ? "?" : cf.getName()));
                }
                DecompileResults res = di.decompileFunction(f, 40, monitor);
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
