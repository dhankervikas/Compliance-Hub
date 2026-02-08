import React, { useState, useEffect, useCallback } from 'react';
import config from '../config';

const API_BASE = config.API_BASE_URL;

// ─── Status Badge Component ───
const StatusBadge = ({ status }) => {
  const map = {
    PASS: { bg: '#ECFDF5', text: '#065F46', label: 'PASS' },
    MET: { bg: '#ECFDF5', text: '#065F46', label: 'MET' },
    FAIL: { bg: '#FEF2F2', text: '#991B1B', label: 'FAIL' },
    NOT_MET: { bg: '#FEF2F2', text: '#991B1B', label: 'NOT MET' },
    PARTIAL: { bg: '#FFFBEB', text: '#92400E', label: 'PARTIAL' },
    PENDING: { bg: '#F3F4F6', text: '#374151', label: 'PENDING' },
    DRAFT: { bg: '#EEF2FF', text: '#3730A3', label: 'DRAFT' },
    REVIEW: { bg: '#FFF7ED', text: '#9A3412', label: 'IN REVIEW' },
    APPROVED: { bg: '#ECFDF5', text: '#065F46', label: 'APPROVED' },
  };
  const s = map[(status || '').toUpperCase()] || map.PENDING;
  return (
    <span style={{
      background: s.bg, color: s.text, padding: '2px 10px',
      borderRadius: '12px', fontSize: '11px', fontWeight: 600, letterSpacing: '0.5px',
      display: 'inline-block',
    }}>
      {s.label}
    </span>
  );
};

// ─── Source Badge (AUTOMATED / MANUAL / HYBRID) ───
const SourceBadge = ({ source }) => {
  const map = {
    AUTOMATED: { bg: '#DBEAFE', text: '#1E40AF', icon: '⚡' },
    MANUAL: { bg: '#FEF3C7', text: '#92400E', icon: '✋' },
    HYBRID: { bg: '#E0E7FF', text: '#3730A3', icon: '🔄' },
  };
  const s = map[(source || '').toUpperCase()] || map.MANUAL;
  return (
    <span style={{
      background: s.bg, color: s.text, padding: '2px 8px',
      borderRadius: '8px', fontSize: '10px', fontWeight: 600,
      display: 'inline-flex', alignItems: 'center', gap: '3px',
    }}>
      {s.icon} {source || 'MANUAL'}
    </span>
  );
};

// ─── Main Component ───
const EnhancedControlDetail = ({ controlId, controlData, onClose }) => {
  // Core state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [control, setControl] = useState(controlData || null);

  // Requirements (AI-generated, cached)
  const [requirements, setRequirements] = useState([]);
  const [explanation, setExplanation] = useState('');
  const [reqCached, setReqCached] = useState(false);
  const [generatingReqs, setGeneratingReqs] = useState(false);

  // Evidence
  const [evidenceMap, setEvidenceMap] = useState({}); // { reqIndex: [evidence] }
  const [allEvidence, setAllEvidence] = useState([]);
  const [uploading, setUploading] = useState(null); // reqIndex being uploaded to
  const [uploadingFile, setUploadingFile] = useState(false);
  const [stagedFile, setStagedFile] = useState(null); // { file, reqIndex }
  const [uploadSuccess, setUploadSuccess] = useState(null); // { reqIndex, message }
  const [aiReviewDetail, setAiReviewDetail] = useState(null); // { reqIndex, review }

  // Cross-framework
  const [crossFramework, setCrossFramework] = useState(null);
  const [loadingCross, setLoadingCross] = useState(false);

  // Policy generator
  const [policyContent, setPolicyContent] = useState('');
  const [policyStatus, setPolicyStatus] = useState(null); // null, 'generating', 'draft', 'editing', 'review', 'approved'
  const [editingPolicy, setEditingPolicy] = useState(false);
  const [editedPolicyContent, setEditedPolicyContent] = useState('');

  // Gap analysis
  const [gapResult, setGapResult] = useState(null);

  // Active tab
  const [activeTab, setActiveTab] = useState('requirements');

  // Expanded requirement
  const [expandedReq, setExpandedReq] = useState(null);

  const cid = controlId || control?.control_id;

  // ─── FETCH REQUIREMENTS (cached after first generation) ───
  const fetchRequirements = useCallback(async (forceRegenerate = false) => {
    if (!cid) return;
    setGeneratingReqs(true);
    setError(null);
    try {
      const res = await fetch(
        `${API_BASE}/controls/${cid}/requirements?regenerate=${forceRegenerate}`
      );
      if (!res.ok) throw new Error(`Failed to load requirements: ${res.status}`);
      const data = await res.json();
      setRequirements(data.requirements || []);
      setExplanation(data.explanation || '');
      setReqCached(data.cached || false);
      if (data.control_title && !control?.title) {
        setControl(prev => ({ ...prev, title: data.control_title }));
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setGeneratingReqs(false);
      setLoading(false);
    }
  }, [cid, control?.title]);

  // ─── FETCH EVIDENCE ───
  const fetchEvidence = useCallback(async () => {
    if (!cid) return;
    try {
      const res = await fetch(`${API_BASE}/controls/${cid}/evidence`);
      if (!res.ok) return;
      const data = await res.json();
      setAllEvidence(data.evidence || []);
    } catch (err) {
      console.error('Evidence fetch error:', err);
    }
  }, [cid]);

  // ─── FETCH CROSS-FRAMEWORK ───
  const fetchCrossFramework = useCallback(async () => {
    if (!cid) return;
    setLoadingCross(true);
    try {
      const res = await fetch(`${API_BASE}/controls/${cid}/cross-framework`);
      if (!res.ok) return;
      const data = await res.json();
      setCrossFramework(data);
    } catch (err) {
      console.error('Cross-framework error:', err);
    } finally {
      setLoadingCross(false);
    }
  }, [cid]);

  // ─── INITIAL LOAD ───
  useEffect(() => {
    fetchRequirements(false);
    fetchEvidence();
  }, [fetchRequirements, fetchEvidence]);

  // ─── UPLOAD EVIDENCE ───
  const handleUpload = async (file, reqIndex, isConfidential = false) => {
    if (!file || !cid) return;
    setUploadingFile(true);
    setUploadSuccess(null);
    setAiReviewDetail(null);
    const reqName = requirements[reqIndex]?.name || '';

    const formData = new FormData();
    formData.append('file', file);
    formData.append('requirement_name', reqName);
    formData.append('is_confidential', isConfidential);

    try {
      const res = await fetch(`${API_BASE}/controls/${cid}/evidence/upload`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Upload failed');
      const data = await res.json();

      // Refresh evidence list
      await fetchEvidence();

      // Show success confirmation
      setUploadSuccess({ reqIndex, message: `"${file.name}" uploaded successfully.` });
      setStagedFile(null);

      // Show AI review detail (never reject — always show review)
      if (data.ai_review) {
        setAiReviewDetail({ reqIndex, review: data.ai_review });
      }
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
    } finally {
      setUploadingFile(false);
    }
  };

  // ─── GENERATE POLICY ───
  const handleGeneratePolicy = async () => {
    if (!cid) return;
    setPolicyStatus('generating');
    try {
      const formData = new FormData();
      formData.append('company_name', 'Our Organization');
      formData.append('industry', 'Technology');

      const res = await fetch(`${API_BASE}/controls/${cid}/generate-policy`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Policy generation failed');
      const data = await res.json();
      setPolicyContent(data.content || '');
      setEditedPolicyContent(data.content || '');
      setPolicyStatus('draft');
    } catch (err) {
      setError(`Policy generation failed: ${err.message}`);
      setPolicyStatus(null);
    }
  };

  // ─── RUN GAP ANALYSIS ───
  const handleGapAnalysis = async () => {
    if (!cid) return;
    try {
      const res = await fetch(`${API_BASE}/controls/${cid}/gap-analysis`);
      if (!res.ok) throw new Error('Gap analysis failed');
      const data = await res.json();
      setGapResult(data);
    } catch (err) {
      setError(err.message);
    }
  };

  // ─── APPLY EVIDENCE CROSS-FRAMEWORK ───
  const handleApplyCrossFramework = async (evidenceId) => {
    if (!cid || !evidenceId) return;
    try {
      const res = await fetch(
        `${API_BASE}/controls/${cid}/evidence/${evidenceId}/apply-cross-framework`,
        { method: 'POST' }
      );
      if (!res.ok) throw new Error('Cross-framework apply failed');
      const data = await res.json();
      alert(`Evidence applied to ${data.total_applied} controls across frameworks!`);
      fetchCrossFramework();
    } catch (err) {
      setError(err.message);
    }
  };

  // ─── POLICY WORKFLOW ───
  const handleSendForApproval = () => {
    setPolicyStatus('review');
    // In production: POST to a document workflow endpoint
    alert('Policy sent for approval. Approver will be notified.');
  };

  const handleApprovePolicy = () => {
    setPolicyStatus('approved');
  };

  // ─── STYLES ───
  const styles = {
    overlay: {
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.5)', zIndex: 1000,
      display: 'flex', justifyContent: 'center', alignItems: 'flex-start',
      paddingTop: '40px', overflowY: 'auto',
    },
    modal: {
      background: '#FFFFFF', borderRadius: '12px', width: '90%', maxWidth: '820px',
      maxHeight: '90vh', overflowY: 'auto', boxShadow: '0 25px 50px rgba(0,0,0,0.25)',
      fontFamily: "'Inter', -apple-system, sans-serif",
    },
    header: {
      padding: '24px 28px 16px', borderBottom: '1px solid #E5E7EB',
      position: 'sticky', top: 0, background: '#FFF', zIndex: 10, borderRadius: '12px 12px 0 0',
    },
    body: { padding: '0 28px 28px' },
    card: {
      background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '10px',
      padding: '18px', marginBottom: '14px',
    },
    tab: (active) => ({
      padding: '8px 16px', border: 'none', borderRadius: '8px', cursor: 'pointer',
      fontSize: '13px', fontWeight: active ? 600 : 400,
      background: active ? '#1E293B' : 'transparent',
      color: active ? '#FFF' : '#64748B',
      transition: 'all 0.2s',
    }),
    btn: (variant) => ({
      padding: '8px 16px', border: 'none', borderRadius: '8px', cursor: 'pointer',
      fontSize: '13px', fontWeight: 600,
      background: variant === 'primary' ? '#1E293B' : variant === 'success' ? '#059669' : variant === 'danger' ? '#DC2626' : '#F1F5F9',
      color: variant === 'primary' || variant === 'success' || variant === 'danger' ? '#FFF' : '#334155',
      transition: 'all 0.15s',
    }),
    reqRow: (expanded) => ({
      background: expanded ? '#F0F9FF' : '#FFF',
      border: `1px solid ${expanded ? '#BAE6FD' : '#E5E7EB'}`,
      borderRadius: '10px', padding: '14px 16px', marginBottom: '8px',
      cursor: 'pointer', transition: 'all 0.2s',
    }),
    uploadZone: {
      border: '2px dashed #CBD5E1', borderRadius: '8px', padding: '20px',
      textAlign: 'center', cursor: 'pointer', background: '#FAFBFC',
      transition: 'all 0.2s',
    },
  };

  // ─── LOADING STATE ───
  if (loading) {
    return (
      <div style={styles.overlay}>
        <div style={{ ...styles.modal, padding: '60px', textAlign: 'center' }}>
          <div style={{ fontSize: '32px', marginBottom: '16px' }}>⚙️</div>
          <div style={{ fontSize: '15px', color: '#64748B', fontWeight: 500 }}>
            {generatingReqs ? 'Genie is generating requirements...' : 'Loading control...'}
          </div>
          <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '8px' }}>
            First time takes 3-5 seconds. Cached after that.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.overlay} onClick={(e) => { if (e.target === e.currentTarget) onClose?.(); }}>
      <div style={styles.modal}>

        {/* ─── HEADER ─── */}
        <div style={styles.header}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                <span style={{
                  background: '#F1F5F9', padding: '3px 10px', borderRadius: '6px',
                  fontSize: '13px', fontWeight: 700, color: '#334155',
                }}>{cid}</span>
                <StatusBadge status={control?.status || 'PENDING'} />
                {reqCached && (
                  <span style={{ fontSize: '10px', color: '#94A3B8' }}>● Cached</span>
                )}
              </div>
              <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: '#0F172A' }}>
                {control?.title || `Control ${cid}`}
              </h2>
            </div>
            <button
              onClick={onClose}
              style={{ background: 'none', border: 'none', fontSize: '22px', cursor: 'pointer', color: '#94A3B8', padding: '0 4px' }}
            >✕</button>
          </div>

          {/* Description */}
          {control?.description && (
            <p style={{ margin: '10px 0 0', fontSize: '13px', color: '#64748B', lineHeight: 1.5 }}>
              {control.description}
            </p>
          )}

          {/* Business Goal */}
          {explanation && (
            <div style={{
              margin: '12px 0 0', padding: '10px 14px', background: '#F0F9FF',
              borderRadius: '8px', borderLeft: '3px solid #0EA5E9',
              fontSize: '13px', color: '#0C4A6E', fontWeight: 500,
            }}>
              🎯 {explanation}
            </div>
          )}

          {/* Tab Navigation */}
          <div style={{ display: 'flex', gap: '6px', marginTop: '16px' }}>
            {['requirements', 'evidence', 'cross-framework', 'policy'].map(tab => (
              <button
                key={tab}
                style={styles.tab(activeTab === tab)}
                onClick={() => {
                  setActiveTab(tab);
                  if (tab === 'cross-framework' && !crossFramework) fetchCrossFramework();
                }}
              >
                {tab === 'requirements' && `Requirements (${requirements.length})`}
                {tab === 'evidence' && `Evidence (${allEvidence.length})`}
                {tab === 'cross-framework' && '🔗 Cross-Framework'}
                {tab === 'policy' && '📄 Policy'}
              </button>
            ))}
          </div>
        </div>

        {/* ─── BODY ─── */}
        <div style={styles.body}>
          {error && (
            <div style={{
              margin: '14px 0', padding: '12px 16px', background: '#FEF2F2',
              borderRadius: '8px', color: '#991B1B', fontSize: '13px',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            }}>
              <span>⚠️ {error}</span>
              <button onClick={() => setError(null)} style={{ ...styles.btn(), fontSize: '11px' }}>Dismiss</button>
            </div>
          )}

          {/* ━━━ TAB: REQUIREMENTS ━━━ */}
          {activeTab === 'requirements' && (
            <div style={{ marginTop: '16px' }}>

              {/* CONTROL-LEVEL UPLOAD — one document can satisfy multiple requirements */}
              <div style={{
                background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '10px',
                padding: '16px', marginBottom: '16px',
              }}>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#0F172A', marginBottom: '8px' }}>
                  📄 Upload Evidence for this Control
                </div>
                <div style={{ fontSize: '12px', color: '#64748B', marginBottom: '10px' }}>
                  One document can satisfy multiple requirements. Upload once — Genie will check which requirements are met.
                </div>

                {/* Staged file for control-level */}
                {stagedFile && stagedFile.reqIndex === -1 && (
                  <div style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '10px 14px', background: '#F0F9FF', borderRadius: '8px',
                    border: '1px solid #BAE6FD', marginBottom: '8px',
                  }}>
                    <span style={{ fontSize: '13px', color: '#0C4A6E' }}>
                      📎 {stagedFile.file.name} ({(stagedFile.file.size / 1024).toFixed(1)} KB)
                    </span>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      <button
                        onClick={() => handleUpload(stagedFile.file, -1)}
                        disabled={uploadingFile}
                        style={{ ...styles.btn('primary'), opacity: uploadingFile ? 0.6 : 1 }}
                      >
                        {uploadingFile ? '⏳ Uploading & Reviewing...' : '📤 Upload & Review'}
                      </button>
                      <button onClick={() => setStagedFile(null)} style={styles.btn()}>✕</button>
                    </div>
                  </div>
                )}

                {(!stagedFile || stagedFile.reqIndex !== -1) && (
                  <div style={styles.uploadZone}>
                    <input
                      type="file"
                      accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.txt,.md,.xlsx"
                      onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) setStagedFile({ file, reqIndex: -1 });
                        e.target.value = '';
                      }}
                      style={{ display: 'none' }}
                      id="file-input-control"
                    />
                    <label htmlFor="file-input-control" style={{ cursor: 'pointer', display: 'block' }}>
                      <div style={{ fontSize: '20px', marginBottom: '4px' }}>📤</div>
                      <div style={{ fontSize: '12px', color: '#64748B', fontWeight: 500 }}>
                        Choose File or Drag & Drop
                      </div>
                      <div style={{ fontSize: '11px', color: '#94A3B8' }}>
                        PDF, Word, Excel, PNG • Genie reviews against all requirements
                      </div>
                    </label>
                  </div>
                )}

                {/* Control-level upload success */}
                {uploadSuccess && uploadSuccess.reqIndex === -1 && (
                  <div style={{
                    padding: '10px 14px', background: '#ECFDF5', borderRadius: '8px',
                    border: '1px solid #A7F3D0', marginTop: '8px',
                    fontSize: '13px', color: '#065F46', fontWeight: 500,
                  }}>
                    ✅ {uploadSuccess.message}
                  </div>
                )}

                {/* Control-level AI review */}
                {aiReviewDetail && aiReviewDetail.reqIndex === -1 && (
                  <div style={{
                    background: '#1E293B', borderRadius: '10px', padding: '16px',
                    marginTop: '10px', color: '#FFF',
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 700 }}>⚡ Genie Evidence Review</span>
                      <StatusBadge status={aiReviewDetail.review.final_verdict || 'PENDING'} />
                    </div>
                    {aiReviewDetail.review.summary && (
                      <p style={{
                        fontSize: '12px', color: '#CBD5E1', lineHeight: 1.6,
                        borderLeft: '3px solid #F59E0B', paddingLeft: '10px',
                        marginBottom: '10px', fontStyle: 'italic',
                      }}>
                        {aiReviewDetail.review.summary}
                      </p>
                    )}
                    {aiReviewDetail.review.gaps_found && aiReviewDetail.review.gaps_found.length > 0 &&
                      aiReviewDetail.review.gaps_found[0] !== 'None' && (
                        <div style={{ marginBottom: '8px' }}>
                          <div style={{ fontSize: '11px', fontWeight: 600, color: '#F87171', marginBottom: '4px' }}>
                            GAPS IDENTIFIED:
                          </div>
                          {aiReviewDetail.review.gaps_found.map((gap, gi) => (
                            <div key={gi} style={{ fontSize: '12px', color: '#FCA5A5', paddingLeft: '10px', marginBottom: '2px' }}>
                              • {gap}
                            </div>
                          ))}
                        </div>
                      )}
                    {aiReviewDetail.review.date_check_passed !== undefined && (
                      <div style={{ fontSize: '11px', color: aiReviewDetail.review.date_check_passed ? '#6EE7B7' : '#FCA5A5' }}>
                        {aiReviewDetail.review.date_check_passed
                          ? '✅ Document date is current (within 12 months)'
                          : '⚠️ Document may be outdated (>12 months old)'}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Regenerate button */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <div style={{ fontSize: '13px', color: '#64748B' }}>
                  {requirements.length} requirements generated
                  {reqCached && <span style={{ color: '#059669' }}> • Locked (consistent)</span>}
                </div>
                {/* Regenerate button removed per user request - requirements are fixed once generated */}
              </div>

              {/* Requirements List */}
              {requirements.map((req, idx) => {
                const isExpanded = expandedReq === idx;
                const reqEvidence = allEvidence.filter(
                  e => e.file_name && req.name && e.file_name.toLowerCase().includes(req.name.toLowerCase().slice(0, 10))
                );
                // Determine status based on evidence
                const reqStatus = reqEvidence.length > 0
                  ? (reqEvidence.some(e => e.ai_review_status === 'PASS') ? 'PASS' : 'PARTIAL')
                  : 'PENDING';

                return (
                  <div key={idx} style={styles.reqRow(isExpanded)}>
                    {/* Requirement Header Row */}
                    <div
                      onClick={() => setExpandedReq(isExpanded ? null : idx)}
                      style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1 }}>
                        <span style={{ fontSize: '16px' }}>
                          {reqStatus === 'PASS' ? '✅' : reqStatus === 'PARTIAL' ? '🟡' : '⬜'}
                        </span>
                        <div>
                          <div style={{ fontSize: '13px', fontWeight: 600, color: '#0F172A' }}>
                            {req.name || `Requirement ${idx + 1}`}
                          </div>
                          <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '2px' }}>
                            {req.type || 'Artifact'}
                          </div>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <SourceBadge source={req.source} />
                        <StatusBadge status={reqStatus} />
                        <span style={{ fontSize: '14px', color: '#94A3B8', transition: 'transform 0.2s', transform: isExpanded ? 'rotate(180deg)' : 'rotate(0)' }}>▾</span>
                      </div>
                    </div>

                    {/* Expanded Content */}
                    {isExpanded && (
                      <div style={{ marginTop: '14px', paddingTop: '14px', borderTop: '1px solid #E5E7EB' }}>
                        {/* Description */}
                        {req.desc && (
                          <p style={{ fontSize: '13px', color: '#475569', lineHeight: 1.6, margin: '0 0 12px' }}>
                            {req.desc}
                          </p>
                        )}

                        {/* Auditor Guidance */}
                        {req.audit_guidance && (
                          <div style={{
                            background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: '8px',
                            padding: '10px 14px', marginBottom: '12px', fontSize: '12px', color: '#92400E',
                          }}>
                            <strong>🔍 Auditor Tip:</strong> {req.audit_guidance}
                          </div>
                        )}

                        {/* Evidence Types Needed */}
                        {req.evidence_types && req.evidence_types.length > 0 && (
                          <div style={{ marginBottom: '12px' }}>
                            <div style={{ fontSize: '11px', fontWeight: 600, color: '#64748B', marginBottom: '6px' }}>
                              ACCEPTABLE EVIDENCE:
                            </div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                              {req.evidence_types.map((et, eti) => (
                                <span key={eti} style={{
                                  background: '#F1F5F9', border: '1px solid #E2E8F0', borderRadius: '6px',
                                  padding: '2px 8px', fontSize: '11px', color: '#475569',
                                }}>
                                  {et}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Automation Note */}
                        {(req.source || '').toUpperCase() === 'AUTOMATED' && (
                          <div style={{
                            background: '#EFF6FF', border: '1px solid #BFDBFE', borderRadius: '8px',
                            padding: '10px 14px', marginBottom: '12px', fontSize: '12px', color: '#1E40AF',
                          }}>
                            ⚡ <strong>Automated:</strong> This requirement can be satisfied through system integration (API, logs, screenshots). Evidence is collected automatically when connected.
                          </div>
                        )}

                        {/* Existing Evidence for this Requirement */}
                        {reqEvidence.length > 0 && (
                          <div style={{ marginBottom: '12px' }}>
                            <div style={{ fontSize: '12px', fontWeight: 600, color: '#64748B', marginBottom: '6px' }}>
                              UPLOADED EVIDENCE
                            </div>
                            {reqEvidence.map((ev, eidx) => (
                              <div key={eidx} style={{
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                padding: '8px 12px', background: '#FFF', borderRadius: '6px',
                                border: '1px solid #E5E7EB', marginBottom: '4px',
                              }}>
                                <span style={{ fontSize: '12px', color: '#334155' }}>📎 {ev.file_name}</span>
                                <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                                  <StatusBadge status={ev.ai_review_status || 'PENDING'} />
                                  {crossFramework && crossFramework.total_related > 0 && (
                                    <button
                                      onClick={(e) => { e.stopPropagation(); handleApplyCrossFramework(ev.id); }}
                                      style={{ ...styles.btn('primary'), fontSize: '10px', padding: '4px 8px' }}
                                      title="Apply this evidence to related controls in other frameworks"
                                    >
                                      🔗 Apply Cross-Framework
                                    </button>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Upload Zone */}
                        <div style={{ marginBottom: '12px' }}>
                          {/* Staged file preview + upload button */}
                          {stagedFile && stagedFile.reqIndex === idx && (
                            <div style={{
                              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                              padding: '10px 14px', background: '#F0F9FF', borderRadius: '8px',
                              border: '1px solid #BAE6FD', marginBottom: '8px',
                            }}>
                              <span style={{ fontSize: '13px', color: '#0C4A6E' }}>
                                📎 {stagedFile.file.name} ({(stagedFile.file.size / 1024).toFixed(1)} KB)
                              </span>
                              <div style={{ display: 'flex', gap: '6px' }}>
                                <button
                                  onClick={() => handleUpload(stagedFile.file, idx)}
                                  disabled={uploadingFile}
                                  style={{
                                    ...styles.btn('primary'),
                                    opacity: uploadingFile ? 0.6 : 1,
                                  }}
                                >
                                  {uploadingFile ? '⏳ Uploading...' : '📤 Upload'}
                                </button>
                                <button
                                  onClick={() => setStagedFile(null)}
                                  style={styles.btn()}
                                >
                                  ✕ Cancel
                                </button>
                              </div>
                            </div>
                          )}

                          {/* File picker (hidden when file is staged) */}
                          {(!stagedFile || stagedFile.reqIndex !== idx) && (
                            <div
                              style={styles.uploadZone}
                              onDragOver={(e) => e.preventDefault()}
                              onDrop={(e) => {
                                e.preventDefault();
                                const file = e.dataTransfer.files[0];
                                if (file) setStagedFile({ file, reqIndex: idx });
                              }}
                            >
                              <input
                                type="file"
                                accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.txt,.md,.xlsx"
                                onChange={(e) => {
                                  const file = e.target.files[0];
                                  if (file) setStagedFile({ file, reqIndex: idx });
                                  e.target.value = '';
                                }}
                                style={{ display: 'none' }}
                                id={`file-input-${idx}`}
                              />
                              <label htmlFor={`file-input-${idx}`} style={{ cursor: 'pointer', display: 'block' }}>
                                <div style={{ fontSize: '20px', marginBottom: '4px' }}>📤</div>
                                <div style={{ fontSize: '12px', color: '#64748B', fontWeight: 500 }}>
                                  Choose File or Drag & Drop
                                </div>
                                <div style={{ fontSize: '11px', color: '#94A3B8' }}>
                                  PDF, Word, Excel, PNG supported • Genie will review after upload
                                </div>
                              </label>
                            </div>
                          )}
                        </div>

                        {/* Upload Success Confirmation */}
                        {uploadSuccess && uploadSuccess.reqIndex === idx && (
                          <div style={{
                            padding: '10px 14px', background: '#ECFDF5', borderRadius: '8px',
                            border: '1px solid #A7F3D0', marginBottom: '10px',
                            fontSize: '13px', color: '#065F46', fontWeight: 500,
                          }}>
                            ✅ {uploadSuccess.message}
                          </div>
                        )}

                        {/* AI Review Detail */}
                        {aiReviewDetail && aiReviewDetail.reqIndex === idx && (
                          <div style={{
                            background: '#1E293B', borderRadius: '10px', padding: '16px',
                            marginBottom: '10px', color: '#FFF',
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                              <span style={{ fontSize: '13px', fontWeight: 700 }}>
                                ⚡ Genie Evidence Review
                              </span>
                              <StatusBadge status={aiReviewDetail.review.final_verdict || 'PENDING'} />
                            </div>

                            {/* Summary */}
                            {aiReviewDetail.review.summary && (
                              <p style={{
                                fontSize: '12px', color: '#CBD5E1', lineHeight: 1.6,
                                borderLeft: '3px solid #F59E0B', paddingLeft: '10px',
                                marginBottom: '10px', fontStyle: 'italic',
                              }}>
                                {aiReviewDetail.review.summary}
                              </p>
                            )}

                            {/* Gaps Found */}
                            {aiReviewDetail.review.gaps_found && aiReviewDetail.review.gaps_found.length > 0 &&
                              aiReviewDetail.review.gaps_found[0] !== 'None' && (
                                <div style={{ marginBottom: '8px' }}>
                                  <div style={{ fontSize: '11px', fontWeight: 600, color: '#F87171', marginBottom: '4px' }}>
                                    GAPS IDENTIFIED:
                                  </div>
                                  {aiReviewDetail.review.gaps_found.map((gap, gi) => (
                                    <div key={gi} style={{ fontSize: '12px', color: '#FCA5A5', paddingLeft: '10px', marginBottom: '2px' }}>
                                      • {gap}
                                    </div>
                                  ))}
                                </div>
                              )}

                            {/* Date Check */}
                            {aiReviewDetail.review.date_check_passed !== undefined && (
                              <div style={{ fontSize: '11px', color: aiReviewDetail.review.date_check_passed ? '#6EE7B7' : '#FCA5A5' }}>
                                {aiReviewDetail.review.date_check_passed
                                  ? '✅ Document date is current (within 12 months)'
                                  : '⚠️ Document may be outdated (>12 months old)'}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Gap Analysis Button */}
              {requirements.length > 0 && (
                <div style={{ marginTop: '16px', display: 'flex', gap: '10px' }}>
                  <button onClick={handleGapAnalysis} style={styles.btn('primary')}>
                    🔍 Run Gap Analysis
                  </button>
                </div>
              )}

              {/* Gap Analysis Result */}
              {gapResult && (
                <div style={{
                  ...styles.card, marginTop: '14px',
                  borderLeft: `4px solid ${gapResult.status === 'MET' ? '#059669' : gapResult.status === 'PARTIAL' ? '#F59E0B' : '#DC2626'}`,
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '14px', fontWeight: 700, color: '#0F172A' }}>Gap Analysis Result</span>
                    <StatusBadge status={gapResult.status} />
                  </div>
                  <p style={{ fontSize: '13px', color: '#475569', margin: '0 0 8px', lineHeight: 1.5 }}>
                    {gapResult.reasoning}
                  </p>
                  {gapResult.missing_items?.length > 0 && gapResult.missing_items[0] !== 'None' && (
                    <div>
                      <div style={{ fontSize: '12px', fontWeight: 600, color: '#991B1B', marginBottom: '4px' }}>Missing:</div>
                      {gapResult.missing_items.map((item, i) => (
                        <div key={i} style={{ fontSize: '12px', color: '#64748B', paddingLeft: '12px' }}>• {item}</div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* ━━━ TAB: EVIDENCE ━━━ */}
          {activeTab === 'evidence' && (
            <div style={{ marginTop: '16px' }}>
              <div style={{ fontSize: '13px', color: '#64748B', marginBottom: '14px' }}>
                All evidence uploaded for this control
              </div>
              {allEvidence.length === 0 ? (
                <div style={{ ...styles.card, textAlign: 'center', padding: '30px' }}>
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>📁</div>
                  <div style={{ fontSize: '14px', color: '#64748B' }}>No evidence uploaded yet</div>
                  <div style={{ fontSize: '12px', color: '#94A3B8' }}>
                    Go to Requirements tab to upload evidence per requirement
                  </div>
                </div>
              ) : (
                allEvidence.map((ev, idx) => (
                  <div key={idx} style={{
                    ...styles.card,
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '12px 16px',
                  }}>
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 600, color: '#0F172A' }}>📎 {ev.file_name}</div>
                      <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '2px' }}>
                        {ev.file_type?.toUpperCase()} • {ev.uploaded_at ? new Date(ev.uploaded_at).toLocaleDateString() : 'N/A'}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <StatusBadge status={ev.ai_review_status || 'PENDING'} />
                      <button
                        onClick={() => handleApplyCrossFramework(ev.id)}
                        style={{ ...styles.btn('primary'), fontSize: '11px', padding: '5px 10px' }}
                      >
                        🔗 Apply to Other Frameworks
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* ━━━ TAB: CROSS-FRAMEWORK ━━━ */}
          {activeTab === 'cross-framework' && (
            <div style={{ marginTop: '16px' }}>
              {loadingCross ? (
                <div style={{ textAlign: 'center', padding: '30px', color: '#64748B' }}>
                  Loading cross-framework mappings...
                </div>
              ) : crossFramework ? (
                <>
                  <div style={{
                    ...styles.card,
                    background: 'linear-gradient(135deg, #EEF2FF, #F0F9FF)',
                    borderLeft: '4px solid #6366F1',
                  }}>
                    <div style={{ fontSize: '14px', fontWeight: 700, color: '#312E81', marginBottom: '4px' }}>
                      🔗 Cross-Framework Impact
                    </div>
                    <div style={{ fontSize: '13px', color: '#4338CA' }}>
                      Evidence from this control maps to <strong>{crossFramework.total_related}</strong> controls
                      across <strong>{crossFramework.total_frameworks_impacted}</strong> frameworks
                    </div>
                    {crossFramework.frameworks_impacted?.length > 0 && (
                      <div style={{ display: 'flex', gap: '6px', marginTop: '10px', flexWrap: 'wrap' }}>
                        {crossFramework.frameworks_impacted.map((fw, i) => (
                          <span key={i} style={{
                            background: '#FFF', border: '1px solid #C7D2FE', borderRadius: '6px',
                            padding: '3px 10px', fontSize: '11px', fontWeight: 600, color: '#4338CA',
                          }}>
                            {fw}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Related Controls */}
                  {crossFramework.related_controls?.map((rc, idx) => (
                    <div key={idx} style={{
                      ...styles.card, padding: '12px 16px',
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    }}>
                      <div>
                        <div style={{ fontSize: '13px', fontWeight: 600, color: '#0F172A' }}>
                          {rc.control_id} — {rc.title}
                        </div>
                        <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '2px' }}>
                          {rc.framework_name} • Intent: {rc.shared_intent}
                        </div>
                      </div>
                      <StatusBadge status={rc.status || 'PENDING'} />
                    </div>
                  ))}

                  {crossFramework.total_related === 0 && (
                    <div style={{ ...styles.card, textAlign: 'center', padding: '24px' }}>
                      <div style={{ fontSize: '13px', color: '#64748B' }}>
                        No cross-framework mappings found for this control.
                        Check that intent_framework_crosswalk has entries.
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div style={{ textAlign: 'center', padding: '30px' }}>
                  <button onClick={fetchCrossFramework} style={styles.btn('primary')}>
                    Load Cross-Framework Mappings
                  </button>
                </div>
              )}
            </div>
          )}

          {/* ━━━ TAB: POLICY ━━━ */}
          {activeTab === 'policy' && (
            <div style={{ marginTop: '16px' }}>
              {!policyStatus && (
                <div style={{ ...styles.card, textAlign: 'center', padding: '30px' }}>
                  <div style={{ fontSize: '32px', marginBottom: '10px' }}>📋</div>
                  <div style={{ fontSize: '15px', fontWeight: 600, color: '#0F172A', marginBottom: '6px' }}>
                    Generate Audit-Ready Policy
                  </div>
                  <div style={{ fontSize: '13px', color: '#64748B', marginBottom: '16px' }}>
                    Genie will create a professional policy document for this control,
                    ready for review and approval.
                  </div>
                  <button onClick={handleGeneratePolicy} style={styles.btn('primary')}>
                    ✨ Generate Policy
                  </button>
                </div>
              )}

              {policyStatus === 'generating' && (
                <div style={{ ...styles.card, textAlign: 'center', padding: '30px' }}>
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>⚙️</div>
                  <div style={{ fontSize: '14px', color: '#64748B' }}>Genie is drafting your policy...</div>
                  <div style={{ fontSize: '12px', color: '#94A3B8' }}>This takes 5-10 seconds</div>
                </div>
              )}

              {(policyStatus === 'draft' || policyStatus === 'editing' || policyStatus === 'review' || policyStatus === 'approved') && (
                <>
                  {/* Document Workflow Status */}
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px',
                    padding: '12px 16px', background: '#F8FAFC', borderRadius: '10px', border: '1px solid #E2E8F0',
                  }}>
                    <span style={{ fontSize: '12px', fontWeight: 600, color: '#64748B' }}>WORKFLOW:</span>
                    {['draft', 'review', 'approved'].map((step, i) => (
                      <React.Fragment key={step}>
                        <span style={{
                          padding: '3px 10px', borderRadius: '6px', fontSize: '11px', fontWeight: 600,
                          background: policyStatus === step ? '#1E293B' : '#F1F5F9',
                          color: policyStatus === step ? '#FFF' : '#94A3B8',
                        }}>
                          {step.charAt(0).toUpperCase() + step.slice(1)}
                        </span>
                        {i < 2 && <span style={{ color: '#CBD5E1' }}>→</span>}
                      </React.Fragment>
                    ))}
                  </div>

                  {/* Policy Content */}
                  {editingPolicy ? (
                    <textarea
                      value={editedPolicyContent}
                      onChange={(e) => setEditedPolicyContent(e.target.value)}
                      style={{
                        width: '100%', minHeight: '400px', padding: '16px',
                        border: '1px solid #CBD5E1', borderRadius: '10px',
                        fontSize: '13px', fontFamily: "'JetBrains Mono', monospace",
                        lineHeight: 1.7, resize: 'vertical', boxSizing: 'border-box',
                      }}
                    />
                  ) : (
                    <div style={{
                      ...styles.card, padding: '20px', maxHeight: '400px', overflowY: 'auto',
                      fontSize: '13px', lineHeight: 1.7, whiteSpace: 'pre-wrap', color: '#334155',
                    }}>
                      {editedPolicyContent || policyContent}
                    </div>
                  )}

                  {/* Policy Actions */}
                  <div style={{ display: 'flex', gap: '8px', marginTop: '12px', flexWrap: 'wrap' }}>
                    {policyStatus === 'draft' && (
                      <>
                        <button
                          onClick={() => { setEditingPolicy(!editingPolicy); }}
                          style={styles.btn()}
                        >
                          {editingPolicy ? '👁️ Preview' : '✏️ Edit'}
                        </button>
                        <button onClick={handleSendForApproval} style={styles.btn('primary')}>
                          📨 Send for Approval
                        </button>
                        <button onClick={handleGeneratePolicy} style={styles.btn()}>
                          🔄 Regenerate
                        </button>
                      </>
                    )}
                    {policyStatus === 'review' && (
                      <>
                        <button onClick={handleApprovePolicy} style={styles.btn('success')}>
                          ✅ Approve
                        </button>
                        <button onClick={() => setPolicyStatus('draft')} style={styles.btn()}>
                          ↩️ Send Back to Draft
                        </button>
                      </>
                    )}
                    {policyStatus === 'approved' && (
                      <div style={{
                        padding: '12px 16px', background: '#ECFDF5', borderRadius: '8px',
                        color: '#065F46', fontSize: '13px', fontWeight: 600,
                      }}>
                        ✅ Policy Approved — Ready for Audit
                      </div>
                    )}
                    <button
                      onClick={() => {
                        const content = editedPolicyContent || policyContent;
                        // Convert markdown to basic HTML for Word
                        const htmlBody = content
                          .replace(/^### (.*$)/gm, '<h3>$1</h3>')
                          .replace(/^## (.*$)/gm, '<h2>$1</h2>')
                          .replace(/^# (.*$)/gm, '<h1>$1</h1>')
                          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                          .replace(/\*(.*?)\*/g, '<em>$1</em>')
                          .replace(/\n/g, '<br/>');

                        const fullHtml = `
                          <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">
                          <head><meta charset="utf-8"><style>
                            body { font-family: Calibri, sans-serif; font-size: 11pt; line-height: 1.6; padding: 20px; }
                            h1 { font-size: 18pt; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; padding-bottom: 4px; }
                            h2 { font-size: 14pt; color: #2E74B5; margin-top: 16px; }
                            h3 { font-size: 12pt; color: #333; }
                            table { border-collapse: collapse; width: 100%; margin: 12px 0; }
                            td, th { border: 1px solid #ccc; padding: 6px 10px; font-size: 10pt; }
                            th { background: #F2F2F2; font-weight: bold; }
                          </style></head>
                          <body>${htmlBody}</body></html>`;

                        const blob = new Blob([fullHtml], { type: 'application/msword' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `${cid}_Policy.doc`;
                        a.click();
                        URL.revokeObjectURL(url);
                      }}
                      style={styles.btn()}
                    >
                      ⬇️ Download Word
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancedControlDetail;
