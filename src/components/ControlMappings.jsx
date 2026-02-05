import React, { useState, useEffect } from 'react';
import { Link2, CheckCircle2, ArrowRight } from 'lucide-react';
import api from '../services/api';

const ControlMappings = ({ controlId }) => {
  const [mappings, setMappings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMappings = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/controls/${controlId}/mappings`);
        setMappings(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (controlId) {
      fetchMappings();
    }
  }, [controlId]);

  if (loading) {
    return (
      <div className="animate-pulse bg-muted rounded-lg p-6">
        <div className="h-4 bg-muted-foreground/20 rounded w-1/4 mb-3"></div>
        <div className="h-3 bg-muted-foreground/20 rounded w-3/4"></div>
      </div>
    );
  }

  if (error) {
    return null;
  }

  if (!mappings || (mappings.satisfies.length === 0 && mappings.satisfied_by.length === 0)) {
    return null;
  }

  return (
    <div className="space-y-6 animate-slide-in">
      {mappings.satisfies && mappings.satisfies.length > 0 && (
        <div className="bg-gradient-to-br from-emerald-50 to-green-50 border-2 border-emerald-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-success rounded-lg">
              <CheckCircle2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-foreground">
                Also Satisfies
              </h3>
              <p className="text-sm text-muted-foreground">
                {mappings.satisfies.length} cross-framework {mappings.satisfies.length === 1 ? 'requirement' : 'requirements'}
              </p>
            </div>
          </div>
          <p className="text-sm text-muted-foreground mb-4 leading-relaxed">
            ✨ Implementing this control automatically helps satisfy the following requirements in other frameworks:
          </p>
          <div className="space-y-3">
            {mappings.satisfies.map((mapping, index) => (
              <MappingItem key={index} mapping={mapping} type="outgoing" />
            ))}
          </div>
        </div>
      )}

      {mappings.satisfied_by && mappings.satisfied_by.length > 0 && (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-primary rounded-lg">
              <Link2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-foreground">
                Satisfied By
              </h3>
              <p className="text-sm text-muted-foreground">
                {mappings.satisfied_by.length} supporting {mappings.satisfied_by.length === 1 ? 'control' : 'controls'}
              </p>
            </div>
          </div>
          <p className="text-sm text-muted-foreground mb-4 leading-relaxed">
            🔗 This requirement is satisfied by implementing these controls:
          </p>
          <div className="space-y-3">
            {mappings.satisfied_by.map((mapping, index) => (
              <MappingItem key={index} mapping={mapping} type="incoming" />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const MappingItem = ({ mapping, type }) => {
  const getMappingTypeLabel = (mappingType) => {
    switch (mappingType) {
      case 'full': return 'Full Coverage';
      case 'partial': return 'Partial Coverage';
      case 'equivalent': return 'Equivalent';
      case 'related': return 'Related';
      default: return mappingType;
    }
  };

  const getMappingTypeColor = (mappingType) => {
    switch (mappingType) {
      case 'full':
      case 'equivalent':
        return 'bg-success/10 text-success border-success/30';
      case 'partial':
        return 'bg-warning/10 text-warning border-warning/30';
      case 'related':
        return 'bg-primary/10 text-primary border-primary/30';
      default:
        return 'bg-muted text-muted-foreground border-border';
    }
  };

  return (
    <div className="bg-white rounded-lg p-4 border-2 border-border hover:border-primary/50 hover:shadow-md transition-all duration-200 group">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            {type === 'outgoing' && (
              <ArrowRight className="w-4 h-4 text-muted-foreground flex-shrink-0 group-hover:text-primary transition-colors" />
            )}
            <span className="font-mono text-sm font-bold text-primary bg-primary/5 px-2.5 py-1 rounded-md">
              {mapping.control_identifier}
            </span>
            <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-secondary text-secondary-foreground">
              {mapping.framework_short_name}
            </span>
          </div>
          <p className="text-sm text-foreground font-medium leading-relaxed">
            {mapping.control_title}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1 flex-shrink-0">
          <span className={`text-xs font-semibold px-3 py-1.5 rounded-full border ${getMappingTypeColor(mapping.mapping_type)}`}>
            {getMappingTypeLabel(mapping.mapping_type)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default ControlMappings;