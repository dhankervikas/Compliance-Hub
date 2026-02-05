import React, { useState, useEffect } from 'react';
import processService from '../services/processService';
import {
    BuildingOfficeIcon,
    ChevronDownIcon,
    ChevronUpIcon,
    ShieldCheckIcon
} from '@heroicons/react/24/outline';

const ProcessList = () => {
    const [processes, setProcesses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedProcess, setExpandedProcess] = useState(null);

    useEffect(() => {
        fetchProcesses();
    }, []);

    const fetchProcesses = async () => {
        try {
            const data = await processService.getAll();
            setProcesses(data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setError('Failed to load processes');
            setLoading(false);
        }
    };

    const toggleExpand = (id) => {
        setExpandedProcess(expandedProcess === id ? null : id);
    };

    if (loading) return <div className='p-8 text-center text-gray-500'>Loading processes...</div>;
    if (error) return <div className='p-8 text-center text-red-500'>{error}</div>;

    return (
        <div className='container mx-auto px-4 py-8'>
            <h1 className='text-2xl font-bold mb-6 text-gray-900'>Organizational Processes ({processes.length})</h1>
            <div className='grid grid-cols-1 gap-6 pb-20'>
                {processes.map((proc) => {
                    const stats = proc.stats || { total: 0, implemented: 0, in_progress: 0, not_started: 0 };
                    const implPct = stats.total ? (stats.implemented / stats.total) * 100 : 0;
                    const progPct = stats.total ? (stats.in_progress / stats.total) * 100 : 0;
                    // Remaining is not started

                    return (
                        <div key={proc.id} className='bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden'>
                            <div
                                className='p-6 cursor-pointer hover:bg-gray-50 transition-colors'
                                onClick={() => toggleExpand(proc.id)}
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <div className='flex items-center gap-4'>
                                        <div className='p-3 bg-blue-100 rounded-lg'>
                                            <BuildingOfficeIcon className='w-6 h-6 text-blue-600' />
                                        </div>
                                        <div>
                                            <h3 className='text-lg font-semibold text-gray-900'>{proc.name}</h3>
                                            <p className='text-sm text-gray-500'>{proc.description || 'No description provided.'}</p>
                                        </div>
                                    </div>
                                    <div className='flex items-center gap-4'>
                                        {expandedProcess === proc.id ? (
                                            <ChevronUpIcon className='w-5 h-5 text-gray-400' />
                                        ) : (
                                            <ChevronDownIcon className='w-5 h-5 text-gray-400' />
                                        )}
                                    </div>
                                </div>

                                {/* Status Bar (Chart) */}
                                <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden flex">
                                    <div style={{ width: `${implPct}%` }} className="h-full bg-green-500" title={`Implemented: ${stats.implemented}`} />
                                    <div style={{ width: `${progPct}%` }} className="h-full bg-yellow-400" title={`In Progress: ${stats.in_progress}`} />
                                </div>
                                <div className="flex justify-between text-xs text-gray-500 mt-2">
                                    <span>Coverage: {Math.round(implPct)}% Implemented</span>
                                    <span>Total Controls: {stats.total}</span>
                                </div>
                            </div>

                            {expandedProcess === proc.id && (
                                <div className='border-t border-gray-100 bg-gray-50 p-6'>
                                    <h4 className='text-sm font-medium text-gray-500 uppercase tracking-wider mb-4'>Sub-processes & Linked Controls</h4>
                                    <div className='grid grid-cols-1 gap-4'>
                                        {proc.sub_processes.map((sub) => (
                                            <div key={sub.id} className='bg-white p-5 rounded-lg border border-gray-200'>
                                                <div className='flex items-start justify-between mb-3'>
                                                    <div>
                                                        <h5 className='font-medium text-gray-900 text-lg'>{sub.name}</h5>
                                                        <p className='text-sm text-gray-500'>{sub.description}</p>
                                                    </div>
                                                </div>

                                                {/* Controls List */}
                                                <div className="mt-4 bg-gray-50 rounded border border-gray-100 p-3">
                                                    <h6 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Covered Controls</h6>
                                                    {sub.controls && sub.controls.length > 0 ? (
                                                        <div className="space-y-2">
                                                            {sub.controls.map(c => (
                                                                <div key={c.id} className="flex justify-between items-center text-sm bg-white p-2 rounded shadow-sm border border-gray-100">
                                                                    <div className="flex items-center gap-2">
                                                                        <span className="font-mono font-medium text-blue-600">{c.control_id}</span>
                                                                        <span className="text-gray-700 truncate max-w-md" title={c.title}>{c.title}</span>
                                                                    </div>
                                                                    <div className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${c.status === 'implemented' ? 'bg-green-100 text-green-700' :
                                                                            c.status === 'in_progress' ? 'bg-yellow-100 text-yellow-700' :
                                                                                'bg-gray-100 text-gray-600'
                                                                        }`}>
                                                                        {c.status.replace('_', ' ')}
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    ) : (
                                                        <p className="text-sm text-gray-400 italic">No controls mapped yet.</p>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
export default ProcessList;
