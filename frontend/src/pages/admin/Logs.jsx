import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Loader2, Search, RefreshCw, Info, AlertTriangle, XCircle, CheckCircle } from 'lucide-react';
import api from '../../api';

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({});
  const [systemInfo, setSystemInfo] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Filter states
  const [selectedLogType, setSelectedLogType] = useState('system');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [entriesPerPage, setEntriesPerPage] = useState(50);
  
  // Pagination
  const [totalPages, setTotalPages] = useState(1);
  const [totalEntries, setTotalEntries] = useState(0);

  const logTypes = [
    { value: 'auth', label: 'Authentication', color: 'bg-blue-100 text-blue-800' },
    { value: 'ai', label: 'AI/ML', color: 'bg-purple-100 text-purple-800' },
    { value: 'rules', label: 'Rules Engine', color: 'bg-green-100 text-green-800' },
    { value: 'transactions', label: 'Transactions', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'system', label: 'System', color: 'bg-gray-100 text-gray-800' },
    { value: 'errors', label: 'Errors', color: 'bg-red-100 text-red-800' }
  ];

  const logLevels = [
    { value: '', label: 'All Levels' },
    { value: 'INFO', label: 'Info', color: 'bg-blue-100 text-blue-800' },
    { value: 'WARNING', label: 'Warning', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'ERROR', label: 'Error', color: 'bg-red-100 text-red-800' },
    { value: 'CRITICAL', label: 'Critical', color: 'bg-red-200 text-red-900' }
  ];

  const fetchLogs = async () => {
    setLoading(true);
    setError('');
    
    try {
      const params = new URLSearchParams({
        log_type: selectedLogType,
        page: currentPage,
        limit: entriesPerPage
      });
      
      if (selectedLevel) params.append('level', selectedLevel);
      if (searchTerm) params.append('search', searchTerm);
      
      const response = await api.get(`/api/system/logs/?${params}`);
      setLogs(response.data.entries);
      setTotalPages(response.data.total_pages);
      setTotalEntries(response.data.total_entries);
    } catch (err) {
      setError('Failed to fetch logs: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/system/logs/stats/');
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch log stats:', err);
    }
  };

  const fetchSystemInfo = async () => {
    try {
      const response = await api.get('/api/system/info/');
      setSystemInfo(response.data);
    } catch (err) {
      console.error('Failed to fetch system info:', err);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [selectedLogType, selectedLevel, currentPage, entriesPerPage]);

  useEffect(() => {
    fetchStats();
    fetchSystemInfo();
  }, []);

  const handleSearch = () => {
    setCurrentPage(1);
    fetchLogs();
  };

  const handleRefresh = () => {
    fetchLogs();
    fetchStats();
    fetchSystemInfo();
  };

  const getLevelIcon = (level) => {
    switch (level) {
      case 'INFO':
        return <Info className="w-4 h-4 text-blue-600" />;
      case 'WARNING':
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case 'ERROR':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'CRITICAL':
        return <XCircle className="w-4 h-4 text-red-800" />;
      default:
        return <Info className="w-4 h-4 text-gray-600" />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTimestamp = (timestamp) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">System Logs & Monitoring</h1>
        <Button onClick={handleRefresh} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="logs" className="space-y-4">
        <TabsList>
          <TabsTrigger value="logs">Logs</TabsTrigger>
          <TabsTrigger value="stats">Statistics</TabsTrigger>
          <TabsTrigger value="system">System Info</TabsTrigger>
        </TabsList>

        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Log Viewer</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Filters */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Log Type</label>
                  <Select value={selectedLogType} onValueChange={setSelectedLogType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {logTypes.map(type => (
                        <SelectItem key={type.value} value={type.value}>
                          <Badge className={type.color}>{type.label}</Badge>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Log Level</label>
                  <Select value={selectedLevel} onValueChange={setSelectedLevel}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {logLevels.map(level => (
                        <SelectItem key={level.value} value={level.value}>
                          {level.value ? (
                            <Badge className={level.color}>{level.label}</Badge>
                          ) : (
                            level.label
                          )}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Search</label>
                  <div className="flex space-x-2">
                    <Input
                      placeholder="Search in messages..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    />
                    <Button onClick={handleSearch} size="sm">
                      <Search className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Entries per page</label>
                  <Select value={entriesPerPage.toString()} onValueChange={(value) => setEntriesPerPage(parseInt(value))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="25">25</SelectItem>
                      <SelectItem value="50">50</SelectItem>
                      <SelectItem value="100">100</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Log Entries */}
              <div className="border rounded-lg">
                {loading ? (
                  <div className="p-8 text-center">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
                    <p>Loading logs...</p>
                  </div>
                ) : logs.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    No logs found for the selected criteria
                  </div>
                ) : (
                  <div className="max-h-96 overflow-y-auto">
                    {logs.map((log, index) => (
                      <div
                        key={index}
                        className="border-b p-4 hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              {getLevelIcon(log.level)}
                              <Badge variant={log.level === 'ERROR' || log.level === 'CRITICAL' ? 'destructive' : 'secondary'}>
                                {log.level}
                              </Badge>
                              <span className="text-sm text-gray-500">{log.name}</span>
                              <span className="text-sm text-gray-400">{formatTimestamp(log.timestamp)}</span>
                            </div>
                            <p className="text-sm font-mono bg-gray-100 p-2 rounded">
                              {log.message}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    Showing {((currentPage - 1) * entriesPerPage) + 1} to {Math.min(currentPage * entriesPerPage, totalEntries)} of {totalEntries} entries
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(currentPage - 1)}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </Button>
                    <span className="px-3 py-2 text-sm">
                      Page {currentPage} of {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(currentPage + 1)}
                      disabled={currentPage === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stats" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Log Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {logTypes.map(type => {
                  const stat = stats[type.value];
                  return (
                    <div key={type.value} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Badge className={type.color}>{type.label}</Badge>
                        {stat?.exists ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-600" />
                        )}
                      </div>
                      {stat?.exists ? (
                        <div className="space-y-1 text-sm">
                          <p>Size: {formatFileSize(stat.size_bytes)}</p>
                          <p>Lines: {stat.line_count.toLocaleString()}</p>
                          <p>Modified: {formatTimestamp(stat.last_modified * 1000)}</p>
                        </div>
                      ) : (
                        <p className="text-gray-500 text-sm">File not found</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Information</CardTitle>
            </CardHeader>
            <CardContent>
              {Object.keys(systemInfo).length === 0 ? (
                <div className="text-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
                  <p>Loading system information...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Database</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Engine:</span> {systemInfo.database?.engine}</p>
                      <p><span className="font-medium">Name:</span> {systemInfo.database?.name}</p>
                      <p><span className="font-medium">Status:</span> 
                        <Badge variant={systemInfo.database?.status === 'connected' ? 'default' : 'destructive'} className="ml-2">
                          {systemInfo.database?.status}
                        </Badge>
                      </p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Email</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Backend:</span> {systemInfo.email?.backend}</p>
                      <p><span className="font-medium">Host:</span> {systemInfo.email?.host}:{systemInfo.email?.port}</p>
                      <p><span className="font-medium">TLS:</span> {systemInfo.email?.tls ? 'Yes' : 'No'}</p>
                      <p><span className="font-medium">SSL:</span> {systemInfo.email?.ssl ? 'Yes' : 'No'}</p>
                      <p><span className="font-medium">Configured:</span> 
                        <Badge variant={systemInfo.email?.user_configured && systemInfo.email?.password_configured ? 'default' : 'destructive'} className="ml-2">
                          {systemInfo.email?.user_configured && systemInfo.email?.password_configured ? 'Yes' : 'No'}
                        </Badge>
                      </p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Logging</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Root Level:</span> {systemInfo.logging?.log_level_root}</p>
                      <p><span className="font-medium">Console Level:</span> {systemInfo.logging?.log_level_console}</p>
                      <p><span className="font-medium">Directory:</span> {systemInfo.logging?.logs_directory}</p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">General</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Debug Mode:</span> 
                        <Badge variant={systemInfo.debug_mode ? 'destructive' : 'default'} className="ml-2">
                          {systemInfo.debug_mode ? 'Enabled' : 'Disabled'}
                        </Badge>
                      </p>
                      <p><span className="font-medium">Allowed Hosts:</span> {systemInfo.allowed_hosts?.join(', ')}</p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Logs;
