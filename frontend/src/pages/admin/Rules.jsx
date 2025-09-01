import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  AppBar,
  Toolbar,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Switch,
  FormControlLabel,
} from '@mui/material';
import api from '../../api';

const Rules = () => {
  const [thresholds, setThresholds] = useState([]);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingThreshold, setEditingThreshold] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [thresholdsRes, rulesRes] = await Promise.all([
        api.get('/api/admin/thresholds/'),
        api.get('/api/admin/rules/')
      ]);
      setThresholds(thresholdsRes.data);
      setRules(rulesRes.data);
    } catch (error) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateThreshold = async () => {
    try {
      await api.patch(`/api/admin/thresholds/${editingThreshold.id}/`, {
        value: editingThreshold.value,
        description: editingThreshold.description
      });
      setOpenDialog(false);
      setEditingThreshold(null);
      fetchData();
    } catch (error) {
      setError('Failed to update threshold');
    }
  };

  const handleToggleRule = async (ruleId, enabled) => {
    try {
      await api.patch(`/api/admin/rules/${ruleId}/`, { enabled });
      fetchData();
    } catch (error) {
      setError('Failed to update rule');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Admin - Rules & Thresholds
          </Typography>
          <Button color="inherit" onClick={() => navigate('/admin/clients')}>
            Clients
          </Button>
          <Button color="inherit" onClick={() => navigate('/admin/transactions')}>
            Transactions
          </Button>
          <Button color="inherit" onClick={() => navigate('/admin/fraud-alerts')}>
            Fraud Alerts
          </Button>
          <Button color="inherit" onClick={() => navigate('/dashboard')}>
            Dashboard
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Thresholds Section */}
        <Typography variant="h4" sx={{ mb: 3 }}>Fraud Detection Thresholds</Typography>
        <TableContainer component={Paper} sx={{ mb: 4 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Key</TableCell>
                <TableCell>Value</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {thresholds.map((threshold) => (
                <TableRow key={threshold.id}>
                  <TableCell>{threshold.key}</TableCell>
                  <TableCell>{threshold.value}</TableCell>
                  <TableCell>{threshold.description}</TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => {
                        setEditingThreshold(threshold);
                        setOpenDialog(true);
                      }}
                    >
                      Edit
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Rules Section */}
        <Typography variant="h4" sx={{ mb: 3 }}>Fraud Detection Rules</Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Rule</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rules.map((rule) => (
                <TableRow key={rule.id}>
                  <TableCell>{rule.key}</TableCell>
                  <TableCell>{rule.description}</TableCell>
                  <TableCell>
                    {rule.enabled ? 'Enabled' : 'Disabled'}
                  </TableCell>
                  <TableCell>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={rule.enabled}
                          onChange={(e) => handleToggleRule(rule.id, e.target.checked)}
                        />
                      }
                      label=""
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Edit Threshold Dialog */}
        <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
          <DialogTitle>Edit Threshold</DialogTitle>
          <DialogContent>
            {editingThreshold && (
              <Box sx={{ pt: 1 }}>
                <TextField
                  fullWidth
                  label="Value"
                  type="number"
                  value={editingThreshold.value}
                  onChange={(e) => setEditingThreshold({
                    ...editingThreshold,
                    value: parseFloat(e.target.value)
                  })}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Description"
                  value={editingThreshold.description}
                  onChange={(e) => setEditingThreshold({
                    ...editingThreshold,
                    description: e.target.value
                  })}
                />
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button onClick={handleUpdateThreshold} variant="contained">
              Update
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
};

export default Rules;
