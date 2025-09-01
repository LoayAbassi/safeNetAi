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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import api from '../../api';

const FraudAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [levelFilter, setLevelFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      let url = '/api/admin/fraud-alerts/';
      const params = new URLSearchParams();
      if (levelFilter) params.append('level', levelFilter);
      if (statusFilter) params.append('status', statusFilter);
      if (params.toString()) url += '?' + params.toString();
      
      const response = await api.get(url);
      setAlerts(response.data);
    } catch (error) {
      setError('Failed to load fraud alerts');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (alertId) => {
    try {
      await api.patch(`/api/admin/fraud-alerts/${alertId}/approve/`);
      fetchAlerts();
    } catch (error) {
      setError('Failed to approve alert');
    }
  };

  const handleReject = async (alertId) => {
    try {
      await api.patch(`/api/admin/fraud-alerts/${alertId}/reject/`);
      fetchAlerts();
    } catch (error) {
      setError('Failed to reject alert');
    }
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'High': return 'error';
      case 'Medium': return 'warning';
      case 'Low': return 'info';
      default: return 'default';
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
            Admin - Fraud Alert Management
          </Typography>
          <Button color="inherit" onClick={() => navigate('/admin/clients')}>
            Clients
          </Button>
          <Button color="inherit" onClick={() => navigate('/admin/transactions')}>
            Transactions
          </Button>
          <Button color="inherit" onClick={() => navigate('/admin/rules')}>
            Rules
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

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Fraud Alerts</Typography>
          <Button variant="outlined" onClick={fetchAlerts}>
            Refresh
          </Button>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Level</InputLabel>
            <Select
              value={levelFilter}
              label="Level"
              onChange={(e) => setLevelFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="High">High</MenuItem>
              <MenuItem value="Medium">Medium</MenuItem>
              <MenuItem value="Low">Low</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              label="Status"
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="Pending">Pending</MenuItem>
              <MenuItem value="Reviewed">Reviewed</MenuItem>
            </Select>
          </FormControl>

          <Button variant="contained" onClick={fetchAlerts}>
            Apply Filters
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Transaction</TableCell>
                <TableCell>Risk Level</TableCell>
                <TableCell>Risk Score</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Message</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {alerts.map((alert) => (
                <TableRow key={alert.id}>
                  <TableCell>
                    {alert.transaction_details?.client_name} - ${alert.transaction_details?.amount}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={alert.level} 
                      color={getLevelColor(alert.level)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{alert.risk_score}</TableCell>
                  <TableCell>{alert.status}</TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                      {alert.message}
                    </Typography>
                  </TableCell>
                  <TableCell>{new Date(alert.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    {alert.status === 'Pending' && (
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          size="small"
                          variant="contained"
                          color="success"
                          onClick={() => handleApprove(alert.id)}
                        >
                          Approve
                        </Button>
                        <Button
                          size="small"
                          variant="contained"
                          color="error"
                          onClick={() => handleReject(alert.id)}
                        >
                          Reject
                        </Button>
                      </Box>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Container>
    </Box>
  );
};

export default FraudAlerts;
