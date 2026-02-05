// src/components/Controls.js
import React, { useState, useEffect } from 'react';
import { Search, Filter, CheckCircle, Clock, Circle, ChevronDown, ChevronUp } from 'lucide-react';
import ControlMappings from './ControlMappings';
import { controlsAPI, frameworksAPI } from '../services/api';

const Controls = () => {
  const [controls, setControls] = useState([]);
  const [frameworks, setFrameworks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFramework, setSelectedFramework] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [expandedControl, setExpandedControl] = useState(null);

  // Fetch data on component mount
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [controlsData, frameworksData] = await Promise.all([
        controlsAPI.getAll(),
        frameworksAPI.getAll(),
      ]);

     // Sort controls: ISMS clauses first, then Annex A in natural order
      const sortedControls = controlsData.sort((a, b) => {
        // ISMS controls first (clauses 4.1, 5.1, etc.)
        const aIsISMS = a.framework_name && a.framework_name.includes('ISMS');
        const bIsISMS = b.framework_name && b.framework_name.includes('ISMS');
        
        if (aIsISMS && !bIsISMS) return -1;
        if (!aIsISMS && bIsISMS) return 1;
        
        // Natural sort by control_id (A.5.3 before A.5.4, not A.5.10 before A.5.4)
        return a.control_id.localeCompare(b.control_id, undefined, { numeric: true });
      });
      
      setControls(sortedControls);
      setFrameworks(frameworksData);
    } catch (err) {
      console.error('Error fetching controls:', err);
      setError('Failed to load controls');
    } finally {
      setLoading(false);
    }
  };

  // Filter controls based on search and filters
  const filteredControls = controls.filter((control) => {
    const matchesSearch =
      searchQuery === '' ||
      control.control_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      control.title.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesFramework =
      selectedFramework === 'all' ||
      control.framework_id === parseInt(selectedFramework);

    const matchesStatus =
      selectedStatus === 'all' || control.status === selectedStatus;

    return matchesSearch && matchesFramework && matchesStatus;
  });

  // Get status badge component
  const StatusBadge = ({ status }) => {
    const configs = {
      implemented: {
        icon: CheckCircle,
        bg: 'bg-green-100',
        text: 'text-green-700',
        label: 'Implemented',
      },
      in_progress: {
        icon: Clock,
        bg: 'bg-yellow-100',
        text: 'text-yellow-700',
        label: 'In Progress',
      },
      not_started: {
        icon: Circle,
        bg: 'bg-gray-100',
        text: 'text-gray-700',
        label: 'Not Started',
      },
    };

    const config = configs[status] || configs.not_started;
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text}`}>
        <Icon className="w-4 h-4" />
        {config.label}
      </span>
    );
  };

  // Update control status
  const handleStatusUpdate = async (controlId, newStatus) => {
    try {
      await controlsAPI.update(controlId, { status: newStatus });
      
      // Update local state
      setControls(controls.map(c => 
        c.id === controlId ? { ...c, status: newStatus } : c
      ));
      
      alert('Control status updated successfully!');
    } catch (err) {
      console.error('Error updating control:', err);
      alert('Failed to update control status');
    }
  };

  // Toggle control expansion
  const toggleControl = (controlId) => {
    setExpandedControl(expandedControl === controlId ? null : controlId);
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading controls...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Controls Management</h1>
        <p className="text-gray-600 mt-1">View and manage all compliance controls</p>
      </div>

      {/* Filters Section */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Controls
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by ID or title..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Framework Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Framework
            </label>
            <select
              value={selectedFramework}
              onChange={(e) => setSelectedFramework(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Frameworks</option>
              {frameworks.map((fw) => (
                <option key={fw.id} value={fw.id}>
                  {fw.name}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Statuses</option>
              <option value="implemented">Implemented</option>
              <option value="in_progress">In Progress</option>
              <option value="not_started">Not Started</option>
            </select>
          </div>
        </div>

        {/* Results Count */}
        <div className="mt-4 text-sm text-gray-600">
          Showing {filteredControls.length} of {controls.length} controls
        </div>
      </div>

      {/* Controls List */}
      <div className="space-y-3">
        {filteredControls.map((control) => (
          <div key={control.id} className="bg-white rounded-lg shadow">
            {/* Control Header - Clickable */}
            <div
              onClick={() => toggleControl(control.id)}
              className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-sm font-semibold text-blue-600">
                      {control.control_id}
                    </span>
                    <StatusBadge status={control.status} />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mt-2">
                    {control.title}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {control.framework_name}
                  </p>
                </div>
                <div className="ml-4">
                  {expandedControl === control.id ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </div>
            </div>

            {/* Expanded Details */}
            {expandedControl === control.id && (
              <div className="border-t border-gray-200 p-4 bg-gray-50">
                <div className="space-y-4">
                  {/* Description */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Description</h4>
                    <p className="text-sm text-gray-600">
                      {control.description || 'No description available'}
                    </p>
                  </div>

                  {/* Implementation Guide */}
                  {control.implementation_guide && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-2">
                        Implementation Guide
                      </h4>
                      <p className="text-sm text-gray-600">{control.implementation_guide}</p>
                    </div>
                  )}

{/* Control Mappings */}
<ControlMappings controlId={control.id} />

                  {/* Status Update Buttons */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Update Status</h4>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleStatusUpdate(control.id, 'not_started')}
                        disabled={control.status === 'not_started'}
                        className="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Not Started
                      </button>
                      <button
                        onClick={() => handleStatusUpdate(control.id, 'in_progress')}
                        disabled={control.status === 'in_progress'}
                        className="px-4 py-2 text-sm bg-yellow-200 text-yellow-700 rounded hover:bg-yellow-300 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        In Progress
                      </button>
                      <button
                        onClick={() => handleStatusUpdate(control.id, 'implemented')}
                        disabled={control.status === 'implemented'}
                        className="px-4 py-2 text-sm bg-green-200 text-green-700 rounded hover:bg-green-300 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Implemented
                      </button>
                    </div>
                  </div>

                  {/* Additional Info */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Owner: </span>
                      <span className="font-medium">{control.owner || 'Unassigned'}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Evidence Count: </span>
                      <span className="font-medium">{control.evidence_count || 0}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* No Results */}
        {filteredControls.length === 0 && (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <Filter className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No controls found matching your filters</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Controls;