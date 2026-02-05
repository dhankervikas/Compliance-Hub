
const BabelParser = require('@babel/parser');

// Simulate the prefix context we believe exists
const prefix = `
function FrameworkDetail() {
  return (
    <>
      <div className="min-h-screen">
        {/* Assume previous content closed */}
        
        {/* CONTROL DRAWER context match */}
        {
            selectedControl && (
                <div className="fixed">
                    <div className="absolute"></div>
                    <div className="relative">
                        <div className="p-8">
`;

// The tail we are appending
const tail = `
                                            <div className="text-center py-12 text-gray-400">
                                                <p>Section Content Reset for Recovery</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )
                        }
                </div>
            </>
        );
};
`;

const code = prefix + tail;

try {
    BabelParser.parse(code, {
        sourceType: "module",
        plugins: ["jsx"]
    });
    console.log("Parse SUCCESS! Structure is valid.");
} catch (e) {
    console.log("Parse FAILED:", e.message);
    if (e.loc) console.log(`Location: Line ${e.loc.line}, Column ${e.loc.column}`);
}
