
import React from 'react';
import { Search, ChevronDown, Layers } from 'lucide-react';

const ControlsToolbar = ({
    filters,
    updateFilter,
    grouping,
    setGrouping,
    availableGroups,
    framework
}) => {
    return (
        <div className="bg-white border text-sm border-gray-200 rounded-xl p-3 shadow-sm mb-6 flex flex-col lg:flex-row gap-4 justify-between items-center sticky top-24 z-10">

            {/* AREA A: FILTERS */}
            <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto flex-1">
                {/* Search */}
                <div className="relative flex-1 min-w-[200px]">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                        type="text"
                        placeholder="Search controls (ID, Title, Desc)..."
                        className="pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm w-full focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        value={filters.search}
                        onChange={(e) => updateFilter('search', e.target.value)}
                    />
                </div>

                {/* Status Filter */}
                <div className="relative min-w-[140px]">
                    <select
                        value={filters.status}
                        onChange={(e) => updateFilter('status', e.target.value)}
                        className={`w-full appearance-none pl-3 pr-8 py-2 font-medium border rounded-lg cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${filters.status !== 'All'
                            ? 'bg-blue-50 text-blue-700 border-blue-200'
                            : 'bg-white text-gray-700 border-gray-200 hover:border-gray-300'
                            }`}
                    >
                        <option value="All">Status: All</option>
                        <option value="Implemented">Implemented</option>
                        <option value="Pending">Pending</option>
                    </select>
                    <ChevronDown className={`w-3 h-3 absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none ${filters.status !== 'All' ? 'text-blue-500' : 'text-gray-400'}`} />
                </div>

                {/* Owner Filter (Placeholder) */}
                <div className="relative min-w-[120px]">
                    <select
                        value={filters.owner}
                        onChange={(e) => updateFilter('owner', e.target.value)}
                        className="w-full appearance-none pl-3 pr-8 py-2 font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:border-gray-300 cursor-pointer focus:outline-none"
                    >
                        <option value="All">Owner: All</option>
                        <option value="IT">Owner: IT</option>
                        <option value="HR">Owner: HR</option>
                        <option value="Legal">Owner: Legal</option>
                    </select>
                    <ChevronDown className="w-3 h-3 text-gray-400 absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
                </div>
            </div>

            <div className="h-px w-full lg:w-px lg:h-8 bg-gray-200"></div>

            {/* AREA B: ORGANIZATION */}
            <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">

                {/* Jump to Section */}
                <div className="relative min-w-[180px]">
                    <select
                        onChange={(e) => {
                            if (e.target.value) {
                                const element = document.getElementById(`section-${e.target.value}`);
                                if (element) {
                                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                    // Reset select after jump
                                    e.target.value = "";
                                }
                            }
                        }}
                        className="w-full appearance-none pl-3 pr-8 py-2 font-bold text-gray-700 bg-gray-50 border border-gray-200 rounded-lg hover:bg-white transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-gray-200"
                    >
                        <option value="">Jump to Section...</option>
                        {availableGroups.map(group => (
                            <option key={group} value={group}>{group}</option>
                        ))}
                    </select>
                    <Layers className="w-3 h-3 text-gray-500 absolute right-8 top-1/2 transform -translate-y-1/2 pointer-events-none" />
                    <ChevronDown className="w-3 h-3 text-gray-400 absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
                </div>

                {/* Group By Toggle */}
                <div className="relative min-w-[160px]">
                    <select
                        value={grouping.groupBy}
                        onChange={(e) => setGrouping(prev => ({ ...prev, groupBy: e.target.value }))}
                        className="w-full appearance-none pl-3 pr-8 py-2 font-bold text-blue-700 bg-blue-50 border border-blue-100 rounded-lg hover:bg-blue-100 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-200"
                    >
                        <option value="section">
                            {framework?.code?.includes('SOC2') ? 'Group: COSO Principles' : 'Group: Domain'}
                        </option>
                        <option value="framework">
                            {framework?.code?.includes('SOC2') ? 'Group: Category' : 'Group: ISO Theme'}
                        </option>
                    </select>
                    <ChevronDown className="w-3 h-3 text-blue-500 absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
                </div>
            </div>
        </div>
    );
};

export default ControlsToolbar;
