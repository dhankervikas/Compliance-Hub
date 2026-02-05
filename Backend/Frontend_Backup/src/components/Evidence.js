// src/components/Evidence.js
import React, { useState, useEffect } from 'react';
import { Upload, FileText, Download, Trash2, Link as LinkIcon, Search, Filter } from 'lucide-react';
import { evidenceAPI, controlsAPI } from '../services/api';

const Evidence = () => {
  const [evidence, setEvidence] = useState([]);
  const [controls, setControls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  
  // Upload form state
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedControlId, setSelectedControlId] = useState('');
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  
  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedControl, setSelectedControl] = useState('all');

  // Fetch data on mount
  useEffect(() => {
    fetchData();
  }, []);

 const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [evidenceData, controlsData] = await Promise.all([
        evidenceAPI.getAll(),
        controlsAPI.getAll(),
      ]);

      // Sort controls: ISMS clauses first, then Annex A in natural order
      const sortedControls = controlsData.sort((a, b) => {
        const aIsISMS = a.framework_name && a.framework_name.includes('ISMS');
        const bIsISMS = b.framework_name && b.framework_name.includes('ISMS');
        
        if (aIsISMS && !bIsISMS) return -1;
        if (!aIsISMS && bIsISMS) return 1;
        
        return a.control_id.localeCompare(b.control_id, undefined, { numeric: true });
      });

      setEvidence(evidenceData);
      setControls(sortedControls);
    } catch (err) {
      console.error('Error fetching evidence:', err);
      setError('Failed to load evidence');
    } finally {
      setLoading(false);
    }
  };

  // Handle file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
      }
      setSelectedFile(file);
    }
  };

  // Handle file upload
  const handleUpload = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      alert('Please select a file');
      return;
    }

    if (!selectedControlId) {
      alert('Please select a control');
      return;
    }

    try {
      setUploading(true);

      // Create evidence record
      const newEvidence = await evidenceAPI.create({
        control_id: parseInt(selectedControlId),
        filename: selectedFile.name,
        file_type: selectedFile.type || 'application/octet-stream',
        file_size: selectedFile.size,
        description: description || '',
      });

      // Add to local state
      setEvidence([newEvidence, ...evidence]);

      // Reset form
      setSelectedFile(null);
      setSelectedControlId('');
      setDescription('');
      setUploadModalOpen(false);

      alert('Evidence uploaded successfully!');
    } catch (err) {
      console.error('Error uploading evidence:', err);
      alert('Failed to upload evidence');
    } finally {
      setUploading(false);
    }
  };

  // Delete evidence
  const handleDelete = async (evidenceId) => {
    if (!window.confirm('Are you sure you want to delete this evidence?')) {
      return;
    }

    try {
      await evidenceAPI.delete(evidenceId);
      setEvidence(evidence.filter(e => e.id !== evidenceId));
      alert('Evidence deleted successfully');
    } catch (err) {
      console.error('Error deleting evidence:', err);
      alert('Failed to delete evidence');
    }
  };

  // Filter evidence
  const filteredEvidence = evidence.filter((item) => {
    const matchesSearch =
      searchQuery === '' ||
      item.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.description && item.description.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesControl =
      selectedControl === 'all' || item.control_id === parseInt(selectedControl);

    return matchesSearch && matchesControl;
  });

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  // Get control info
  const getControlInfo = (controlId) => {
    const control = controls.find(c => c.id === controlId);
    return control ? `${control.control_id} - ${control.title}` : 'Unknown Control';
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading evidence...</p>
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Evidence Repository</h1>
          <p className="text-gray-600 mt-1">Manage compliance evidence and documentation</p>
        </div>
        <button
          onClick={() => setUploadModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Upload className="w-5 h-5" />
          Upload Evidence
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Evidence</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{evidence.length}</p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Controls with Evidence</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {new Set(evidence.map(e => e.control_id)).size}
              </p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <LinkIcon className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Size</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {formatFileSize(evidence.reduce((sum, e) => sum + (e.file_size || 0), 0))}
              </p>
            </div>
            <div className="bg-purple-100 rounded-full p-3">
              <FileText className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Evidence
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by filename or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Control Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Control
            </label>
            <select
              value={selectedControl}
              onChange={(e) => setSelectedControl(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Controls</option>
              {controls.map((control) => (
                <option key={control.id} value={control.id}>
                  {control.control_id} - {control.title}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-4 text-sm text-gray-600">
          Showing {filteredEvidence.length} of {evidence.length} evidence items
        </div>
      </div>

      {/* Evidence List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {filteredEvidence.length === 0 ? (
          <div className="p-8 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No evidence found</p>
            <button
              onClick={() => setUploadModalOpen(true)}
              className="mt-4 text-blue-600 hover:text-blue-700"
            >
              Upload your first evidence
            </button>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Filename
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Control
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Uploaded
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredEvidence.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <FileText className="w-5 h-5 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">{item.filename}</div>
                        {item.description && (
                          <div className="text-sm text-gray-500">{item.description}</div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {getControlInfo(item.control_id)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatFileSize(item.file_size)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatDate(item.created_at)}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="text-red-600 hover:text-red-700"
                      title="Delete"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Upload Modal */}
      {uploadModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Evidence</h2>
            
            <form onSubmit={handleUpload} className="space-y-4">
              {/* File Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select File
                </label>
                <input
                  type="file"
                  onChange={handleFileChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.txt,.xlsx,.xls"
                />
                {selectedFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    Selected: {selectedFile.name} - Size: {formatFileSize(selectedFile.size)}
                  </p>
                )}
              </div>

              {/* Control Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Link to Control
                </label>
                <select
                  value={selectedControlId}
                  onChange={(e) => setSelectedControlId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select a control...</option>
                  {controls.map((control) => (
                    <option key={control.id} value={control.id}>
                      {control.control_id} - {control.title}
                    </option>
                  ))}
                </select>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  placeholder="Add a description for this evidence..."
                />
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setUploadModalOpen(false);
                    setSelectedFile(null);
                    setSelectedControlId('');
                    setDescription('');
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  disabled={uploading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  disabled={uploading}
                >
                  {uploading ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Evidence;