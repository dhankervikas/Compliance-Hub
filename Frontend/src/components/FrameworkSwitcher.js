import { List, Globe } from 'lucide-react';

const FrameworkSwitcher = ({ viewMode, setViewMode, frameworkCode }) => {
    return (
        <div className="bg-white border rounded-lg p-1 flex gap-1 mb-4">
            <button
                onClick={() => setViewMode('intent')}
                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${viewMode === 'intent'
                    ? 'bg-blue-50 text-blue-700 border border-blue-200 shadow-sm'
                    : 'text-gray-600 hover:bg-gray-50'
                    }`}
            >
                <Globe className="w-4 h-4" />
                <span>
                    {frameworkCode && frameworkCode.includes("SOC2")
                        ? "COSO Principles"
                        : frameworkCode && (frameworkCode.includes("ISO42001") || frameworkCode.includes("NIST"))
                            ? "Business View"
                            : "Business View (Universal)"}
                </span>
            </button>

            <button
                onClick={() => setViewMode('standard')}
                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${viewMode === 'standard'
                    ? 'bg-blue-50 text-blue-700 border border-blue-200 shadow-sm'
                    : 'text-gray-600 hover:bg-gray-50'
                    }`}
            >
                <List className="w-4 h-4" />
                <span>Standard View ({frameworkCode})</span>
            </button>
        </div>
    );
};

export default FrameworkSwitcher;
