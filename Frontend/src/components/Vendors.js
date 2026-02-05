import React, { useState } from 'react';
import {
    BuildingOffice2Icon,
    ShieldCheckIcon,
    ExclamationTriangleIcon,
    DocumentPlusIcon,
    PlusIcon,
    EllipsisVerticalIcon
} from '@heroicons/react/24/outline';

const MOCK_VENDORS = [
    {
        id: 1,
        name: "AWS (Amazon Web Services)",
        category: "Cloud Infrastructure",
        risk: "Critical",
        dataAccess: ["PII", "Customer Data", "Production code"],
        security: { soc2: true, dpa: true, iso27001: true },
        nextReview: "2024-12-01"
    },
    {
        id: 2,
        name: "GitHub",
        category: "Software Development",
        risk: "High",
        dataAccess: ["Source Code"],
        security: { soc2: true, dpa: true, iso27001: false },
        nextReview: "2024-11-15"
    },
    {
        id: 3,
        name: "Slack",
        category: "Communication",
        risk: "Medium",
        dataAccess: ["Internal Comms"],
        security: { soc2: true, dpa: true, iso27001: true },
        nextReview: "2024-10-30"
    },
    {
        id: 4,
        name: "Gusto",
        category: "HR & Payroll",
        risk: "High",
        dataAccess: ["PII", "Financials"],
        security: { soc2: true, dpa: true, iso27001: false },
        nextReview: "2024-09-01"
    },
    {
        id: 5,
        name: "Bob's Catering",
        category: "Office Services",
        risk: "Low",
        dataAccess: [],
        security: { soc2: false, dpa: false, iso27001: false },
        nextReview: "2025-01-01"
    },
];

const RiskBadge = ({ level }) => {
    let color = 'bg-gray-100 text-gray-800';
    if (level === 'Critical') color = 'bg-red-100 text-red-800 border-red-200';
    if (level === 'High') color = 'bg-orange-100 text-orange-800 border-orange-200';
    if (level === 'Medium') color = 'bg-yellow-100 text-yellow-800 border-yellow-200';
    if (level === 'Low') color = 'bg-green-100 text-green-800 border-green-200';

    return (
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${color} uppercase`}>
            {level}
        </span>
    );
};

const Vendors = () => {
    const [vendors, setVendors] = useState(MOCK_VENDORS);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Vendor Risk Management</h1>
                    <p className="text-sm text-gray-500">Track third-party vendors, security reports, and data access.</p>
                </div>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 shadow-sm flex items-center gap-2">
                    <PlusIcon className="w-5 h-5" />
                    New Vendor
                </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                    <div className="text-gray-500 text-xs font-bold uppercase tracking-wide">Total Vendors</div>
                    <div className="text-2xl font-bold text-gray-900 mt-1">{vendors.length}</div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                    <div className="text-red-500 text-xs font-bold uppercase tracking-wide">Critical Risk</div>
                    <div className="text-2xl font-bold text-gray-900 mt-1">{vendors.filter(v => v.risk === 'Critical').length}</div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                    <div className="text-orange-500 text-xs font-bold uppercase tracking-wide">Missing Reports</div>
                    <div className="text-2xl font-bold text-gray-900 mt-1">1</div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                    <div className="text-blue-500 text-xs font-bold uppercase tracking-wide">Upcoming Reviews</div>
                    <div className="text-2xl font-bold text-gray-900 mt-1">2</div>
                </div>
            </div>

            {/* Vendors Grid */}
            <div className="grid grid-cols-1 gap-4">
                {vendors.map(vendor => (
                    <div key={vendor.id} className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">

                        {/* Vendor Info */}
                        <div className="flex items-start gap-4 flex-1">
                            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-gray-500">
                                <BuildingOffice2Icon className="w-6 h-6" />
                            </div>
                            <div>
                                <div className="flex items-center gap-3">
                                    <h3 className="text-lg font-bold text-gray-900">{vendor.name}</h3>
                                    <RiskBadge level={vendor.risk} />
                                </div>
                                <p className="text-sm text-gray-500 mt-1">{vendor.category}</p>

                                <div className="flex flex-wrap gap-2 mt-3">
                                    {vendor.dataAccess.map(d => (
                                        <span key={d} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                                            {d}
                                        </span>
                                    ))}
                                    {vendor.dataAccess.length === 0 && (
                                        <span className="text-xs text-gray-400 italic">No sensitive data access</span>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Security Reports */}
                        <div className="flex flex-col gap-2 min-w-[200px]">
                            <div className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Security Reports</div>
                            <div className="flex items-center gap-4">
                                <div className={`flex items-center gap-1.5 text-sm ${vendor.security.soc2 ? 'text-green-700' : 'text-gray-400'}`}>
                                    {vendor.security.soc2 ? <ShieldCheckIcon className="w-5 h-5" /> : <ExclamationTriangleIcon className="w-5 h-5" />}
                                    <span className="font-medium">SOC 2</span>
                                </div>
                                <div className={`flex items-center gap-1.5 text-sm ${vendor.security.dpa ? 'text-green-700' : 'text-gray-400'}`}>
                                    {vendor.security.dpa ? <ShieldCheckIcon className="w-5 h-5" /> : <ExclamationTriangleIcon className="w-5 h-5" />}
                                    <span className="font-medium">DPA</span>
                                </div>
                            </div>
                        </div>

                        {/* Review Date */}
                        <div className="flex flex-col gap-1 min-w-[150px]">
                            <div className="text-xs font-bold text-gray-400 uppercase tracking-wide">Next Review</div>
                            <div className="text-sm font-medium text-gray-700">{vendor.nextReview}</div>
                        </div>

                        {/* Actions */}
                        <div>
                            <button className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100">
                                <EllipsisVerticalIcon className="w-6 h-6" />
                            </button>
                        </div>

                    </div>
                ))}
            </div>
        </div>
    );
};

export default Vendors;
