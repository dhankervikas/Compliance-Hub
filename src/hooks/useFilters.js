
import { useState } from 'react';

const useFilters = (initialFilters = {}) => {
    const [filters, setFilters] = useState({
        search: initialFilters.search || '',
        status: initialFilters.status || 'All',
        owner: initialFilters.owner || 'All'
    });

    const updateFilter = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const applyFilters = (controls) => {
        return controls.filter(c => {
            // 1. Search Filter
            const searchLower = filters.search.toLowerCase();
            const matchesSearch = !filters.search ||
                (c.title && c.title.toLowerCase().includes(searchLower)) ||
                (c.control_id && c.control_id.toLowerCase().includes(searchLower)) ||
                (c.description && c.description.toLowerCase().includes(searchLower));

            // 2. Status Filter
            let matchesStatus = true;
            if (filters.status === 'Implemented') {
                matchesStatus = c.status === 'IMPLEMENTED';
            } else if (filters.status === 'Pending') {
                matchesStatus = c.status !== 'IMPLEMENTED';
            }

            // 3. Owner Filter (Mocked for now as data might be sparse)
            const matchesOwner = filters.owner === 'All' || c.owner === filters.owner;

            return matchesSearch && matchesStatus && matchesOwner;
        });
    };

    return {
        filters,
        setFilters, // Expose full setter if needed
        updateFilter,
        applyFilters
    };
};

export default useFilters;
