import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { getAlerts, getLogs } from '../services/api';

export default function Dashboard() {
    const [alerts, setAlerts] = useState([]);
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        setLoading(true);
        try {
            const [alertsRes, logsRes] = await Promise.all([
                getAlerts(),
                getLogs()
            ]);
            setAlerts(alertsRes.data);
            setLogs(logsRes.data);
        } catch (err) {
            toast.error('Failed to load dashboard data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div className="grid md:grid-cols-2 gap-6">
            <div>
                <h2 className="text-xl font-bold mb-4">Recent Alerts</h2>
                <div className="space-y-4">
                    {alerts.map(alert => (
                        <div key={alert.id} className="p-4 bg-white rounded shadow">
                            <div className="font-bold">{alert.type}</div>
                            <div className="text-gray-600">{alert.message}</div>
                            <div className="text-sm text-gray-500">{alert.timestamp}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div>
                <h2 className="text-xl font-bold mb-4">Activity Logs</h2>
                <div className="space-y-4">
                    {logs.map(log => (
                        <div key={log.id} className="p-4 bg-white rounded shadow">
                            <div>{log.action}</div>
                            <div className="text-sm text-gray-500">{log.timestamp}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
