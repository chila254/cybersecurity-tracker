'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle, Settings, Check } from 'lucide-react';

interface WiFiConfig {
  router_type: string;
  router_url: string;
  router_username: string;
  dns_log_source: string;
  is_enabled: boolean;
}

interface NetworkPolicy {
  id: string;
  name: string;
  description: string;
  block_categories: string[];
  is_active: boolean;
}

const ROUTER_TYPES = [
  { value: 'unifi', label: 'Ubiquiti UniFi' },
  { value: 'meraki', label: 'Cisco Meraki' },
  { value: 'tp_link', label: 'TP-Link' },
  { value: 'mikrotik', label: 'Mikrotik RouterOS' }
];

const DOMAIN_CATEGORIES = [
  { value: 'social', label: '🔵 Social Media' },
  { value: 'streaming', label: '🎬 Video Streaming' },
  { value: 'adult', label: '⛔ Adult Content' },
  { value: 'gambling', label: '🎰 Gambling' },
  { value: 'malware', label: '🚨 Malware/Phishing' }
];

export default function NetworkSettingsPage() {
  const [config, setConfig] = useState<WiFiConfig | null>(null);
  const [policies, setPolicies] = useState<NetworkPolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showConfigForm, setShowConfigForm] = useState(false);

  const [formData, setFormData] = useState({
    router_type: 'unifi',
    router_url: '',
    router_username: '',
    router_password: '',
    dns_log_source: '',
    dns_log_url: '',
    dns_api_key: ''
  });

  const [policyForm, setPolicyForm] = useState({
    name: '',
    description: '',
    block_categories: [] as string[]
  });

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${apiUrl}/network/wifi-config`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        setConfig(await res.json());
      }

      const policiesRes = await fetch(`${apiUrl}/network/policies`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (policiesRes.ok) {
        setPolicies(await policiesRes.json());
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfig = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const res = await fetch(`${apiUrl}/network/wifi-config`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (!res.ok) throw new Error('Failed to save configuration');

      alert('WiFi configuration saved successfully');
      setShowConfigForm(false);
      fetchSettings();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save');
    }
  };

  const handleCreatePolicy = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const res = await fetch(`${apiUrl}/network/policies`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(policyForm)
      });

      if (!res.ok) throw new Error('Failed to create policy');

      alert('Policy created successfully');
      setPolicyForm({ name: '', description: '', block_categories: [] });
      fetchSettings();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create policy');
    }
  };

  if (loading) return <div className="p-8 text-center">Loading settings...</div>;

  return (
    <div className="space-y-8 p-8">
      {/* Header */}
      <div>
        <h1 className="flex items-center gap-2 text-3xl font-bold">
          <Settings className="h-8 w-8" />
          Network Settings
        </h1>
        <p className="text-gray-600">Configure WiFi router and network policies</p>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="flex items-center gap-3 pt-6">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <p className="text-red-800">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* WiFi Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>WiFi Router Configuration</CardTitle>
          <CardDescription>Connect your WiFi router to track connected devices</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {config ? (
            <div className="space-y-3 rounded bg-green-50 p-4">
              <div className="flex items-center gap-2 text-green-800">
                <Check className="h-5 w-5" />
                <span className="font-semibold">Router Connected</span>
              </div>
              <div className="space-y-2 text-sm">
                <p>
                  <span className="font-semibold">Type:</span> {config.router_type}
                </p>
                <p>
                  <span className="font-semibold">URL:</span> {config.router_url}
                </p>
                {config.dns_log_source && (
                  <p>
                    <span className="font-semibold">DNS Source:</span> {config.dns_log_source}
                  </p>
                )}
              </div>
              <Button variant="outline" size="sm" onClick={() => setShowConfigForm(true)}>
                Edit Configuration
              </Button>
            </div>
          ) : (
            <Button onClick={() => setShowConfigForm(true)}>Add WiFi Configuration</Button>
          )}

          {showConfigForm && (
            <form onSubmit={handleSaveConfig} className="space-y-4 border-t pt-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium">Router Type *</label>
                  <select
                    value={formData.router_type}
                    onChange={e => setFormData({ ...formData, router_type: e.target.value })}
                    className="mt-1 block w-full rounded border px-3 py-2"
                    required
                  >
                    {ROUTER_TYPES.map(rt => (
                      <option key={rt.value} value={rt.value}>
                        {rt.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium">Router URL *</label>
                  <input
                    type="text"
                    placeholder="https://192.168.1.1"
                    value={formData.router_url}
                    onChange={e => setFormData({ ...formData, router_url: e.target.value })}
                    className="mt-1 block w-full rounded border px-3 py-2"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium">Username *</label>
                  <input
                    type="text"
                    value={formData.router_username}
                    onChange={e => setFormData({ ...formData, router_username: e.target.value })}
                    className="mt-1 block w-full rounded border px-3 py-2"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium">Password *</label>
                  <input
                    type="password"
                    value={formData.router_password}
                    onChange={e => setFormData({ ...formData, router_password: e.target.value })}
                    className="mt-1 block w-full rounded border px-3 py-2"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium">DNS Log Source</label>
                  <select
                    value={formData.dns_log_source}
                    onChange={e => setFormData({ ...formData, dns_log_source: e.target.value })}
                    className="mt-1 block w-full rounded border px-3 py-2"
                  >
                    <option value="">None</option>
                    <option value="cloudflare">Cloudflare</option>
                    <option value="quad9">Quad9</option>
                    <option value="local">Local Router</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-2">
                <Button type="submit">Save Configuration</Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowConfigForm(false)}
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>

      {/* Network Policies */}
      <Card>
        <CardHeader>
          <CardTitle>Network Policies</CardTitle>
          <CardDescription>Block categories of websites</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Policy List */}
          {policies.length > 0 && (
            <div className="space-y-2">
              {policies.map(policy => (
                <div
                  key={policy.id}
                  className={`rounded border p-3 ${
                    policy.is_active ? 'border-blue-200 bg-blue-50' : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">{policy.name}</p>
                      <p className="text-sm text-gray-600">{policy.description}</p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {policy.block_categories.map(cat => (
                          <span key={cat} className="inline-block rounded bg-red-100 px-2 py-1 text-xs text-red-800">
                            ❌ {cat}
                          </span>
                        ))}
                      </div>
                    </div>
                    <span className={`rounded px-2 py-1 text-xs font-semibold ${
                      policy.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {policy.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Create New Policy */}
          <form onSubmit={handleCreatePolicy} className="space-y-4 border-t pt-4">
            <h3 className="font-semibold">Create New Policy</h3>

            <div>
              <label className="block text-sm font-medium">Policy Name *</label>
              <input
                type="text"
                placeholder="e.g., Block Adult Content"
                value={policyForm.name}
                onChange={e => setPolicyForm({ ...policyForm, name: e.target.value })}
                className="mt-1 block w-full rounded border px-3 py-2"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Description</label>
              <input
                type="text"
                placeholder="Policy description"
                value={policyForm.description}
                onChange={e => setPolicyForm({ ...policyForm, description: e.target.value })}
                className="mt-1 block w-full rounded border px-3 py-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Block Categories</label>
              <div className="mt-2 space-y-2">
                {DOMAIN_CATEGORIES.map(cat => (
                  <label key={cat.value} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={policyForm.block_categories.includes(cat.value)}
                      onChange={e => {
                        if (e.target.checked) {
                          setPolicyForm({
                            ...policyForm,
                            block_categories: [...policyForm.block_categories, cat.value]
                          });
                        } else {
                          setPolicyForm({
                            ...policyForm,
                            block_categories: policyForm.block_categories.filter(c => c !== cat.value)
                          });
                        }
                      }}
                    />
                    <span>{cat.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <Button type="submit" disabled={!policyForm.name || policyForm.block_categories.length === 0}>
              Create Policy
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Configuration Guide */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle>📖 Configuration Guide</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div>
            <h4 className="font-semibold">UniFi Setup</h4>
            <p>Enable SSH access and use the UniFi controller IP address</p>
          </div>
          <div>
            <h4 className="font-semibold">Meraki Setup</h4>
            <p>Generate an API key from your Meraki dashboard and use it as the password</p>
          </div>
          <div>
            <h4 className="font-semibold">Data Privacy Notice</h4>
            <p>⚠️ This feature requires employee consent. Ensure you have proper policies in place.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
