'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle, ArrowLeft, Globe, Check, X } from 'lucide-react';

interface Device {
  id: string;
  device_name: string;
  mac_address: string;
  ip_address: string;
  device_type: string;
  user_name: string;
  manufacturer: string;
  connected_at: string;
  data_sent_bytes: string;
  data_received_bytes: string;
  is_online: boolean;
}

interface DNSLog {
  id: string;
  domain: string;
  domain_category: string;
  is_blocked: boolean;
  timestamp: string;
}

export default function DeviceHistoryPage() {
  const params = useParams();
  const router = useRouter();
  const deviceId = params.id as string;

  const [device, setDevice] = useState<Device | null>(null);
  const [logs, setLogs] = useState<DNSLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  useEffect(() => {
    fetchDeviceData();
  }, []);

  const fetchDeviceData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [deviceRes, logsRes] = await Promise.all([
        fetch(`${apiUrl}/network/devices/${deviceId}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${apiUrl}/network/devices/${deviceId}/dns-history?limit=200`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      if (!deviceRes.ok || !logsRes.ok) {
        throw new Error('Failed to fetch device data');
      }

      setDevice(await deviceRes.json());
      setLogs(await logsRes.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8 text-center">Loading device data...</div>;

  const filteredLogs = selectedCategory
    ? logs.filter(log => log.domain_category === selectedCategory)
    : logs;

  const blockedCount = logs.filter(l => l.is_blocked).length;
  const categories = [...new Set(logs.map(l => l.domain_category))].sort();

  return (
    <div className="space-y-8 p-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.back()}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold">{device?.device_name || 'Unknown Device'}</h1>
          <p className="text-gray-600">
            {device?.device_type} • {device?.mac_address}
          </p>
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

      {/* Device Info */}
      {device && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Device Type</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-lg font-semibold capitalize">{device.device_type}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">IP Address</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="font-mono text-lg">{device.ip_address}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Status</CardTitle>
            </CardHeader>
            <CardContent>
              <span
                className={`inline-block rounded px-2 py-1 font-semibold ${
                  device.is_online
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {device.is_online ? '🟢 Online' : '🔴 Offline'}
              </span>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Connected Since</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">
                {new Date(device.connected_at).toLocaleDateString()}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Site Access History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Site Visit History ({filteredLogs.length})
          </CardTitle>
          <CardDescription>All websites accessed by this device</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Category Filter */}
          {categories.length > 0 && (
            <div className="flex flex-wrap gap-2">
              <Button
                variant={selectedCategory === '' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory('')}
              >
                All ({logs.length})
              </Button>
              {categories.map(cat => (
                <Button
                  key={cat}
                  variant={selectedCategory === cat ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(cat)}
                >
                  {cat} ({logs.filter(l => l.domain_category === cat).length})
                </Button>
              ))}
            </div>
          )}

          {/* DNS Logs Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b bg-gray-50">
                <tr className="text-left">
                  <th className="px-4 py-3 font-semibold">Domain</th>
                  <th className="px-4 py-3 font-semibold">Category</th>
                  <th className="px-4 py-3 font-semibold">Status</th>
                  <th className="px-4 py-3 font-semibold">Time</th>
                </tr>
              </thead>
              <tbody>
                {filteredLogs.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="py-8 text-center text-gray-500">
                      No DNS logs found
                    </td>
                  </tr>
                ) : (
                  filteredLogs.map(log => (
                    <tr key={log.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-3 font-mono text-xs">{log.domain}</td>
                      <td className="px-4 py-3">
                        <span className="inline-block rounded bg-blue-100 px-2 py-1 text-xs text-blue-800">
                          {log.domain_category}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {log.is_blocked ? (
                          <span className="flex items-center gap-1 text-red-600">
                            <X className="h-4 w-4" /> Blocked
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-green-600">
                            <Check className="h-4 w-4" /> Allowed
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-500">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Stats */}
          <div className="flex gap-4 border-t pt-4">
            <div>
              <p className="text-sm text-gray-600">Total Queries</p>
              <p className="text-2xl font-bold">{logs.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Blocked</p>
              <p className="text-2xl font-bold text-red-600">{blockedCount}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Allowed</p>
              <p className="text-2xl font-bold text-green-600">
                {logs.length - blockedCount}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
