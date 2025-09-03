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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import api from '../../api';

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      let url = '/api/admin/transactions/';
      const params = new URLSearchParams();
      if (statusFilter) params.append('status', statusFilter);
      if (typeFilter) params.append('transaction_type', typeFilter);
      if (params.toString()) url += '?' + params.toString();
      
      const response = await api.get(url);
      setTransactions(response.data);
    } catch (error) {
      setError('Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success.main';
      case 'pending': return 'warning.main';
      case 'failed': return 'error.main';
      default: return 'text.primary';
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
            Admin - Transaction Management
          </Typography>
          <Button color="inherit" onClick={() => navigate('/admin/clients')}>
            Clients
          </Button>
          <Button color="inherit" onClick={() => navigate('/admin/fraud-alerts')}>
            Fraud Alerts
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
          <Typography variant="h4">All Transactions</Typography>
          <Button variant="outlined" onClick={fetchTransactions}>
            Refresh
          </Button>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              label="Status"
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={typeFilter}
              label="Type"
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="transfer">Transfer</MenuItem>
              <MenuItem value="withdraw">Withdraw</MenuItem>
              <MenuItem value="deposit">Deposit</MenuItem>
            </Select>
          </FormControl>

          <Button variant="contained" onClick={fetchTransactions}>
            Apply Filters
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Client</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>From Account</TableCell>
                <TableCell>To Account</TableCell>
                <TableCell>Created</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {transactions.map((transaction) => (
                <TableRow key={transaction.id}>
                  <TableCell>{transaction.client_name}</TableCell>
                  <TableCell>{transaction.transaction_type}</TableCell>
                  <TableCell>
                    {new Intl.NumberFormat('ar-DZ', {
                      style: 'currency',
                      currency: 'DZD',
                      minimumFractionDigits: 2
                    }).format(transaction.amount)}
                  </TableCell>
                  <TableCell>
                    <Typography color={getStatusColor(transaction.status)}>
                      {transaction.status}
                    </Typography>
                  </TableCell>
                  <TableCell>{transaction.from_account}</TableCell>
                  <TableCell>{transaction.to_account_number}</TableCell>
                  <TableCell>{new Date(transaction.created_at).toLocaleDateString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Container>
    </Box>
  );
};

export default Transactions;
