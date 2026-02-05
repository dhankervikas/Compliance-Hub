import React, { useState, useEffect } from 'react';
import policyService from '../services/policyService';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Chip,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    CircularProgress
} from '@mui/material';
import ReactMarkdown from 'react-markdown';

const PolicyList = () => {
    const [policies, setPolicies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedPolicy, setSelectedPolicy] = useState(null);
    const [open, setOpen] = useState(false);

    useEffect(() => {
        fetchPolicies();
    }, []);

    const fetchPolicies = async () => {
        try {
            const data = await policyService.getPolicies();
            setPolicies(data);
        } catch (error) {
            console.error("Failed to fetch policies", error);
        } finally {
            setLoading(false);
        }
    };

    const handleViewPolicy = (policy) => {
        setSelectedPolicy(policy);
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
        setSelectedPolicy(null);
    };

    if (loading) return <Box display="flex" justifyContent="center" mt={4}><CircularProgress /></Box>;

    return (
        <Box p={3}>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', color: '#1a237e' }}>
                Compliance Policies
            </Typography>
            <Typography variant="body1" color="textSecondary" paragraph>
                Core security policies required for ISO 27001 and SOC 2 compliance.
            </Typography>

            <Grid container spacing={3}>
                {policies.map((policy) => (
                    <Grid item xs={12} md={6} lg={4} key={policy.id}>
                        <Card elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column', borderRadius: 2 }}>
                            <CardContent sx={{ flexGrow: 1 }}>
                                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                                    <Chip label={`v${policy.version}`} size="small" color="primary" variant="outlined" />
                                    <Typography variant="caption" color="textSecondary">
                                        Last Updated: {new Date(policy.updated_at || policy.created_at).toLocaleDateString()}
                                    </Typography>
                                </Box>
                                <Typography variant="h6" gutterBottom component="div" sx={{ fontWeight: 600 }}>
                                    {policy.name}
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                    {policy.description}
                                </Typography>
                            </CardContent>
                            <Box p={2} pt={0}>
                                <Button
                                    variant="contained"
                                    fullWidth
                                    onClick={() => handleViewPolicy(policy)}
                                    sx={{ textTransform: 'none' }}
                                >
                                    View Policy
                                </Button>
                            </Box>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            {/* Policy Viewer Dialog */}
            <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
                <DialogTitle sx={{ bgcolor: '#f5f5f5', borderBottom: '1px solid #e0e0e0' }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="h6">{selectedPolicy?.name}</Typography>
                        <Chip label={selectedPolicy?.version ? `v${selectedPolicy.version}` : ''} size="small" />
                    </Box>
                </DialogTitle>
                <DialogContent dividers>
                    <Box sx={{ '& h1': { fontSize: '1.5em', mb: 2 }, '& h2': { fontSize: '1.25em', mt: 2, mb: 1, color: '#1976d2' } }}>
                        <ReactMarkdown>
                            {selectedPolicy?.content || ''}
                        </ReactMarkdown>
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">Close</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default PolicyList;
