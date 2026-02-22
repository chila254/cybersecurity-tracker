'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle, Wifi, Users, Globe, Shield, Activity } from 'lucide-react';

interface NetworkStats {
  total_devices: number;
  online_devices: number;
  total_dns_queries: number;
  blocked_queries: number;
  top_domains: Array<{ domain: string; count: number; category: string }>;
  top_categories: Array<{ category: string; count: number }>;
  device_types: Record<string, number>;
}

interface ConnectedDevice {
  id: string;
  mac_address: string;
  ip_address: string;
  device_name: string;
  device_type: string;
  user_name: string;
  is_online: boolean;
  connected_at: string;
  signal_strength?: number;
}

export default function NetworkMonitoringPage() {
  const [stats, setStats] = useState<NetworkStats | null>(null);
  const [devices, setDevices] = useState<ConnectedDevice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  useEffect(() => {
    fetchNetworkData();
  }, []);

  const fetchNetworkData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsRes, devicesRes] = await Promise.all([
        fetch(`${apiUrl}/network/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${apiUrl}/network/devices?limit=20`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      if (!statsRes.ok || !devicesRes.ok) {
        throw new Error('Failed to fetch network data');
      }

      setStats(await statsRes.json());
      setDevices(await devicesRes.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    try {
      setSyncing(true);
      const res = await fetch(`${apiUrl}/network/wifi-config/sync`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!res.ok) throw new Error('Sync failed');

      await fetchNetworkData();
      alert('Devices synced successfully');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Sync failed');
    } finally {
      setSyncing(false);
    }
  };

  if (loading) return <div className="p-8 text-center">Loading network data...</div>;

  return (
    <div className="space-y-8 p-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h1 className="flex items-center gap-2 text-3xl font-bold">
            <Wifi className="h-8 w-8" />
            Network Monitoring
          </h1>
          <p className="text-gray-600">Monitor WiFi devices and website access</p>
        </div>
        <div className="space-x-2">
          <Button onClick={() => (window.location.href = '/network/settings')} variant="outline">
            ⚙️ Settings
          </Button>
          <Button onClick={handleSync} disabled={syncing}>
            {syncing ? 'Syncing...' : '🔄 Sync Now'}
          </Button>
        </div>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="flex items-center gap-3 pt-6">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Key Stats */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm font-medium">
                <Users className="h-4 w-4" /> Total Devices
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_devices}</div>
              <p className="text-xs text-gray-500">{stats.online_devices} online</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm font-medium">
                <Globe className="h-4 w-4" /> DNS Queries
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_dns_queries}</div>
              <p className="text-xs text-gray-500">Sites visited</p>
            </CardContent>
          </Card>

          <Card className="bg-red-50">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm font-medium text-red-800">
                <Shield className="h-4 w-4" /> Blocked
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.blocked_queries}</div>
              <p className="text-xs text-gray-500">Dangerous sites</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm font-medium">
                <Activity className="h-4 w-4" /> Top Category
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.top_categories[0]?.category || 'N/A'}
              </div>
              <p className="text-xs text-gray-500">
                {stats.top_categories[0]?.count || 0} queries
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Connected Devices */}
      <Card>
        <CardHeader>
          <CardTitle>Connected Devices ({devices.length})</CardTitle>
          <CardDescription>Currently connected WiFi devices</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {devices.length === 0 ? (
              <p className="py-8 text-center text-gray-500">No devices found. Click "Sync Now" to scan your network.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr className="text-left">
                      <th className="pb-2 font-semibold">Device Name</th>
                      <th className="pb-2 font-semibold">MAC Address</th>
                      <th className="pb-2 font-semibold">IP Address</th>
                      <th className="pb-2 font-semibold">Type</th>
                      <th className="pb-2 font-semibold">Status</th>
                      <th className="pb-2 font-semibold">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {devices.map(device => (
                      <tr key={device.id} className="border-b hover:bg-gray-50">
                        <td className="py-3">{device.device_name || 'Unknown'}</td>
                        <td className="py-3 font-mono text-xs">{device.mac_address}</td>
                        <td className="py-3 font-mono text-xs">{device.ip_address}</td>
                        <td className="py-3 capitalize">{device.device_type}</td>
                        <td className="py-3">
                          <span
                            className={`inline-block rounded px-2 py-1 text-xs font-semibold ${
                              device.is_online
                                ? 'bg-green-100 text-green-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {device.is_online ? 'Online' : 'Offline'}
                          </span>
                        </td>
                        <td className="py-3">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => (window.location.href = `/network/device/${device.id}`)}
                          >
                            View History
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Top Domains */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Top Visited Domains</CardTitle>
            <CardDescription>Most frequently accessed websites</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {stats.top_domains.length === 0 ? (
                <p className="py-4 text-center text-gray-500">No DNS data available</p>
              ) : (
                <div className="space-y-3">
                  {stats.top_domains.slice(0, 10).map((domain, idx) => (
                    <div key={idx} className="flex items-center justify-between border-b pb-2 last:border-0">
                      <div className="flex-1">
                        <div className="font-mono text-sm">{domain.domain}</div>
                        <span className="inline-block rounded bg-blue-100 px-2 py-1 text-xs text-blue-800">
                          {domain.category}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{domain.count}</div>
                        <p className="text-xs text-gray-500">queries</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
