/* ###
 * IP: LOG1-REMAKE
 *
 * List all references to given addresses (globals/tables/functions), with
 * containing-function attribution where available.
 *
 * Args: <output-path> <addr> [addr ...]
 *
 * @category LOG1
 */

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class AutoXrefs extends GhidraScript {

    private static final String EXPECTED_MD5 =
        "3a74fce97f1ea2b28c2a50ec3df0acee";
    private static final String EXPECTED_SHA256 =
        "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e";
    private static final String EXPECTED_LANGUAGE = "ARM:LE:32:v4t";

    @Override
    public void run() throws Exception {
        String md5 = currentProgram.getExecutableMD5();
        String sha256 = currentProgram.getExecutableSHA256();
        String language = currentProgram.getLanguageID().toString();
        if (!EXPECTED_MD5.equalsIgnoreCase(md5) ||
                !EXPECTED_SHA256.equalsIgnoreCase(sha256) ||
                !EXPECTED_LANGUAGE.equals(language)) {
            throw new IllegalStateException(
                "refusing non-canonical program: md5=" + md5 +
                " sha256=" + sha256 + " language=" + language);
        }

        String[] args = getScriptArgs();
        if (args.length < 2) {
            throw new IllegalArgumentException("expected output path and addresses");
        }
        File reportFile = requireIgnoredReportPath(args[0]);

        try (PrintWriter out = new PrintWriter(new OutputStreamWriter(
                new FileOutputStream(reportFile), StandardCharsets.UTF_8))) {
            out.println("AUTO_XREFS");
            out.println("executable_sha256=" + sha256);
            for (int i = 1; i < args.length; i++) {
                long raw = Long.parseLong(args[i].replaceFirst("^0x", ""), 16);
                Address address = currentProgram.getAddressFactory()
                    .getDefaultAddressSpace().getAddress(raw);
                out.println();
                out.println("XREFS_TO " + address);
                ReferenceIterator references =
                    currentProgram.getReferenceManager().getReferencesTo(address);
                List<Reference> found = new ArrayList<>();
                while (references.hasNext()) {
                    found.add(references.next());
                }
                found.sort(Comparator.comparing(Reference::getFromAddress));
                if (found.isEmpty()) {
                    out.println("  NONE");
                }
                for (Reference reference : found) {
                    Function from = currentProgram.getFunctionManager()
                        .getFunctionContaining(reference.getFromAddress());
                    out.printf("  from=%s type=%s source_function=%s%n",
                        reference.getFromAddress(), reference.getReferenceType(),
                        from == null ? "NONE"
                            : from.getEntryPoint() + " " + from.getName());
                }
            }
        }
        println("AutoXrefs written to " + reportFile);
    }

    private File requireIgnoredReportPath(String requestedPath) throws Exception {
        File source = getSourceFile().getFile(false);
        if (source == null || source.getParentFile() == null ||
                source.getParentFile().getParentFile() == null ||
                source.getParentFile().getParentFile().getParentFile() == null) {
            throw new IllegalStateException("cannot resolve repository from script path");
        }
        File repository = source.getParentFile().getParentFile().getParentFile();
        File allowedRoot = new File(repository, "build/ghidra/reports")
            .getCanonicalFile();
        File report = new File(requestedPath).getCanonicalFile();
        if (!report.toPath().startsWith(allowedRoot.toPath())) {
            throw new IllegalArgumentException(
                "report path must be below ignored directory " + allowedRoot);
        }
        return report;
    }
}
